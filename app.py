import streamlit as st
import requests
from datetime import datetime, timedelta
from transformers import pipeline

# ✅ Load Hugging Face token from secrets
HF_TOKEN = st.secrets["HF_TOKEN"]

# ✅ Hugging Face summarizer model
@st.cache_resource
def get_summarizer():
    return pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

summarizer = get_summarizer()

# ✅ YouTube API key from Streamlit secrets
YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]

# ✅ Streamlit UI
st.title("🌍 Yatra Yogi – Top 10 Travel Videos")
query = st.text_input("Enter a destination (e.g., Bali, Ladakh, Goa)")

# ✅ Filter videos uploaded in last 6 months and with min 2,000 views
def fetch_filtered_videos(query):
    search_url = "https://www.googleapis.com/youtube/v3/search"
    search_params = {
        "part": "snippet",
        "q": f"{query} travel",
        "key": YOUTUBE_API_KEY,
        "maxResults": 20,
        "type": "video",
        "order": "viewCount",
        "publishedAfter": (datetime.utcnow() - timedelta(days=180)).isoformat("T") + "Z"
    }

    search_res = requests.get(search_url, params=search_params).json()
    videos = []

    for item in search_res.get("items", []):
        video_id = item["id"]["videoId"]
        stats_url = "https://www.googleapis.com/youtube/v3/videos"
        stats_params = {
            "part": "statistics",
            "id": video_id,
            "key": YOUTUBE_API_KEY
        }

        stats_res = requests.get(stats_url, params=stats_params).json()
        stats = stats_res["items"][0]["statistics"]
        view_count = int(stats.get("viewCount", 0))

        if view_count >= 2000:
            videos.append({
                "title": item["snippet"]["title"],
                "description": item["snippet"]["description"],
                "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
                "video_id": video_id,
                "views": view_count
            })

        if len(videos) == 10:
            break

    return videos

# ✅ Summarize text using Hugging Face
def summarize(text):
    if not text.strip():
        return "No description to summarize."
    result = summarizer(text[:1024], max_length=60, min_length=20, do_sample=False)
    return result[0]['summary_text']

if query:
    with st.spinner("📺 Fetching and summarizing top videos..."):
        videos = fetch_filtered_videos(query)

        if not videos:
            st.warning("No suitable videos found. Try a different location.")
        else:
            for video in videos:
                st.image(video["thumbnail"])
                st.markdown(f"### [{video['title']}](https://www.youtube.com/watch?v={video['video_id']})")
                st.write(f"👁️ Views: {video['views']:,}")
                st.write("📄 Description:", video["description"] or "_No description_")
                summary = summarize(video["description"])
                st.success("📝 Summary: " + summary)
