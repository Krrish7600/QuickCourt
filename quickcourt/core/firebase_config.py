import firebase_admin
from firebase_admin import credentials, firestore, auth

# Path to the downloaded JSON key
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore, auth

# Option A (dev): load local JSON file named firebase_key.json placed in project root
LOCAL_KEY_PATH = os.path.join(os.path.dirname(__file__), '..', 'firebase_key.json')

if os.path.exists(LOCAL_KEY_PATH):
    cred = credentials.Certificate(os.path.abspath(LOCAL_KEY_PATH))
else:
    # Option B (production): read base64 or JSON from env var FIREBASE_SERVICE_ACCOUNT
    svc = os.environ.get('FIREBASE_SERVICE_ACCOUNT')
    if not svc:
        raise RuntimeError("No Firebase credentials found: set firebase_key.json or FIREBASE_SERVICE_ACCOUNT env var")
    try:
        # svc might be JSON string or base64-encoded JSON
        sa = json.loads(svc)
        cred = credentials.Certificate(sa)
    except Exception:
        import base64
        sa = json.loads(base64.b64decode(svc))
        cred = credentials.Certificate(sa)

# initialize app only once
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()
firebase_auth = auth
