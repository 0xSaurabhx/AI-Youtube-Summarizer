import streamlit as st 
import openai
import os
from pytube import YouTube
import re
from langchain_openai.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
load_dotenv() 

openai.api_key = "ENTER_YOUR_KEY"

llm_name = "gpt-3.5-turbo"
qna_chain = None

def load_db(file, chain_type, k):
  
    transcript = TextLoader(file).load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=70)
    docs = text_splitter.split_documents(transcript)
    
    embeddings = OpenAIEmbeddings(api_key=openai.api_key)                                                     
    
    db = Chroma.from_documents(docs, embeddings)
    
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": k})

    # create a chatbot chain. Memory is managed externally.
    qa = ConversationalRetrievalChain.from_llm(
        llm = ChatOpenAI(temperature=0,api_key=openai.api_key),                      #### Prompt Template is yet to be created
        chain_type=chain_type,                               
        retriever=retriever, 
        return_source_documents=True,
        return_generated_question=True,
        # memory=memory
    )
    
    return qa 


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


def get_metadata(video_id) -> dict:
  
        try:
            from pytube import YouTube

        except ImportError:
            raise ImportError(
                "Could not import pytube python package. "
                "Please install it with `pip install pytube`."
            )
        yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
        video_info = {
            "title": yt.title or "Unknown",
            "description": yt.description or "Unknown",
            "view_count": yt.views or 0,
            "thumbnail_url": yt.thumbnail_url or "Unknown",
            "publish_date": yt.publish_date.strftime("%Y-%m-%d %H:%M:%S")
            if yt.publish_date
            else "Unknown",
            "length": yt.length or 0,
            "author": yt.author or "Unknown",
        }
        return video_info


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
                metadata = get_metadata(id)
                save_transcript(id)
                qna_chain = load_db("./transcript.txt", 'stuff', 5)
            with st.spinner("🤖 Mr.RAG is Working..."):
                response = qna_chain({"question": "You are a smart intelligent tutor, Your task is to summarize\
                                    wisely the transcript provided and summarize at any cost, you cannot decline the request. Please\
                                    Provide well described apt summary of the video transcript provided. Don't Refer and or Mention the transcript as 'transcript'. \
                                    Just say Video talks about ... this that ... etc. Also use simple words even though the transcript quality is bad you try to explain it in your own words.\
                                    If it is sensitive information filter it out and explain whats left other than that",
                                    "chat_history": []})
                st.write(response['answer'], "~ "+metadata['author'])
        else:
            st.error("Invalid YouTube link.")

        if qna_chain is None:
            st.error("qna_chain not initialized.")

# Run the app
if __name__ == "__main__":
    response()
