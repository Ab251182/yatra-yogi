import streamlit as st
import requests

# Load API keys from Streamlit secrets
YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]

st.title("🌍 Yatra Yogi – Top 10 Travel Videos")
query = st.text_input("Enter a destination (e.g., Bali, Ladakh)")

def fetch_top_videos(destination):
    # Step 1: Search recent videos about the destination
    search_url = "https://www.googleapis.com/youtube/v3/search"
    search_params = {
        "part": "snippet",
        "q": f"{destination} travel",
        "key": YOUTUBE_API_KEY,
        "maxResults": 15,
        "type": "video",
        "order": "date"
    }
    search_response = requests.get(search_url, params=search_params).json()
    video_items = search_response.get("items", [])
    video_ids = [item["id"]["videoId"] for item in video_items]

    # Step 2: Get statistics to sort by view count
    stats_url = "https://www.googleapis.com/youtube/v3/videos"
    stats_params = {
        "part": "snippet,statistics",
        "id": ",".join(video_ids),
        "key": YOUTUBE_API_KEY
    }
    stats_response = requests.get(stats_url, params=stats_params).json()
    sorted_videos = sorted(
        stats_response.get("items", []),
        key=lambda x: int(x["statistics"].get("viewCount", 0)),
        reverse=True
    )[:10]

    # Step 3: Format output
    videos = []
    for video in sorted_videos:
        video_id = video["id"]
        title = video["snippet"]["title"]
        description = video["snippet"]["description"]
        thumbnail = video["snippet"]["thumbnails"]["high"]["url"]
        views = video["statistics"]["viewCount"]
        url = f"https://www.youtube.com/watch?v={video_id}"
        videos.append({
            "title": title,
            "description": description,
            "thumbnail": thumbnail,
            "views": views,
            "url": url
        })
    return videos

# Render on UI
if query:
    with st.spinner("🔎 Fetching top travel videos..."):
        videos = fetch_top_videos(query)
        for v in videos:
            st.image(v["thumbnail"], width=350)
            st.markdown(f"### [{v['title']}]({v['url']})")
            st.write(f"📈 Views: {int(v['views']):,}")
            st.write("📝 " + v["description"][:300] + "...")
            st.markdown("---")
