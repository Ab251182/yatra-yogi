import streamlit as st
import openai
import requests

# ✅ Load API keys from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]
youtube_api_key = st.secrets["YOUTUBE_API_KEY"]

# ✅ Debug check - shows message if OpenAI key loads
st.write("🔑 OpenAI Key Loaded")

# ✅ Function to fetch videos from YouTube
def fetch_youtube_videos(query):
    search_url = "https://www.googleapis.com/youtube/v3/search"
    search_params = {
        "part": "snippet",
        "q": query,
        "key": youtube_api_key,
        "maxResults": 10,
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

# ✅ Function to summarize video using OpenAI
def summarize_video(title, description):
    prompt = f"Summarize this travel video:\nTitle: {title}\nDescription: {description}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]

# ✅ Streamlit UI
st.title("🌍 Yatra Yogi – Top 10 Travel Videos")
query = st.text_input("Enter a destination (e.g., Bali, Ladakh)")

if query:
    with st.spinner("Fetching and summarizing videos..."):
        videos = fetch_youtube_videos(query)
        for video in videos:
            st.subheader(video["title"])
            st.write("📄 Description:", video["description"])
            summary = summarize_video(video["title"], video["description"])
            st.success("📝 Summary: " + summary)
