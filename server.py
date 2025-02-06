from flask import Flask, request, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

# 🔹 פרטי האימות של Spotify (וודא שהם תואמים לאלה שהגדרת ב-Spotify Developers)
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "66de8086ff0e443a92518ffff0805f5c")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "63ea9e2cb1564a939e768b73eb501f23")
SPOTIFY_REDIRECT_URI = "https://songz-bot.onrender.com/callback"
SCOPE = "playlist-modify-public playlist-modify-private"

# 🔹 יצירת אפליקציית Flask
app = Flask(__name__)

# 🔹 אתחול החיבור ל-Spotify API
sp_oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope=SCOPE
)

@app.route("/")
def home():
    """עמוד בית פשוט"""
    return "🚀 Spotify Auth Server is running! 🔥"

@app.route("/login")
def login():
    """יצירת קישור התחברות ל-Spotify"""
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route("/callback")
def callback():
    """קליטת קוד ההתחברות והחזרת טוקן גישה"""
    code = request.args.get("code")
    if not code:
        return "❌ Authentication failed!", 400

    try:
        # קבלת טוקן גישה
        token_info = sp_oauth.get_access_token(code)

        # שמירת הטוקן לקובץ `.cache`
        with open(".spotipyauthcache", "w") as f:
            f.write(str(token_info))

        return "✅ Authentication successful! You can close this window."

    except Exception as e:
        return f"❌ Authentication error: {str(e)}", 500

# 🔹 הפעלת השרת עם Gunicorn / Waitress
if __name__ == "__main__":
    try:
        from waitress import serve
        print("🚀 Running with Waitress")
        serve(app, host="0.0.0.0", port=8080)
    except ImportError:
        print("⚠ Waitress not found, running Flask default server")
        app.run(host="0.0.0.0", port=8080, debug=True)


