import spotipy
from spotipy.oauth2 import SpotifyOAuth
import urllib.parse
import os

# 🔹 פרטי החיבור ל-Spotify (יש לוודא שהתעדכנו בפורטל של Spotify Developers)
SPOTIFY_CLIENT_ID = "3dee87c95878453cbf6b7c54a59e2a20"
SPOTIFY_CLIENT_SECRET = "103c8fccc71e4acb8bcb2ffc8386b607"
SPOTIFY_REDIRECT_URI = "https://songz-bot.onrender.com/callback"





# 🔹 יצירת קובץ התחברות אוטומטי
CACHE_PATH = os.path.join(os.getcwd(), ".spotipyauthcache")

sp_oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="playlist-modify-public playlist-modify-private",
    cache_path=CACHE_PATH,  # 🔹 שמירת הטוקן אוטומטית
    open_browser=False
)

# 🔹 ניסיון לקבל טוקן מהמטמון
token_info = sp_oauth.get_cached_token()

if not token_info:
    auth_url = sp_oauth.get_authorize_url()
    print(f"🔗 פתח את הקישור הבא בדפדפן והתחבר ל-Spotify:\n{auth_url}")
    response_url = input("📋 הדבק כאן את ה-URL שהתקבל לאחר ההתחברות: ").strip()

    parsed_url = urllib.parse.urlparse(response_url)
    query_params = urllib.parse.parse_qs(parsed_url.query)

    if "code" in query_params:
        code = query_params["code"][0]
        token_info = sp_oauth.get_access_token(code, as_dict=True)
    else:
        print("❌ שגיאה: קוד הרשאה לא נמצא.")
        exit(1)

sp = spotipy.Spotify(auth=token_info["access_token"])
print("✅ חיבור מוצלח ל-Spotify!")


