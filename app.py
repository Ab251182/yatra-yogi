import streamlit as st
import requests
from datetime import datetime, timedelta
from transformers import pipeline
import wikipedia

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
st.set_page_config(page_title="Yatra Yogi", page_icon="🌍")
st.title("🌍 Yatra Yogi – Your AI Travel Buddy")

query = st.text_input("Enter a destination (e.g., Bali, Ladakh, Goa)")

# ✅ Fetch and filter YouTube videos
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

# ✅ Get user city from IP
def get_user_location():
    try:
        res = requests.get("https://ipinfo.io/json")
        data = res.json()
        return data.get('city', 'your city')
    except:
        return 'your city'

# ✅ If user enters a destination
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

    # ✅ Destination Summary (Wikipedia)
    st.subheader(f"📍 About {query.title()}")
    try:
        summary = wikipedia.summary(query, sentences=3)
    except:
        summary = f"{query.title()} is a beautiful destination worth visiting!"
    st.write(summary)

    # ✅ User City and Travel Tips
    user_city = get_user_location()
    st.subheader(f"🚗 How to Reach {query.title()} from {user_city}")
    st.markdown(f"""
- ✈️ **Flight**: Most cities including {user_city} have direct or connecting flights to {query}.
- 🚆 **Train**: Check trains from {user_city} to the nearest station.
- 🚘 **Road**: Reach by car or cab via highways.
    """)

    # ✅ Booking / Offer Links
    st.subheader("💸 Book Your Trip")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"[🛫 Flights to {query}](https://www.cleartrip.com/flights)")
    with col2:
        st.markdown(f"[🏨 Hotels in {query}](https://www.booking.com/searchresults.html?ss={query})")

    col3, col4 = st.columns(2)
    with col3:
        st.markdown(f"[🍛 Food in {query}](https://www.zomato.com/{query.lower()})")
    with col4:
        st.markdown(f"[🏄 Activities in {query}](https://www.thrillophilia.com/cities/{query.lower()})")

    # ✅ Itinerary Generator
    if st.button("🧳 Want a 3-Day Itinerary?"):
        st.subheader(f"🗓️ Suggested 3-Day Itinerary for {query.title()}")
        st.markdown(f"""
**Day 1:**  
- Arrive at {query}  
- Explore local market  
- Sunset at scenic point

**Day 2:**  
- Visit top attractions  
- Street food and shopping  
- Cultural or beach experience

**Day 3:**  
- Half-day nature walk or museum visit  
- Souvenir shopping  
- Return journey
        """)
