

"""
seed_mock_data.py

Mock data generator for the Spliits schema (users, pools, pool_members),
scaled for 10k+ rows. Built to practice real Postgres transactions.

WHY THIS IS FAST AT SCALE
---------------------------------------
Two things kill performance at 10k+ rows if you do them naively:

1. bcrypt is DELIBERATELY slow (~200-300ms per hash by design, to resist
   brute force). Hashing 10,000 unique passwords one at a time would take
   ~30-50 minutes. Since these are throwaway mock accounts anyway, we hash
   ONE password once and reuse the same hash string for every user. If you
   specifically need distinct passwords per account, see the comment in
   `build_users()` — but expect it to be slow.

2. Inserting via `session.add(obj)` one row at a time (or even add_all with
   thousands of ORM objects) is slow because SQLAlchemy tracks each object
   individually. Instead, we build plain dicts and use Core-level bulk
   `insert()` executed in chunks — this compiles to executemany() under
   psycopg2, which is dramatically faster.

All primary keys (UUIDs) are generated client-side in Python BEFORE
insert, so we always know a user's user_id / a pool's pool_id up front —
no need to flush-and-reread IDs back from the DB between steps.

BEFORE RUNNING
---------------------------------------
1. pip install sqlalchemy psycopg2-binary bcrypt faker
2. Set DATABASE_URL below (or export it as an env var).
3. Fix the two imports marked "ADJUST THIS" to match where your
   `request_status`, `pool_role`, and `PoolCategory` enums actually live.
4. This imports your REAL models (User, pool, pool_members) so table/column
   names match production exactly.
"""
from dotenv import load_dotenv
load_dotenv()
import os
import random
import time
import uuid
from contextlib import contextmanager

import bcrypt
from faker import Faker
from sqlalchemy import create_engine, insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

# --------------------------------------------------------------------------
# CONFIG
# --------------------------------------------------------------------------

DATABASE_URL = os.getenv(
    "DATABASE_URL1"
)

NUM_USERS = 10_000
NUM_POOLS = 1_500
MEMBERS_PER_POOL = (2, 6)      # random range per pool, capped by pool.max_members
INSERT_CHUNK_SIZE = 2_000      # rows per executemany batch

engine = create_engine(DATABASE_URL, echo=False, future=True)
fake = Faker()

# --------------------------------------------------------------------------
# YOUR REAL MODELS — adjust these import paths to match your project layout
# --------------------------------------------------------------------------

from app.models.users import User
from app.models.pools import pool as Pool
from app.models.pool_members import pool_members as PoolMember

# ADJUST THIS: point these at wherever request_status / pool_role / PoolCategory
# actually live in your codebase (e.g. app.models.enums, app.schemas.pools)
try:
    from app.utils.enum import request_status, pool_role
except ImportError:
    from enum import Enum

    class request_status(str, Enum):
        REQUESTED = 'requested'
        ACCEPTED = 'accepted'
        REJECTED = 'rejected'

    class pool_role(str,Enum):
        HOST = 'host'
        MEMBER = 'member'
        


try:
    from app.utils.enum import PoolCategory
except ImportError:
    from enum import Enum

    class PoolCategory(str, Enum):
        ENTERTAINMENT = "Entertainment"
        MUSIC = "Music"
        AI_PRODUCTIVITY = "AI & Productivity"
        CLOUD_STORAGE = "Cloud Storage"
        DESIGN_CREATIVE = "Design & Creative"
        GAMING = "Gaming"
        EDUCATION = "Education & Learning"
        SOFTWARE_DEV = "Software & Developer Tools"
        NEWS = "News & Reading"
        FITNESS = "Fitness & Wellness"
        BUSINESS = "Business & Finance"
        SHOPPING = "Shopping & Memberships"
        OTHER = "Other"

POOL_CATEGORY_VALUES = [c.value for c in PoolCategory]

# --------------------------------------------------------------------------
# ONE bcrypt hash, reused for every mock account (see module docstring).
# Login for ALL mock users: password = "MockPassw0rd!"
# --------------------------------------------------------------------------

_SHARED_HASH = bcrypt.hashpw(b"MockPassw0rd!", bcrypt.gensalt()).decode("utf-8")


