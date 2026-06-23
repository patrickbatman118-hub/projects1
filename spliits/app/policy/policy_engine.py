from typing import Callable
from dataclasses import dataclass

@dataclass

class Rule:
    scope: str
    check: Callable[[object,object],bool]

class PolicyEngine:
    def __init__(self):
        self._rules: dict[tuple[str,str], Rule] = {}

    def register(self, resource_type: str, action: str, rule: Rule):
        self._rules[(resource_type, action)] = rule

    def check(self, action: str, resource_type: str, actor, Resource=None):
        print("AVAILABLE RULES:", self._rules)
        rule = self._rules.get((resource_type, action))
        if rule is None:
            return False, "no_policy_defined"
        if rule.scope not in actor.scopes:
            return False, f"missing_scope:{rule.scope}"
        if rule is not None and not rule.check(actor, Resource):
            return False, "ownership_check_failed"
        return True, "allowed"
