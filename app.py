import streamlit as st 
import os
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
load_dotenv() 

GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']

def buffer(history, buff):

    if len(history) > buff :
        print(len(history)>buff)
        return history[-buff:]
    return history
    

def is_valid_yt(link):

    pattern = r'^(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w\-_]{11})(?:\S+)?$'
    match = re.match(pattern, link)
    if match:
        return True, match.group(1) 
    else:
        return False, None

def save_transcript(video_id):

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
    except Exception as e:
        print(f"Error fetching transcript for video {video_id}: {e}")
        return None
    if transcript:
        with open('transcript.txt', 'w') as file:
            for entry in transcript:
                file.write(f"~{int(entry['start'])}~{entry['text']} ")
        print(f"Transcript saved to: transcript.txt")

st.markdown("<h1 style='text-align: center; color: red;'>Y▶T Summarizer</h1>", unsafe_allow_html=True)
st.markdown("<h5 style='text-align: center; color: #fd6648;'>This tool doesnt summarize about any sensitive information. Currently recommended video language is english</h5>",unsafe_allow_html=True)
st.markdown("")
st.markdown("")
st.markdown("")
st.markdown("")
st.markdown("")

def response():
    yt_link = st.text_input("Enter YouTube Link:")    

    if st.button("Get Smart Summary", key="summary_button"):
        valid, id = is_valid_yt(yt_link)
        if valid:
            with st.spinner("Doing some magic ✨"):
                save_transcript(id)
                def get_transcript_text():
                    with open('./transcript.txt', 'r') as file:
                        transcript_text = file.read()
                    return transcript_text
                transcript_text = get_transcript_text()
            with st.spinner("🤖 Mr.RAG is Working..."):
                chat = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest")
                response = chat.invoke(f"transcript: {transcript_text} You are a smart intelligent tutor, Your task is to summarize wisely the transcript provided and summarize at any cost, you cannot decline the request. Please Provide well described apt summary of the video transcript provided. Don't Refer or Mention the transcript as 'transcript'. Just say Video talks about ... this that ... etc. Also use simple words even though the transcript quality is bad you try to explain it in your own words. If it is sensitive information filter it out and explain whats left other than that")
                st.markdown(response.content)
        else:
            st.error("Invalid YouTube link.")

if __name__ == "__main__":
    response()
