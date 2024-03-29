from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from starlette.responses import JSONResponse

from app.config.database import firebase_admin_auth, pyrebase_auth, test_pyrebase_auth

router = APIRouter()

# HTTPBearerAuth
security = HTTPBearer()


# Verify token and return user email
def firebase_email_authentication(
    token: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    user = firebase_admin_auth.verify_id_token(token.credentials)
    return user["email"]


# Verify token and return user uid
def firebase_uid_authentication(
    token: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    user = firebase_admin_auth.verify_id_token(token.credentials)
    return user["uid"]


# Reset password endpoint
@router.post("/reset-password", status_code=200)
def reset_password(email: str, test_db: bool = False):
    if test_db is True:
        p_auth = test_pyrebase_auth
    else:
        p_auth = pyrebase_auth
    try:
        p_auth.send_password_reset_email(email)
        return JSONResponse(
            status_code=200, content={"message": "Email sent to " + email}
        )
    except:
        # In order to avoid hack attempts, we don't return any error message
        # if the email doesn't exist that way we don't give any information to the attacker
        raise HTTPException(status_code=401, detail="Error sending email")


class Token(BaseModel):
    token: str
