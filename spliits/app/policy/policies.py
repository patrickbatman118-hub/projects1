from .policy_engine import PolicyEngine, Rule

policy_engine = PolicyEngine()

policy_engine.register("pool", "update", Rule(
    scope="user",
    check=lambda actor, pool: actor.user_id == pool.host_id
))

policy_engine.register('notifications', 'read', Rule(
    scope='user',
    check= lambda actor, notifications: actor.user_id == notifications.receiver_id
))