"""
Spliits ETL DAG
---------------
Same logic as pipeline.py — extract, transform, load.
Now Airflow owns scheduling, retries, and observability.

Schedule: daily at midnight
"""

import logging
from datetime import datetime, timedelta

import pandas as pd
from sqlalchemy import create_engine, text
import os

from airflow import DAG
from airflow.operators.python import PythonOperator

logger = logging.getLogger(__name__)


default_args = {
    "owner": "nithin",
    "retries": 2,                           # retry failed task twice
    "retry_delay": timedelta(minutes=5),    # wait 5 min between retries
    "email_on_failure": False,             
}


# ── Helpers ───────────────────────────────────────────────────────────────────
def get_source_engine():
    url = os.environ["SOURCE_DB_URL"]
    return create_engine(url)

def get_warehouse_engine():
    url = os.environ["WAREHOUSE_DB_URL"]
    return create_engine(url)

def extract(**context):
    """Extract from OLTP, push dataframes to XCom."""
    ti = context["ti"]
    engine = get_source_engine()

    with engine.connect() as conn:
        users   = pd.read_sql(text("SELECT user_id::text, name, email, is_admin, disabled, created_at FROM users"), conn)
        pools   = pd.read_sql(text("SELECT pool_id::text, title, category, total_cost, max_members, cost_per_member, host_id::text, is_active, created_at FROM pools"), conn)
        members = pd.read_sql(text("SELECT member_id::text, pool_id::text, user_id::text, host_id::text, status, role, joined_at FROM pool_members"), conn)

    logger.info(f"Extracted: {len(users)} users, {len(pools)} pools, {len(members)} members")

    # XCom stores data between tasks — for dataframes, use JSON
    # In production with large data, you'd write to S3/GCS instead
    ti.xcom_push(key="users",   value=users.to_json())
    ti.xcom_push(key="pools",   value=pools.to_json())
    ti.xcom_push(key="members", value=members.to_json())


def transform(**context):
    """Pull from XCom, transform, push results back."""
    ti = context["ti"]

    users   = pd.read_json(ti.xcom_pull(key="users",   task_ids="extract"))
    pools   = pd.read_json(ti.xcom_pull(key="pools",   task_ids="extract"))
    members = pd.read_json(ti.xcom_pull(key="members", task_ids="extract"))

    now = pd.Timestamp.now(tz="UTC")

    # Users
    users["created_at"]      = pd.to_datetime(users["created_at"], utc=True)
    users["account_age_days"] = (now - users["created_at"]).dt.days
    users = users.dropna(subset=["user_id", "email"])

    # Pools
    pools["created_at"]    = pd.to_datetime(pools["created_at"], utc=True)
    pools["pool_age_days"] = (now - pools["created_at"]).dt.days
    pools = pools.dropna(subset=["pool_id"])

    # Members
    members["joined_at"]         = pd.to_datetime(members["joined_at"], utc=True)
    members["days_since_joined"] = (now - members["joined_at"]).dt.days
    members["is_accepted"]       = members["status"] == "accepted"
    members["is_host"]           = members["role"] == "host"
    members = members.dropna(subset=["member_id", "pool_id", "user_id"])

    # Pool summary — aggregated
    accepted      = members[members["is_accepted"]]
    member_counts = accepted.groupby("pool_id").size().reset_index(name="total_members")
    summary       = pools.merge(member_counts, on="pool_id", how="left")
    summary["total_members"] = summary["total_members"].fillna(0).astype(int)
    summary["fill_rate"]     = (summary["total_members"] / summary["max_members"]).round(4)
    summary["is_full"]       = summary["fill_rate"] >= 1.0
    summary = summary[[
        "pool_id", "title", "category", "total_cost", "max_members",
        "cost_per_member", "is_active", "total_members", "fill_rate",
        "is_full", "pool_age_days", "created_at"
    ]]

    logger.info(f"Transformed: {len(users)} users, {len(pools)} pools, {len(members)} members, {len(summary)} summary rows")

    ti.xcom_push(key="users",   value=users.to_json())
    ti.xcom_push(key="pools",   value=pools.to_json())
    ti.xcom_push(key="members", value=members.to_json())
    ti.xcom_push(key="summary", value=summary.to_json())


def load(**context):
    """Pull transformed data from XCom, upsert into warehouse."""
    ti      = context["ti"]
    engine  = get_warehouse_engine()
    SCHEMA  = "warehouse"

    users   = pd.read_json(ti.xcom_pull(key="users",   task_ids="transform"))
    pools   = pd.read_json(ti.xcom_pull(key="pools",   task_ids="transform"))
    members = pd.read_json(ti.xcom_pull(key="members", task_ids="transform"))
    summary = pd.read_json(ti.xcom_pull(key="summary", task_ids="transform"))

    def upsert(df, table, pk):
        temp = f"_temp_{table}"
        with engine.connect() as conn:
            df.to_sql(temp, conn, schema=SCHEMA, if_exists="replace", index=False)
            cols    = ", ".join(df.columns)
            updates = ", ".join(f"{c} = EXCLUDED.{c}" for c in df.columns if c != pk)
            conn.execute(text(f"""
                INSERT INTO {SCHEMA}.{table} ({cols})
                SELECT {cols} FROM {SCHEMA}.{temp}
                ON CONFLICT ({pk}) DO UPDATE SET {updates};
                DROP TABLE IF EXISTS {SCHEMA}.{temp};
            """))
            conn.commit()
        logger.info(f"Upserted {len(df)} rows into {SCHEMA}.{table}")

    upsert(users,   "dim_users",        "user_id")
    upsert(pools,   "dim_pools",        "pool_id")
    upsert(members, "fact_memberships", "member_id")

    with engine.connect() as conn:
        conn.execute(text(f"TRUNCATE TABLE {SCHEMA}.fact_pool_summary"))
        conn.commit()

    summary.to_sql("fact_pool_summary", engine, schema=SCHEMA, if_exists="append", index=False)
    logger.info(f"Rebuilt fact_pool_summary with {len(summary)} rows")

with DAG(
    dag_id="spliits_etl",
    default_args=default_args,
    description="Extract from spliits OLTP, load into warehouse schema",
    schedule="44 18 * * *",          
    start_date=datetime(2024, 1, 1),
    catchup=False,                  
    tags=["etl", "spliits"],
) as dag:

    extract_task = PythonOperator(
        task_id="extract",
        python_callable=extract,
    )

    transform_task = PythonOperator(
        task_id="transform",
        python_callable=transform,
    )

    load_task = PythonOperator(
        task_id="load",
        python_callable=load,
    )

    extract_task >> transform_task >> load_task