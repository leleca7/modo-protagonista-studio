from __future__ import annotations
from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def youtube_credentials_ready(client_secret: Path) -> bool:
    return client_secret.exists() and client_secret.is_file()

def upload_video(video_path: Path, title: str, description: str, client_secret: Path, token_path: Path,
                 privacy: str = "private", tags: list[str] | None = None) -> str:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    if not video_path.exists():
        raise FileNotFoundError("video_final.mp4 não encontrado.")
    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not client_secret.exists():
                raise FileNotFoundError("client_secret.json não encontrado. Baixe as credenciais OAuth do Google Cloud e coloque na pasta do programa.")
            flow = InstalledAppFlow.from_client_secrets_file(str(client_secret), SCOPES)
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json(), encoding="utf-8")

    youtube = build("youtube", "v3", credentials=creds)
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title[:100],
                "description": description[:5000],
                "categoryId": "22",
                "tags": (tags or [])[:30],
            },
            "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False},
        },
        media_body=MediaFileUpload(str(video_path), chunksize=8 * 1024 * 1024, resumable=True),
    )
    response = None
    while response is None:
        _, response = request.next_chunk()
    return response["id"]
