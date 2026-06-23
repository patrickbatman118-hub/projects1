from .policy_engine import PolicyEngine, Rule

policy_engine = PolicyEngine()

policy_engine.register("pool", "update", Rule(
    scope="user",
    check=lambda actor, pool: actor.user_id == pool.host_id
))

policy_engine.register('users', 'read', Rule(
    scope='admin',
    check= lambda actor, user: actor.user_id == user.receiver_id
))