def hash_password_unique(plain: str) -> str:
    """
    Only use this if you truly need distinct hashes per account
    (e.g. testing per-user password rotation). At 10k rows this alone
    will take 30-50+ minutes because bcrypt is intentionally slow.
    """
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


# --------------------------------------------------------------------------
# BULK ROW BUILDERS — return plain dicts, not ORM objects, for speed
# --------------------------------------------------------------------------

def build_users(n: int) -> list[dict]:
    print(f"  Building {n} user rows...")
    rows = []
    for i in range(n):
        rows.append({
            "user_id": uuid.uuid4(),
            "name": fake.name(),
            # Manually constructed unique email instead of fake.unique.email() —
            # Faker's uniqueness tracking gets noticeably slower past a few
            # thousand calls because it checks every prior value.
            "email": f"mock.user.{i}.{uuid.uuid4().hex[:8]}@example.com",
            "password": _SHARED_HASH,
            "pfp": fake.image_url(),
        })
    return rows


def build_pools(n: int, user_rows: list[dict]) -> list[dict]:
    print(f"  Building {n} pool rows...")
    rows = []
    for _ in range(n):
        host = random.choice(user_rows)
        total_cost = round(random.uniform(200, 2000), 2)
        rows.append({
            "pool_id": uuid.uuid4(),
            "title": fake.catch_phrase(),
            "description": fake.sentence(nb_words=12),
            "total_cost": total_cost,
            "max_members": random.randint(2, 6),
            "category": random.choice(POOL_CATEGORY_VALUES),
            "host_id": host["user_id"],
            # cost_per_member is DB-computed — never set it here
        })
    return rows


def build_pool_members(pool_rows: list[dict], user_rows: list[dict]) -> list[dict]:
    print("  Building pool_members rows...")
    rows = []
    seen_pairs = set()  # guard against accidentally violating unq_pool_user ourselves
    for p in pool_rows:
        n = min(random.randint(*MEMBERS_PER_POOL), p["max_members"], len(user_rows) - 1)
        chosen = random.sample(user_rows, n + 1)  # +1 slack in case host is drawn
        chosen = [u for u in chosen if u["user_id"] != p["host_id"]][:n]
        for u in chosen:
            pair = (p["pool_id"], u["user_id"])
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            rows.append({
                "member_id": uuid.uuid4(),
                "pool_id": p["pool_id"],
                "user_id": u["user_id"],
                "host_id": p["host_id"],
                "status": request_status.ACCEPTED,
                "role": pool_role.MEMBER,
            })
    return rows


# --------------------------------------------------------------------------
# CHUNKED BULK INSERT
# --------------------------------------------------------------------------

def bulk_insert(session: Session, model, rows: list[dict], label: str):
    total = len(rows)
    if total == 0:
        return
    start = time.time()
    for i in range(0, total, INSERT_CHUNK_SIZE):
        chunk = rows[i:i + INSERT_CHUNK_SIZE]
        session.execute(insert(model), chunk)
        print(f"    {label}: {min(i + INSERT_CHUNK_SIZE, total)}/{total}")
    print(f"    {label} done in {time.time() - start:.1f}s")


@contextmanager
def transaction():
    session = Session(engine)
    try:
        yield session
        session.commit()
        print("  -> COMMITTED")
    except Exception as e:
        session.rollback()
        print(f"  -> ROLLED BACK ({type(e).__name__}: {e})")
        raise
    finally:
        session.close()


# --------------------------------------------------------------------------
# SCENARIO 1: happy-path bulk seed, one transaction
# --------------------------------------------------------------------------

def seed_happy_path():
    print(f"\n[1] Seeding {NUM_USERS} users, {NUM_POOLS} pools, memberships...")
    t0 = time.time()

    user_rows = build_users(NUM_USERS)
    pool_rows = build_pools(NUM_POOLS, user_rows)
    member_rows = build_pool_members(pool_rows, user_rows)

    with transaction() as session:
        bulk_insert(session, User, user_rows, "users")
        bulk_insert(session, Pool, pool_rows, "pools")
        bulk_insert(session, PoolMember, member_rows, "pool_members")

    print(f"Total: {len(user_rows)} users, {len(pool_rows)} pools, "
          f"{len(member_rows)} pool_members in {time.time() - t0:.1f}s")


