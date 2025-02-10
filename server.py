from flask import Flask, request, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import json

# 🔹 פרטי האימות של Spotify
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "66de8086ff0e443a92518ffff0805f5c")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "63ea9e2cb1564a939e768b73eb501f23")
SPOTIFY_REDIRECT_URI = "https://songz-bot.onrender.com/callback"
SCOPE = "playlist-modify-public playlist-modify-private"

# 🔹 קובץ שמירת הטוקן
CACHE_PATH = os.path.join(os.getcwd(), ".spotipyauthcache")

# 🔹 יצירת Flask אפליקציה
app = Flask(__name__)

# 🔹 אתחול החיבור ל-Spotify API עם Cache מוגדר
sp_oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope=SCOPE,
    cache_path=CACHE_PATH  # שמירה בקובץ
)

@app.route("/")
def home():
    """עמוד בית פשוט"""
    return "🚀 Spotify Auth Server is running! 🔥"

@app.route("/login")
def login():
    """יצירת קישור כניסה ל-Spotify"""
    auth_url = sp_oauth.get_authorize_url()
    print(f"🔗 Generated Auth URL: {auth_url}")  # הדפסת ה-URL ל-logs
    return redirect(auth_url)

@app.route("/callback")
def callback():
    """קליטת קוד ההתחברות מה-Redirect של Spotify"""
    code = request.args.get("code")
    if not code:
        print("❌ No authorization code received!")
        return "❌ Authentication failed! No code received.", 400

    try:
        print(f"🔄 Received auth code: {code}")  # הדפסת הקוד שהתקבל
        token_info = sp_oauth.get_access_token(code)
        print(f"🔑 Full Token Response: {token_info}")  # הדפסת כל המידע שהתקבל מ-Spotify

        # בדיקה אם הטוקן ריק
        if not token_info or "access_token" not in token_info:
            print("❌ Token is empty! Something went wrong.")
            return "❌ Authentication failed: No token received.", 400

        # ✅ שמירת הטוקן **בקובץ Cache**
        cache_path = os.path.join(os.getcwd(), ".spotipyauthcache")
        print(f"📂 Saving token to: {cache_path}")  # הדפסת הנתיב לטרמינל

        try:
            with open(cache_path, "w") as f:
                json.dump(token_info, f)
            print(f"💾 Token saved successfully to {cache_path}")  # אישור שהטוקן נשמר
        except Exception as e:
            print(f"❌ ERROR: Failed to save token - {str(e)}")  # הדפסת השגיאה
            return f"❌ ERROR: Failed to save token - {str(e)}", 500

        return "✅ Authentication successful! You can close this window."

    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return f"❌ Authentication error: {str(e)}", 500


@app.route("/me")
def get_spotify_profile():
    """בודק אם אנחנו מחוברים ומחזיר את פרטי המשתמש"""
    try:
        if not os.path.exists(CACHE_PATH):
            return "❌ No active session. Please log in again.", 401

        with open(CACHE_PATH, "r") as f:
            token_info = json.load(f)

        sp = spotipy.Spotify(auth=token_info["access_token"])
        user_info = sp.current_user()
        return f"✅ מחובר כ: {user_info['display_name']} ({user_info['id']})"
    except Exception as e:
        return f"❌ שגיאה בגישה ל-Spotify API: {str(e)}", 500

# 🔹 הפעלת השרת עם Gunicorn / Waitress
if __name__ == "__main__":
    try:
        from waitress import serve
        print("🚀 Running with Waitress")
        serve(app, host="0.0.0.0", port=8080)
    except ImportError:
        print("⚠ Waitress not found, running Flask default server")
        app.run(host="0.0.0.0", port=8080, debug=True)


