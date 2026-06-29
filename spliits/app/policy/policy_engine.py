from typing import Callable
from dataclasses import dataclass
from ..security.OAuth2 import get_current_user
from fastapi import Depends,HTTPException
from ..log import log_decision,get_resource_id


@dataclass

class Rule:
    scope: str
    check: Callable[[object,object],bool]

class PolicyEngine:
    def __init__(self):
        self._rules: dict[tuple[str,str], Rule] = {}

    def register(self, resource_type: str, action: str, rule: Rule):
        self._rules[(resource_type, action)] = rule

    def check(self,db, action: str, resource_type: str, actor, Resource=None):
        rule = self._rules.get((resource_type, action))
        resource_id = get_resource_id(resource_type, Resource)
        if rule is None:
            decision,reason = False, "no_policy_defined"
        elif rule.scope not in actor.scopes:
            decision,reason = False, f"missing_scope:{rule.scope}"
        elif rule is not None and not rule.check(actor, Resource):
            decision,reason = False, "ownership_check_failed"
        else:
            decision,reason = True, "allowed"
        
        if db is not None:
            log_decision(db, actor, action, resource_type, resource_id, "allowed" if decision else "denied", reason, jti=getattr(actor, "jti", None))

        return decision, reason
    

def require_scope(scope: str):#scope only
    def checker(current_user = Depends(get_current_user)):
        if scope not in current_user.scopes:
            raise HTTPException(status_code=403, detail="Insufficient scope")
        current_user
    checker
