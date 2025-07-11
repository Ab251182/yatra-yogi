import streamlit as st
import openai
import requests

# ✅ Add your keys here
openai.api_key = "your-openai-key"
youtube_api_key = "your-youtube-api-key"

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
    items = data.get("items", [])  # avoid KeyError

    videos = []
    for item in items:
        videos.append({
            "title": item["snippet"]["title"],
            "description": item["snippet"]["description"]
        })
    return videos

def summarize_video(title, description):
    prompt = f"Summarize this travel video:\n\nTitle: {title}\nDescription: {description}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']

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
