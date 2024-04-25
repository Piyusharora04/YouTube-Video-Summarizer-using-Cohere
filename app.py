import requests
import os
from youtube_transcript_api import YouTubeTranscriptApi
from IPython.display import YouTubeVideo
import streamlit as st

def get_video_thumbnail(video_id):

    # Replace YOUR_API_KEY with your actual YouTube Data API v3 key
    api_key = "AIzaSyC4JXlj6bXJPRJHxhn8kZXvMhPVNOdQUbc"
    base_url = "https://www.googleapis.com/youtube/v3/videos"

    # Specify desired thumbnail size (maximum resolution)
    params = {
      "part": "snippet",
      "id": video_id,
      "key": api_key,
      "maxResults": 1,
    }

    try:
        response = requests.get(base_url, params=params)
        print(response.status_code)
        print(response.json())
        response.raise_for_status()  # Raise an exception for unsuccessful requests

        data = response.json()
        items = data.get("items", [])

        if items:
            thumbnail_url = items[0]["snippet"]["thumbnails"]["maxres"]["url"]      
            return thumbnail_url
        else:
            return None  # Video not found or no thumbnails available

    except requests.exceptions.RequestException as e:
        print(f"Error retrieving video thumbnail: {e}")
        return "bye"


def get_id(video_link):
    if "shared" in video_link:
        video_id = video_link.split("?")[0]
        video_id = video_id.split("/")[-1]
        print(video_id)
        return video_id
        
    else:
        video_id = video_link.split("=")[1]
        if "&" in video_id:
            video_id = video_id.split("&")[0]
        print(video_id)
        return video_id 
        
        

def yvs(video_url):
    youtube_video = str(video_url)

    cohere_api_key = "2wHSGlZJesqUP5A6L5LmumjMEjH2P8sVVGFSA84a"

    video_id = get_id(youtube_video)

    transcript = YouTubeTranscriptApi.get_transcript(video_id)

    result = ""
    for i in transcript:
        result += ' ' + i['text']
    
    print(result)  
    
    def summarize_with_cohere(text):
        url = "https://api.cohere.ai/summarize"
        headers = {'Authorization': f'Bearer {cohere_api_key}'}
        data = {
            "model": "command",  
            "text": text
        }
        response = requests.post(url, headers=headers, json=data)

        if 'summary' in response.json():
            return response.json()['summary']
        else:
            return "Summary not available from the API for this segment."
    
    num_iters = int(len(result)/200)  
    summarized_text = []

    
    for i in range(0, num_iters + 1):
        start = i * 1000
        end = (i + 1) * 1000
        # print("Input text \n" + result[start:end])
        out = summarize_with_cohere(result[start:end])
        # print("Summarized text\n" + out)
        summarized_text.append(out)
        
    # print('\n')
    # print('\n')
    
    # print(summarized_text)
    
    output = []
    for item in summarized_text:
        if(item != 'Summary not available from the API for this segment.'):
            output.append(str(item))

    new_string = ''
    for item in output:
        new_string += item + '\n'
    summary = new_string
    return summary



    

# Streamlit starts...
st.set_page_config(page_title="YouTube Video Summarizer", page_icon="", layout="wide")  # Set page title, icon, and wide layout

with st.sidebar:
    st.title("Summarize a YouTube Video")
    video_link = st.text_input("Enter YouTube Video Link")
    st.button("Summarize Video")

col1, col2 = st.columns(2)  # Create two columns for layout

if video_link:
    with col1:
        # Display video thumbnail using st.image
        thumbnail_url = get_video_thumbnail(get_id(video_link))  # Retrieve thumbnail after getting ID
        if thumbnail_url:
            st.image(thumbnail_url)
        else:
            st.write("No thumbnail available for this video.")
    with col2:
        with st.spinner("Summarizing video... Please Wait!"):
            summary = yvs(video_link)
        st.success("Summary:")
        st.write(summary)
else:
    st.warning("Please enter a YouTube video link.")



