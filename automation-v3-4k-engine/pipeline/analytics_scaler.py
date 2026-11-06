"""pipeline/analytics_scaler.py — Dynamic View-Based YouTube Scaling Engine.

Scaling Rules:
  - Tier 1: Until any video receives over 20,000 views within 24 hours -> 1 video daily.
  - Tier 2: After reaching 20,000+ views on any video within 24 hours -> 3 videos daily.
  - Tier 3: Once reaching 100,000+ views on any video within 24 hours -> 5 shorts daily.

Usage:
  python pipeline/analytics_scaler.py [--mock-views N] [--force-quota 1|3|5]
"""
import os, sys, json, datetime, argparse
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
HISTORY_PATH = ROOT_DIR / "archive/published_history.json"


def get_youtube_service():
    client_id = os.environ.get("YOUTUBE_CLIENT_ID", "").strip()
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET", "").strip()
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN", "").strip()
    if not (client_id and client_secret and refresh_token):
        return None
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        creds = Credentials(
            None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=["https://www.googleapis.com/auth/youtube.readonly", "https://www.googleapis.com/auth/youtube.upload"]
        )
        creds.refresh(Request())
        return build("youtube", "v3", credentials=creds)
    except Exception as e:
        print(f"[Analytics Scaler] Warning: Failed to initialize YouTube API client: {e}")
        return None


def determine_quota_from_views(max_views: int) -> tuple[int, str]:
    if max_views >= 100_000:
        return 5, "TIER_3_VIRAL_EXPLOSION (>=100k views in 24h -> 5 shorts daily)"
    elif max_views >= 20_000:
        return 3, "TIER_2_MOMENTUM_SCALE (>=20k views in 24h -> 3 videos daily)"
    else:
        return 1, "TIER_1_STANDARD (<20k views in 24h -> 1 video daily)"


def get_daily_upload_quota(force_quota: int = None, mock_views: int = None) -> dict:
    if force_quota in (1, 3, 5):
        _, desc = determine_quota_from_views(100_000 if force_quota == 5 else 25_000 if force_quota == 3 else 0)
        return {
            "quota": force_quota,
            "max_24h_views": mock_views or (100_000 if force_quota == 5 else 25_000 if force_quota == 3 else 0),
            "tier_description": f"MANUAL_OVERRIDE -> {desc}",
            "evaluated_videos": [],
            "source": "manual_override"
        }

    if mock_views is not None:
        quota, desc = determine_quota_from_views(mock_views)
        return {
            "quota": quota,
            "max_24h_views": mock_views,
            "tier_description": f"MOCKED -> {desc}",
            "evaluated_videos": [{"id": "mock_video_01", "views": mock_views, "title": "Mock Video"}],
            "source": "mock_test"
        }

    youtube = get_youtube_service()
    if not youtube:
        print("[Analytics Scaler] No live YouTube credentials detected. Defaulting to Tier 1 (1 video daily).")
        quota, desc = determine_quota_from_views(0)
        return {
            "quota": 1,
            "max_24h_views": 0,
            "tier_description": f"DEFAULT_OFFLINE -> {desc}",
            "evaluated_videos": [],
            "source": "offline_default"
        }

    # Query recent video IDs from published_history.json or YouTube API
    recent_video_ids = []
    if HISTORY_PATH.exists():
        try:
            history = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
            now = datetime.datetime.now(datetime.timezone.utc)
            for item in reversed(history):
                pub_time_str = item.get("published_at") or item.get("timestamp")
                if pub_time_str:
                    try:
                        pub_time = datetime.datetime.fromisoformat(pub_time_str.replace("Z", "+00:00"))
                        if (now - pub_time).total_seconds() <= 86400 * 2:  # published within last 48 hours
                            vid = item.get("youtube_video_id") or item.get("video_id")
                            if vid and vid not in recent_video_ids:
                                recent_video_ids.append(vid)
                    except Exception:
                        pass
        except Exception as e:
            print(f"[Analytics Scaler] Warning reading history: {e}")

    # Fallback to querying channel's uploads playlist if history is empty
    if not recent_video_ids:
        try:
            channels_resp = youtube.channels().list(mine=True, part="contentDetails").execute()
            uploads_list_id = channels_resp["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
            playlist_items = youtube.playlistItems().list(
                playlistId=uploads_list_id,
                part="snippet,contentDetails",
                maxResults=10
            ).execute()
            for itm in playlist_items.get("items", []):
                vid = itm["contentDetails"]["videoId"]
                recent_video_ids.append(vid)
        except Exception as e:
            print(f"[Analytics Scaler] Channel uploads lookup warning: {e}")

    evaluated = []
    max_views = 0

    if recent_video_ids:
        try:
            videos_resp = youtube.videos().list(
                id=",".join(recent_video_ids[:20]),
                part="snippet,statistics"
            ).execute()
            now = datetime.datetime.now(datetime.timezone.utc)
            for v in videos_resp.get("items", []):
                published_at_str = v["snippet"]["publishedAt"]
                pub_dt = datetime.datetime.fromisoformat(published_at_str.replace("Z", "+00:00"))
                age_hours = (now - pub_dt).total_seconds() / 3600.0
                stats = v.get("statistics", {})
                views = int(stats.get("viewCount", 0))
                title = v["snippet"]["title"]

                # If within 24 hours (or up to 30 hours grace period for 24h analytics check)
                if age_hours <= 30:
                    evaluated.append({
                        "id": v["id"],
                        "title": title,
                        "views": views,
                        "age_hours": round(age_hours, 1)
                    })
                    if views > max_views:
                        max_views = views
        except Exception as e:
            print(f"[Analytics Scaler] Video statistics lookup error: {e}")

    quota, desc = determine_quota_from_views(max_views)
    return {
        "quota": quota,
        "max_24h_views": max_views,
        "tier_description": desc,
        "evaluated_videos": evaluated,
        "source": "live_youtube_api"
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube Analytics Dynamic Quota Scaler")
    parser.add_argument("--mock-views", type=int, help="Mock maximum 24h view count for testing")
    parser.add_argument("--force-quota", type=int, choices=[1, 3, 5], help="Force daily quota to 1, 3, or 5")
    args = parser.parse_args()

    result = get_daily_upload_quota(force_quota=args.force_quota, mock_views=args.mock_views)
    print(json.dumps(result, indent=2))
