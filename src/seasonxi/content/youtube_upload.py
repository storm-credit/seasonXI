"""SeasonXI — YouTube Upload

Usage:
  uv run python -m seasonxi.content.youtube_upload --video outputs/messi_2011_12.mp4 --player messi --season 2011-12
  uv run python -m seasonxi.content.youtube_upload --video outputs/messi_2011_12.mp4 --title "MESSI 2011-12" --privacy unlisted
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[3] / ".env")

PROJECT_ROOT = Path(__file__).resolve().parents[3]
OBSIDIAN_VAULT = Path(r"C:\Users\Storm Credit\Desktop\쇼츠\seasonXI")
CLIENT_SECRETS = PROJECT_ROOT / "client_secrets.json"
TOKEN_FILE = PROJECT_ROOT / "token.json"

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def get_credentials():
    """Get OAuth2 credentials, refreshing or prompting as needed."""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CLIENT_SECRETS.exists():
                raise FileNotFoundError(
                    f"client_secrets.json not found at {CLIENT_SECRETS}\n"
                    "Download from Google Cloud Console → APIs & Services → Credentials"
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CLIENT_SECRETS), SCOPES,
                redirect_uri="urn:ietf:wg:oauth:2.0:oob",
            )
            auth_url, _ = flow.authorization_url(prompt="consent")
            print(f"\n  Open this URL in your browser:\n  {auth_url}\n")
            code = input("  Enter authorization code: ").strip()
            flow.fetch_token(code=code)
            creds = flow.credentials

        TOKEN_FILE.write_text(creds.to_json())

    return creds


def load_season_meta(player_id: str, season: str) -> dict:
    """Load metadata from Obsidian season document."""
    import yaml

    players_dir = OBSIDIAN_VAULT / "01_Players"
    for d in players_dir.iterdir():
        if d.is_dir() and d.name.lower() == player_id.lower():
            md_file = d / f"{season}.md"
            if md_file.exists():
                text = md_file.read_text(encoding="utf-8")
                fm_match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
                if fm_match:
                    return yaml.safe_load(fm_match.group(1))
    return {}


def build_upload_metadata(
    player_id: str | None = None,
    season: str | None = None,
    title: str | None = None,
    description: str | None = None,
    privacy: str = "unlisted",
) -> dict:
    """Build YouTube upload metadata from Obsidian data or manual input."""

    if player_id and season:
        meta = load_season_meta(player_id, season)
        display = meta.get("display_name", player_id.upper())
        season_label = meta.get("season_label", season)
        ovr = meta.get("ovr", "")
        tier = meta.get("tier", "")
        hook = meta.get("hook", "")
        commentary = meta.get("commentary", "")
        achievement = meta.get("achievement", "")
        club = meta.get("club", "")

        auto_title = f"{display} {season_label} | {ovr} OVR | {tier} SEASON | SeasonXI"
        auto_desc = (
            f"{hook}\n\n"
            f"{commentary}\n"
            f"{achievement}\n\n"
            f"{display} | {club} | {season_label}\n\n"
            f"#SeasonXI #football #shorts #{display.lower()} #{tier.lower()}"
        )
        auto_tags = [
            display.lower(),
            "seasonxi",
            "football",
            "shorts",
            tier.lower(),
            season,
            club.lower().replace(" ", ""),
        ]
    else:
        auto_title = title or "SeasonXI"
        auto_desc = description or ""
        auto_tags = ["seasonxi", "football", "shorts"]

    return {
        "snippet": {
            "title": title or auto_title,
            "description": description or auto_desc,
            "tags": auto_tags,
            "categoryId": "17",  # Sports
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }


def upload_video(
    video_path: str,
    metadata: dict,
) -> dict:
    """Upload video to YouTube and return video ID + URL."""
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    creds = get_credentials()
    youtube = build("youtube", "v3", credentials=creds)

    media = MediaFileUpload(
        video_path,
        mimetype="video/mp4",
        resumable=True,
        chunksize=10 * 1024 * 1024,  # 10MB chunks
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=metadata,
        media_body=media,
    )

    print(f"  Uploading: {video_path}")
    print(f"  Title: {metadata['snippet']['title']}")
    print(f"  Privacy: {metadata['status']['privacyStatus']}")

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  Progress: {int(status.progress() * 100)}%")

    video_id = response["id"]
    url = f"https://youtube.com/shorts/{video_id}"
    print(f"  Done! URL: {url}")

    return {"video_id": video_id, "url": url}


def main():
    parser = argparse.ArgumentParser(description="SeasonXI YouTube Uploader")
    parser.add_argument("--video", required=True, help="Path to MP4 file")
    parser.add_argument("--player", help="Player ID (e.g., messi)")
    parser.add_argument("--season", help="Season (e.g., 2011-12)")
    parser.add_argument("--title", help="Custom title (overrides auto)")
    parser.add_argument("--description", help="Custom description")
    parser.add_argument("--privacy", default="unlisted", choices=["public", "unlisted", "private"])
    args = parser.parse_args()

    if not Path(args.video).exists():
        print(f"Error: {args.video} not found")
        return

    print(f"\n{'='*60}")
    print(f"  SeasonXI YouTube Uploader")
    print(f"{'='*60}\n")

    metadata = build_upload_metadata(
        player_id=args.player,
        season=args.season,
        title=args.title,
        description=args.description,
        privacy=args.privacy,
    )

    result = upload_video(args.video, metadata)
    print(f"\n  Video ID: {result['video_id']}")
    print(f"  URL: {result['url']}")


if __name__ == "__main__":
    main()
