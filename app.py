import streamlit as st
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
API_KEY = os.getenv("API_KEY")

# API anahtarını oku
genai.configure(api_key=os.getenv("API_KEY"))

model = genai.GenerativeModel("gemini-2.0-flash")


