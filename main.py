import json
from typing import Optional

import jwt
import requests
from fastapi import FastAPI, Header, HTTPException, Request

from auth0 import Auth0ManagementClient

with open("config.json") as f:
    config = json.load(f)

app = FastAPI()
clients = config["clients"]
auth0_conf = config["auth0"]
auth0_client = Auth0ManagementClient(**auth0_conf)

AUTH0_DOMAIN = auth0_conf["domain"]
JWKS_URL = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
JWKS = requests.get(JWKS_URL).json()["keys"]


def get_kid_header(token):
    headers = jwt.get_unverified_header(token)
    return headers["kid"]


def get_public_key(token):
    kid = get_kid_header(token)
    for key in JWKS:
        if key["kid"] == kid:
            return jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
    raise Exception("Public key not found.")


def validate_token(token: str):
    try:
        public_key = get_public_key(token)
        decoded = jwt.decode(
            token, public_key, algorithms=["RS256"], audience=auth0_conf["audience"]
        )
        return decoded
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token.")


@app.get("/users")
def get_users(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Authorization")

    token = authorization.split(" ")[1]
    claims = validate_token(token)

    client_id = claims["azp"]
    if client_id not in clients:
        raise HTTPException(status_code=403, detail="Unauthorized client")

    org_id = clients[client_id]
    users = auth0_client.get_users_by_org(org_id)
    return users
