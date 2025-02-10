import os

import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()


class AuthHandler:
    def __init__(self):
        # In production, this would be securely stored and unique per container
        self.secret_key = os.getenv("JWT_SECRET_KEY")
        self.container_id = os.getenv("CONTAINER_ID")

    def decode_token(self, token: str):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            if payload["container_id"] != self.container_id:
                raise HTTPException(status_code=401, detail="Invalid container access")
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_token(auth.credentials)
