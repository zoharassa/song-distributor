from flask import Flask, request, redirect, session
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

# 🔹 הגדרת פרטי ההתחברות ל-Spotify
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "66de8086ff0e443a92518ffff0805f5c")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "63ea9e2cb1564a939e768b73eb501f23")
SPOTIFY_REDIRECT_URI = "https://songz-bot.onrender.com/callback"
SCOPE = "playlist-modify-public playlist-modify-private"

# 🔹 יצירת Flask אפליקציה
app = Flask(__name__)
app.secret_key = os.urandom(24)  # יצירת מפתח סודי לאתחול session

# 🔹 ביטול Cache והכרחת התחברות מחדש
sp_oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope=SCOPE,
    cache_path=None
)

@app.route("/")
def home():
    """עמוד בית ראשי"""
    return "🚀 Spotify Auth Server is running!"

@app.route("/login")
def login():
    """ביצוע התחברות מחדש כל פעם"""
    session.pop("token_info", None)  # ביטול שמירת הטוקן
    auth_url = sp_oauth.get_authorize_url()
    print(f"🔗 התחברות ל-Spotify: {auth_url}")
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
        
        if not token_info or "access_token" not in token_info:
            print("❌ Token is empty! Something went wrong.")
            return "❌ Authentication failed: No token received.", 400

        # **הדפסה נוספת לוודא שהטוקן אכן נוצר**
        print(f"🔐 Access Token: {token_info['access_token']}")
        print(f"🔄 Expires In: {token_info['expires_in']} seconds")

        # שמירת הטוקן בזיכרון
        global spotify_token
        spotify_token = token_info["access_token"]

        return "✅ Authentication successful! You can close this window."

    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return f"❌ Authentication error: {str(e)}", 500

@app.route("/me")
def get_spotify_profile():
    """בודק אם אנחנו מחוברים ומחזיר את פרטי המשתמש"""
    token_info = session.get("token_info")
    if not token_info:
        return "❌ No active session. Please log in again.", 401

    sp = spotipy.Spotify(auth=token_info["access_token"])
    user_info = sp.current_user()
    return f"✅ מחובר כ: {user_info['display_name']} ({user_info['id']})"

@app.route("/logout")
def logout():
    """התנתקות מהמערכת - איפוס ה-Session"""
    session.clear()
    print("🔴 User logged out. Session cleared.")
    return "✅ Logged out! Please log in again."


# 🔹 הפעלת השרת עם Gunicorn / Waitress
if __name__ == "__main__":
    from waitress import serve
    print("🚀 Running with Waitress")
    serve(app, host="0.0.0.0", port=8080)
