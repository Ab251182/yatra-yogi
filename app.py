import streamlit as st
import requests
from transformers import pipeline

# Initialize Hugging Face summarizer (free, no key needed)
@st.cache_resource
def get_summarizer():
    return pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

summarizer = get_summarizer()

# YouTube API key from secrets
youtube_api_key = st.secrets["YOUTUBE_API_KEY"]

# Function to fetch top videos (min 2,000 views, last 6 months)
def fetch_top_videos(query):
    search_url = "https://www.googleapis.com/youtube/v3/search"
    video_url = "https://www.googleapis.com/youtube/v3/videos"

    search_params = {
        "part": "snippet",
        "q": f"{query} travel",
        "type": "video",
        "maxResults": 50,
        "key": youtube_api_key,
        "order": "date",
        "publishedAfter": "2024-12-01T00:00:00Z"  # 6 months back approx
    }

    search_resp = requests.get(search_url, params=search_params).json()
    video_ids = [item["id"]["videoId"] for item in search_resp.get("items", [])]

    if not video_ids:
        return []

    details_params = {
        "part": "snippet,statistics",
        "id": ",".join(video_ids),
        "key": youtube_api_key
    }

    details_resp = requests.get(video_url, params=details_params).json()
    results = []

    for item in details_resp.get("items", []):
        views = int(item["statistics"].get("viewCount", 0))
        if views >= 2000:  # ✅ Filter: at least 2,000 views
            results.append({
                "title": item["snippet"]["title"],
                "description": item["snippet"]["description"],
                "video_id": item["id"],
                "views": views,
                "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"]
            })

    return sorted(results, key=lambda x: x["views"], reverse=True)[:10]

# Summarization function using Hugging Face
def summarize(text):
    if not text.strip():
        return "No description to summarize."
    try:
        result = summarizer(text[:1024], max_length=60, min_length=25, do_sample=False)
        return result[0]['summary_text']
    except Exception as e:
        return f"Summarization failed: {e}"

# Streamlit UI
st.set_page_config(page_title="Yatra Yogi", page_icon="🌍")
st.title("🌍 Yatra Yogi – Top Travel Videos")

query = st.text_input("Enter a destination (e.g., Goa, Bali, Ladakh)")

if query:
    with st.spinner("🔍 Searching and summarizing..."):
        videos = fetch_top_videos(query)

        if not videos:
            st.warning("No suitable videos found. Try a different destination.")
        else:
            for video in videos:
                st.image(video["thumbnail"], width=300)
                st.markdown(f"### [{video['title']}](https://www.youtube.com/watch?v={video['video_id']})")
                st.caption(f"👁️ {video['views']} views")
                st.write("📝 Description:", video["description"])
                summary = summarize(video["description"])
                st.success("✍️ Summary: " + summary)
                st.markdown("---")
