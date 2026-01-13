from fastapi import HTTPException, Header, Request
from jose import jwt, jwk, JWTError
import requests

SUPABASE_URL = "https://wkwmjqvxykrmftfboeib.supabase.co"
JWKS_URL = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"


def get_current_user(
    request: Request,
    authorization: str | None = Header(None)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    token = authorization.removeprefix("Bearer ").strip()

    try:
        # 1. Read JWT header
        header = jwt.get_unverified_header(token)
        kid = header["kid"]
        alg = header["alg"]  # <-- RS256 or ES256

        # 2. Fetch JWKS
        jwks = requests.get(JWKS_URL, timeout=5).json()

        # 3. Find matching key
        key_data = next(k for k in jwks["keys"] if k["kid"] == kid)

        # 4. Construct correct key type (RSA or EC)
        public_key = jwk.construct(key_data, algorithm=alg)

        # 5. Decode + verify
        payload = jwt.decode(
            token,
            public_key,
            algorithms=[alg],
            issuer=f"{SUPABASE_URL}/auth/v1",
            audience="authenticated",
        )

        request.state.user_id = payload["sub"]
        return payload["sub"]

    except StopIteration:
        raise HTTPException(status_code=401, detail="Signing key not found")

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")

    except JWTError as e:
        raise HTTPException(status_code=401, detail=str(e))
