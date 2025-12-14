
import os
import pickle
import httplib2
import certifi
from googleapiclient.discovery import build
from google_auth_httplib2 import AuthorizedHttp
from google.oauth2.credentials import Credentials

# Mock credentials or load real ones
token_path = "token_gmail.pickle" 
# Use calendar token if gmail not found, looking for any valid creds
if not os.path.exists(token_path):
    token_path = "token.pickle" # Calendar token usually

if os.path.exists(token_path):
    print(f"Loading credentials from {token_path}...")
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
else:
    print("No token found. Cannot test authenticated build.")
    # Create dummy creds just to test build() instantiation logic (will fail on request but pass build)
    # properly we need Real creds to avoid 'default credentials' error if it tries to refresh.
    creds = None
    exit(1)

print("Attempting to build service with custom http...")

try:
    # Pattern 1: Passing http and credentials to build()
    print("\nTest 1: build(..., credentials=creds, http=http_obj)")
    http = httplib2.Http(ca_certs=certifi.where())
    service = build('calendar', 'v3', credentials=creds, http=http)
    print("✅ Build success!")
    # Test a simple call?
    # service.events().list(calendarId='primary').execute()
except Exception as e:
    print(f"❌ Test 1 Failed: {e}")

try:
    # Pattern 2: My previous attempt (AuthorizedHttp passed as requestBuilder?)
    print("\nTest 2: AuthorizedHttp -> build(requestBuilder=...)")
    http2 = httplib2.Http(ca_certs=certifi.where())
    authed_http = AuthorizedHttp(creds, http=http2)
    # Note: requestBuilder is for 'google-auth' requests-style transport in some contexts, 
    # but build() for discovery usually wants 'http' for httplib2.
    service2 = build('calendar', 'v3', requestBuilder=authed_http)
    print("✅ Build success (Test 2)!")
except Exception as e:
    print(f"❌ Test 2 Failed: {e}")

try:
    # Pattern 3: AuthorizedHttp passed as http? (The Fix)
    print("\nTest 3: AuthorizedHttp -> build(http=...)")
    from google_auth_httplib2 import AuthorizedHttp
    http3 = httplib2.Http(ca_certs=certifi.where())
    authed_http3 = AuthorizedHttp(creds, http=http3)
    service3 = build('calendar', 'v3', http=authed_http3)
    print("✅ Build success (Test 3)!")
except Exception as e:
    print(f"❌ Test 3 Failed: {e}")
