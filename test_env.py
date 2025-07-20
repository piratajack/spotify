# test_env.py
from dotenv import load_dotenv
import os

load_dotenv()
print("SPOTIFY_CLIENT_ID:", os.getenv('SPOTIFY_CLIENT_ID'))
print("SPOTIFY_CLIENT_SECRET:", os.getenv('SPOTIFY_CLIENT_SECRET'))
print("SPOTIFY_REDIRECT_URI:", os.getenv('SPOTIFY_REDIRECT_URI'))
print("FLASK_SECRET_KEY:", os.getenv('FLASK_SECRET_KEY'))