# --------------------------------------------------------------------------
# SCENARIO 2: deliberate failure — duplicate email violates unique constraint,
# demonstrating that a bulk-insert failure rolls back the WHOLE chunk/transaction
# --------------------------------------------------------------------------

def seed_with_duplicate_email_failure():
    print("\n[2] Attempting a chunk with a duplicate email (expect rollback)...")
    with Session(engine) as session:
        existing = session.execute(select(User).limit(1)).scalar_one_or_none()
        if existing is None:
            print("    No existing users found — run scenario 1 first.")
            return
        existing_email = existing.email

    rows = build_users(50)
    rows[25]["email"] = existing_email  # force a UNIQUE violation mid-chunk

    try:
        with transaction() as session:
            bulk_insert(session, User, rows, "users (with 1 bad row)")
    except IntegrityError:
        print("    Confirmed: entire chunk rolled back, none of the 50 rows exist.")


# --------------------------------------------------------------------------
# SCENARIO 3: deliberate failure — duplicate pool_members (pool_id, user_id)
# --------------------------------------------------------------------------

def seed_with_duplicate_membership_failure():
    print("\n[3] Attempting duplicate (pool_id, user_id) membership (expect rollback)...")
    with Session(engine) as session:
        member = session.execute(select(PoolMember).limit(1)).scalar_one_or_none()
        if member is None:
            print("    No existing pool_members found — run scenario 1 first.")
            return
        pool_id, user_id, host_id = member.pool_id, member.user_id, member.host_id

    dup_row = {
        "member_id": uuid.uuid4(),
        "pool_id": pool_id,
        "user_id": user_id,  # same pair as an existing row -> violates unq_pool_user
        "host_id": host_id,
        "status": request_status.REQUESTED,
        "role": pool_role.MEMBER,
    }
    try:
        with transaction() as session:
            bulk_insert(session, PoolMember, [dup_row], "pool_members (dup)")
    except IntegrityError:
        print("    Confirmed: composite UNIQUE constraint enforced, rolled back.")


# --------------------------------------------------------------------------
# SCENARIO 4: SAVEPOINT / nested transaction demo (small scale, ORM-based
# since savepoints are about control flow, not bulk throughput)
# --------------------------------------------------------------------------

def seed_with_savepoint():
    print("\n[4] Demonstrating SAVEPOINT (nested transaction) recovery...")
    safe_row = build_users(1)[0]
    with Session(engine) as session:
        with session.begin():
            session.execute(insert(User), [safe_row])

            try:
                with session.begin_nested():  # SAVEPOINT
                    risky_row = build_users(1)[0]
                    risky_row["email"] = safe_row["email"]  # forces UNIQUE violation
                    session.execute(insert(User), [risky_row])
            except IntegrityError:
                print("    Savepoint rolled back the risky insert only.")

        print("  -> Outer transaction committed (safe_row persisted, risky_row did not).")


# --------------------------------------------------------------------------
# UTILITY: wipe mock data (only rows, not schema) for repeatable runs
# --------------------------------------------------------------------------

def reset_tables():
    confirm = input("Type 'yes' to TRUNCATE pool_members, pools, users: ")
    if confirm.strip().lower() != "yes":
        print("Aborted.")
        return
    with engine.begin() as conn:
        conn.exec_driver_sql(
            "TRUNCATE TABLE pool_members, pools, users RESTART IDENTITY CASCADE;"
        )
    print("Tables truncated.")


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

MENU = f"""
Spliits mock data / transaction practice
-----------------------------------------
Current scale: {NUM_USERS:,} users / {NUM_POOLS:,} pools

1) Seed happy-path data (bulk insert, chunked, one transaction)
2) Trigger duplicate-email failure (whole-chunk rollback)
3) Trigger duplicate-membership failure (composite unique constraint)
4) Savepoint / nested transaction demo
5) Reset (TRUNCATE) tables
0) Exit
"""

def main():
    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()
        try:
            if choice == "1":
                seed_happy_path()
            elif choice == "2":
                seed_with_duplicate_email_failure()
            elif choice == "3":
                seed_with_duplicate_membership_failure()
            elif choice == "4":
                seed_with_savepoint()
            elif choice == "5":
                reset_tables()
            elif choice == "0":
                break
            else:
                print("Invalid option.")
        except IntegrityError:
            pass  # already reported inside the scenario


if __name__ == "__main__":
    main()