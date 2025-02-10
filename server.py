from flask import Flask, request, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import json

# 🔹 Spotify authentication credentials
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "66de8086ff0e443a92518ffff0805f5c")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "63ea9e2cb1564a939e768b73eb501f23")
SPOTIFY_REDIRECT_URI = "https://songz-bot.onrender.com/callback"
SCOPE = "playlist-modify-public playlist-modify-private"

# 🔹 Token cache file path
CACHE_PATH = os.path.join(os.getcwd(), ".spotipyauthcache")

# 🔹 Create the Flask application
app = Flask(__name__)

# 🔹 Initialize the SpotifyOAuth object with the cache file
sp_oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope=SCOPE,
    cache_path=CACHE_PATH  # token will be saved here
)

@app.route("/")
def home():
    """Simple home page."""
    return "🚀 Spotify Auth Server is running! 🔥"

@app.route("/login")
def login():
    """Generate the Spotify login URL."""
    auth_url = sp_oauth.get_authorize_url()
    print(f"🔗 Generated Auth URL: {auth_url}")  # log the URL
    return redirect(auth_url)

@app.route("/callback")
def callback():
    """Receive the auth code from Spotify's redirect."""
    code = request.args.get("code")
    if not code:
        print("❌ No authorization code received!")
        return "❌ Authentication failed! No code received.", 400

    try:
        print(f"🔄 Received auth code: {code}")  # log the code
        token_info = sp_oauth.get_access_token(code)
        print(f"🔑 Full Token Response: {token_info}")  # log the full token response

        # Check if token_info is valid
        if not token_info or "access_token" not in token_info:
            print("❌ Token is empty! Something went wrong.")
            return "❌ Authentication failed: No token received.", 400

        # Save the token to the cache file
        print(f"📂 Saving token to: {CACHE_PATH}")
        try:
            with open(CACHE_PATH, "w") as f:
                json.dump(token_info, f)
            print(f"💾 Token saved successfully to {CACHE_PATH}")
        except Exception as e:
            print(f"❌ ERROR: Failed to save token - {str(e)}")
            return f"❌ ERROR: Failed to save token - {str(e)}", 500

        return "✅ Authentication successful! You can close this window."

    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return f"❌ Authentication error: {str(e)}", 500

@app.route("/me")
def get_spotify_profile():
    """Check if we're logged in and return the user's profile details."""
    try:
        if not os.path.exists(CACHE_PATH):
            return "❌ No active session. Please log in again.", 401

        with open(CACHE_PATH, "r") as f:
            token_info = json.load(f)

        sp = spotipy.Spotify(auth=token_info["access_token"])
        user_info = sp.current_user()
        return f"✅ Logged in as: {user_info['display_name']} ({user_info['id']})"
    except Exception as e:
        return f"❌ Error accessing Spotify API: {str(e)}", 500

@app.route("/logout")
def logout():
    """Log out by deleting the cache file and reinitializing the SpotifyOAuth object."""
    try:
        if os.path.exists(CACHE_PATH):
            os.remove(CACHE_PATH)
            print("🗑️ Cache file removed successfully.")
        else:
            print("🗑️ No cache file to remove.")

        # Reinitialize sp_oauth to clear any cached in-memory token
        global sp_oauth
        sp_oauth = SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            scope=SCOPE,
            cache_path=CACHE_PATH
        )
        return "✅ Logged out successfully."
    except Exception as e:
        print(f"❌ Logout error: {str(e)}")
        return f"❌ Logout error: {str(e)}", 500

# 🔹 Start the server with Waitress or Flask's default server
if __name__ == "__main__":
    try:
        from waitress import serve
        print("🚀 Running with Waitress")
        serve(app, host="0.0.0.0", port=8080)
    except ImportError:
        print("⚠ Waitress not found, running Flask default server")
        app.run(host="0.0.0.0", port=8080, debug=True)
