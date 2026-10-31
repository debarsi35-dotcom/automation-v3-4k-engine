"""pipeline/get_youtube_refresh_token.py — 1-Click Helper to Get Your YouTube Refresh Token."""
import json, os, sys

def main():
    secret_file = sys.argv[1] if len(sys.argv) > 1 else "client_secret.json"
    if not os.path.exists(secret_file):
        print(f"ERROR: Could not find '{secret_file}'. Download your OAuth Desktop JSON from Google Cloud Console and rename it to 'client_secret.json'.")
        sys.exit(1)
    from google_auth_oauthlib.flow import InstalledAppFlow
    flow = InstalledAppFlow.from_client_secrets_file(secret_file, ["https://www.googleapis.com/auth/youtube.upload"])
    creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")
    raw = json.load(open(secret_file, encoding="utf-8"))
    info = raw.get("installed") or raw.get("web") or {}
    print("\n" + "=" * 70)
    print("COPY THESE 3 SECRETS INTO GITHUB -> SETTINGS -> SECRETS -> ACTIONS:")
    print("=" * 70)
    print(f"YOUTUBE_CLIENT_ID     = {creds.client_id or info.get('client_id')}")
    print(f"YOUTUBE_CLIENT_SECRET = {creds.client_secret or info.get('client_secret')}")
    print(f"YOUTUBE_REFRESH_TOKEN = {creds.refresh_token}")
    print("=" * 70)

if __name__ == "__main__":
    main()
