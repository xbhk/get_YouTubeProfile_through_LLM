import logging
from typing import List, Any, Dict, Tuple
import asyncio

logger = logging.getLogger(__name__)

def extract_title_to_id(playlists):
    """
    Extracts the title and id of each playlist from the playlist data and generates a dictionary of title to id.

    Parameters:
    playlists (list): A list containing playlist dictionaries.

    Returns:
    dict: A dictionary with title as the key and id as the value.
    """
    title_to_id = {}
    for playlist in playlists:
        if 'snippet' in playlist and 'title' in playlist['snippet'] and 'id' in playlist:
            title = playlist['snippet']['title']
            pid = playlist['id']
            title_to_id[title] = pid
    return title_to_id

async def fetch_playlist_data_async(
    youtube: Any, 
    playlist_id: str, 
    semaphore: asyncio.Semaphore,
    retries: int = 3, 
    delay: int = 3
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Async version of fetch_playlist_data with rate limiting
    """
    async with semaphore:
        for attempt in range(retries):
            try:
                logger.info(f"Fetching playlist {playlist_id}, attempt {attempt + 1}")
                response = youtube.playlistItems().list(
                    part="snippet",
                    maxResults=20,
                    playlistId=playlist_id
                ).execute()
                
                videos = []
                for item in response.get('items', []):
                    snippet = item.get('snippet', {})
                    video = {
                        'video_id': snippet.get('resourceId', {}).get('videoId', ''),
                        'title': snippet.get('title', ''),
                        'description': snippet.get('description', '')[:250],
                        'published_at': snippet.get('publishedAt', ''),
                        'thumbnail_url': snippet.get('thumbnails', {}).get('default', {}).get('url', ''),
                        'position': snippet.get('position', 0),
                        'playlist_id': playlist_id
                    }
                    videos.append(video)
                    
                logger.info(f"Successfully fetched {len(videos)} videos for playlist: {playlist_id}")
                await asyncio.sleep(1)  # Rate limiting delay
                return playlist_id, videos
                
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed for playlist {playlist_id}: {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(delay * (attempt + 1))
        return playlist_id, []

async def process_playlists(
    youtube: Any,
    playlist_ids: List[str],
    max_concurrent: int = 3
) -> str:
    """
    Process playlists using async and return formatted string
    """
    logger.info(f"Starting playlist processing")
    
    semaphore = asyncio.Semaphore(max_concurrent)
    result_string = ""
    
    try:
        # Create tasks for video data
        video_tasks = [
            fetch_playlist_data_async(youtube, playlist_id, semaphore)
            for playlist_id in playlist_ids
        ]
        
        # Gather all results
        results = await asyncio.gather(*video_tasks, return_exceptions=True)
        
        # Process results and prepare formatted string
        for playlist_id, videos in results:
            if not isinstance(videos, list):  # Skip if there was an error
                continue
            
            result_string += f"Playlist {playlist_id}:\nvedios:\n\n"
            
            for video in videos:
                result_string += f"title:{video['title']}\ndescription:{video['description'][:250]}\n\n"
        
    except Exception as e:
        logger.error(f"Error in async playlist processing: {e}")
        raise
    
    logger.info(f"Completed processing all playlists")
    return result_string
