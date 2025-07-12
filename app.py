import streamlit as st
import requests
from transformers import pipeline

# ✅ Load Hugging Face summarizer pipeline
summarizer = pipeline("summarization")

# ✅ Function to fetch YouTube videos
def fetch_youtube_videos(query, youtube_api_key):
    search_url = "https://www.googleapis.com/youtube/v3/search"
    search_params = {
        "part": "snippet",
        "q": query,
        "key": youtube_api_key,
        "maxResults": 5,
        "type": "video"
    }

    response = requests.get(search_url, params=search_params)
    data = response.json()
    items = data.get("items", [])

    videos = []
    for item in items:
        videos.append({
            "title": item["snippet"]["title"],
            "description": item["snippet"]["description"]
        })
    return videos

# ✅ Summarize using Hugging Face
def summarize_video(title, description):
    text = f"{title}. {description}"
    if len(text) < 50:
        return "Too short to summarize."
    result = summarizer(text, max_length=60, min_length=25, do_sample=False)
    return result[0]['summary_text']

# ✅ Streamlit UI
st.title("🌍 Yatra Yogi – Top 10 Travel Videos")

# Load from Streamlit secrets
youtube_api_key = st.secrets["YOUTUBE_API_KEY"]

query = st.text_input("Enter a destination (e.g., Bali, Ladakh)")

if query:
    with st.spinner("🔍 Fetching and summarizing videos..."):
        videos = fetch_youtube_videos(query, youtube_api_key)
        for video in videos:
            st.subheader(video["title"])
            st.write("📄 Description:", video["description"])
            summary = summarize_video(video["title"], video["description"])
            st.success("📝 Summary: " + summary)
