import streamlit as st
import requests
from transformers import pipeline

# ✅ Load Hugging Face summarizer
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

# ✅ YouTube API key from Streamlit secrets
youtube_api_key = st.secrets["YOUTUBE_API_KEY"]

# ✅ Function to fetch top 10 recent travel videos with at least 10K views and < 6 months old
def fetch_top_videos(query):
    search_url = "https://www.googleapis.com/youtube/v3/search"
    video_url = "https://www.googleapis.com/youtube/v3/videos"

    search_params = {
        "part": "snippet",
        "q": f"{query} travel",
        "type": "video",
        "maxResults": 20,
        "key": youtube_api_key,
        "order": "date",
        "publishedAfter": "2024-12-01T00:00:00Z"  # Adjust if needed
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
        if views >= 10000:
            results.append({
                "title": item["snippet"]["title"],
                "description": item["snippet"]["description"],
                "video_id": item["id"],
                "views": views,
                "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"]
            })

    return sorted(results, key=lambda x: x["views"], reverse=True)[:10]

# ✅ Summarize video using Hugging Face
def summarize_text(text):
    if len(text.strip()) < 50:
        return "Too short to summarize."
    summary = summarizer(text[:1024], max_length=60, min_length=20, do_sample=False)
    return summary[0]["summary_text"]

# ✅ Streamlit UI
st.title("🌍 Yatra Yogi – Top 10 Travel Videos")
query = st.text_input("Enter a destination (e.g., Bali, Ladakh)")

if query:
    with st.spinner("🔍 Fetching videos..."):
        videos = fetch_top_videos(query)

    if not videos:
        st.warning("No recent videos found with enough views.")
    else:
        for video in videos:
            st.image(video["thumbnail"], width=320)
            st.markdown(f"### [{video['title']}]"
                        f"(https://www.youtube.com/watch?v={video['video_id']})")
            st.caption(f"👁️ {video['views']:,} views")
            st.write("📄 Description:", video["description"])
            with st.spinner("✍️ Summarizing..."):
                summary = summarize_text(video["description"])
            st.success("📝 Summary: " + summary)
            st.markdown("---")
