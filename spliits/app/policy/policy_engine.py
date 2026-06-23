from typing import Callable
from dataclasses import dataclass
from ..security.OAuth2 import get_current_user
from fastapi import Depends,HTTPException
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
    

def require_scope(scope: str):#scope only
    def checker(current_user = Depends(get_current_user)):
        if scope not in current_user.scopes:
            raise HTTPException(status_code=403, detail="Insufficient scope")
        return current_user
    return checker
