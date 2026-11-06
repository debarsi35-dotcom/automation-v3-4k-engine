"""pipeline/youtube_uploader.py — Automated YouTube Data API v3 Publisher + Custom Thumbnail Setter + Rclone Backup."""
import os, subprocess

def upload_to_youtube(mp4_path: str, thumbnail_path: str, script_data: dict, privacy_status: str = "public") -> dict:
    client_id = os.environ.get("YOUTUBE_CLIENT_ID", "").strip()
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET", "").strip()
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN", "").strip()
    if not (client_id and client_secret and refresh_token):
        print("[YouTube Uploader] YOUTUBE_CLIENT_ID / SECRET / REFRESH_TOKEN not set; skipping live upload.")
        return {"status": "skipped_no_credentials", "video_id": None}
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    creds = Credentials(None, refresh_token=refresh_token, token_uri="https://oauth2.googleapis.com/token", client_id=client_id, client_secret=client_secret, scopes=["https://www.googleapis.com/auth/youtube.upload"])
    creds.refresh(Request())
    youtube = build("youtube", "v3", credentials=creds)
    chapters_str = "\n".join(f"{c.get('time', '0:00')} {c.get('title', 'Chapter')}" for c in script_data.get("chapters", []))
    refs_str = "\n".join(f"• {r}" for r in script_data.get("scientific_references", []))
    description = f"{script_data.get('youtube_description', script_data.get('title', ''))}\n\n⏱️ CHAPTERS:\n{chapters_str}\n\n🧬 SCIENTIFIC NOTES:\n{refs_str}\n\n#WhatIf #TEDEd #ScienceAnimation"
    body = {"snippet": {"title": script_data.get("title", "What If?")[:95], "description": description[:4900], "tags": script_data.get("youtube_tags", ["what if", "ted ed", "science animation"])[:25], "categoryId": "27", "defaultLanguage": "en", "defaultAudioLanguage": "en"}, "status": {"privacyStatus": privacy_status, "selfDeclaredMadeForKids": False}}
    media = MediaFileUpload(mp4_path, chunksize=10 * 1024 * 1024, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        _, response = request.next_chunk()
    video_id = response["id"]
    if thumbnail_path and os.path.exists(thumbnail_path):
        try:
            youtube.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(thumbnail_path, mimetype="image/png")).execute()
        except Exception as e:
            print(f"[YouTube Uploader] Thumbnail warning: {e}")
    return {"status": "uploaded", "video_id": video_id, "url": f"https://youtu.be/{video_id}"}

def backup_with_rclone(project_dir: str, mp4_path: str, slug: str):
    remote = os.environ.get("RCLONE_REMOTE", "").strip()
    if remote:
        subprocess.run(["rclone", "copy", os.path.dirname(mp4_path), f"{remote.rstrip('/')}/AutomationV2/{slug}/", "--transfers", "4"], check=False)
