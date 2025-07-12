import streamlit as st
import openai
import requests
import datetime

# ✅ Load API keys
openai.api_key = st.secrets["OPENAI_API_KEY"]
youtube_api_key = st.secrets["YOUTUBE_API_KEY"]

# ✅ OpenAI helper
def summarize_video(title, description):
    prompt = f"Summarize this travel video:\nTitle: {title}\nDescription: {description}"
    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return "Summary unavailable due to API limits or error."

# ✅ YouTube search function with filters
def fetch_youtube_videos(query):
    search_url = "https://www.googleapis.com/youtube/v3/search"
    video_url = "https://www.googleapis.com/youtube/v3/videos"

    # 6 months ago date
    six_months_ago = (datetime.datetime.now() - datetime.timedelta(days=180)).isoformat("T") + "Z"

    search_params = {
        "part": "snippet",
        "q": f"{query} travel",
        "key": youtube_api_key,
        "maxResults": 20,
        "type": "video",
        "order": "viewCount",
        "publishedAfter": six_months_ago
    }

    search_res = requests.get(search_url, params=search_params).json()
    video_ids = [item["id"]["videoId"] for item in search_res.get("items", [])]

    if not video_ids:
        return []

    # Now fetch video stats (views)
    video_params = {
        "part": "snippet,statistics",
        "id": ",".join(video_ids),
        "key": youtube_api_key
    }

    video_res = requests.get(video_url, params=video_params).json()

    # Filter videos with >10,000 views
    videos = []
    for item in video_res.get("items", []):
        views = int(item["statistics"].get("viewCount", 0))
        if views >= 10000:
            videos.append({
                "title": item["snippet"]["title"],
                "description": item["snippet"]["description"],
                "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"],
                "video_id": item["id"],
                "views": views
            })

    return videos[:10]

# ✅ Streamlit UI
st.title("🌍 Yatra Yogi – Top 10 Travel Videos")
query = st.text_input("Enter a destination (e.g., Bali, Ladakh, Dubai)")

if query:
    with st.spinner("Fetching videos and generating summaries..."):
        videos = fetch_youtube_videos(query)
        if not videos:
            st.warning("No recent popular videos found.")
        else:
            for video in videos:
                st.image(video["thumbnail"], width=360)
                st.markdown(f"### [{video['title']}](https://www.youtube.com/watch?v={video['video_id']})")
                st.caption(f"👁️ {video['views']:,} views")
                st.write("📄", video["description"])
                summary = summarize_video(video["title"], video["description"])
                st.success("📝 Summary: " + summary)
