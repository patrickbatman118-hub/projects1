from jose import jwt
token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4ZjA2ZTEzZC1mZDFmLTQ0MmQtYjZmOC03YmVkN2JjMTg4ZDQiLCJzY29wZXMiOlsidXNlciJdLCJleHAiOjE3ODIxNjk5NTQsInR5cGUiOiJhY2Nlc3MiLCJqdGkiOiJjMTRkN2RkOS05OWI0LTQwOTYtYTUwNC1jMWFjNjc3MjljODEiLCJpYXQiOjE3ODIxNjY2NTR9.tzXDdQiYdJlXnRJLfCcCCVgDcc-ByK9ZfUHBsVV3pmU'

payload = (jwt.decode(token, 'giganiga', algorithms=['HS256']))
class CurrentUser:
    def __init__(self, payload: dict):
        self.user_id = payload["sub"]
        self.scopes = payload["scopes"]
        self.jti = payload["jti"]

    def has_scope(self, scope: str):
        return scope in self.scopes
    
user = CurrentUser(payload)

print(user.scopes)