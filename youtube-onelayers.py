import logging
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from functionOneLayer import playlist, analysis
from dotenv import load_dotenv
import asyncio

# Suppress all third-party logs
logging.getLogger().setLevel(logging.WARNING)

# Only show your application logs
logging.getLogger("functionOneLayer").setLevel(logging.INFO)
logging.basicConfig(
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def youtube_init():
    load_dotenv()

    SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
    CLIENT_SECRETS_FILE = "secrets-local.json"
    TOKEN_FILE = "token.json"

    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_console()
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
        
    return build('youtube', 'v3', credentials=creds)

def playlist_ids_init(youtube):
    playList = youtube.playlists().list(
        part = "snippet",
        mine = True,
        maxResults=20
    ).execute()

    playListContent = playList.get("items")
    playListTitleId = playlist.extract_title_to_id(playListContent)
    return list(playListTitleId.values())

async def main():
    youtube = youtube_init()
    playlist_ids = playlist_ids_init(youtube)
    
    all_vedios = await playlist.process_playlists(youtube, playlist_ids)
    
    #the profiel is in str format, you can change the setting in regularModel.py
    profile = analysis.generate_regular_profile(all_vedios)
    
    #this profiel is in UserProfile format, so you can easily interact with frontend
    #profile = analysis.generate_formatted_profile(all_vedios)
    
    with open('profile.txt', 'w', encoding='utf-8') as f:
        f.write((str(profile)))

if __name__ == "__main__":
    asyncio.run(main())