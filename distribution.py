import spotipy
from spotipy.oauth2 import SpotifyOAuth
import csv
import urllib.parse
import os
from spotify_config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI

# 🔹 קביעת קובץ המטמון של Spotipy
CACHE_PATH = os.path.join(os.getcwd(), ".spotipyauthcache")

sp_oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="playlist-modify-public playlist-modify-private",
)

# 🔹 ניסיון לטעון טוקן קיים
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

DEFAULT_PLAYLIST_ID = "כאן_שים_את_ה-ID_שלך"


# 🔹 קריאת שירים להפצה
def get_songs_to_distribute():
    songs_to_distribute = []
    updated_rows = []

    try:
        with open("songs.csv", "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            fieldnames = ["שם שיר", "אמן", "אורך", "סטטוס"]

            for row in reader:
                if "סטטוס" not in row or not row["סטטוס"]:
                    row["סטטוס"] = "ממתין"
                updated_rows.append(row)
                if row["סטטוס"] == "ממתין":
                    songs_to_distribute.append(row)

        with open("songs.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(updated_rows)

        return songs_to_distribute

    except FileNotFoundError:
        print("⚠ הקובץ songs.csv לא נמצא.")
        return []


# 🔹 חיפוש שיר ב-Spotify
def search_spotify(song_name, artist_name):
    query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=query, limit=5)

    if not results["tracks"]["items"]:
        print(f"❌ לא נמצאו תוצאות ב-Spotify עבור {song_name} - {artist_name}.")
        return None, None

    options = []
    for idx, track in enumerate(results["tracks"]["items"], start=1):
        track_name = track["name"]
        track_artist = track["artists"][0]["name"]
        track_url = track["external_urls"]["spotify"]
        print(f"{idx}. {track_name} - {track_artist} ({track_url})")
        options.append((track["id"], track_url))

    choice = input("⏩ בחר מספר תוצאה (או השאר ריק לדילוג): ").strip()

    if choice.isdigit():
        choice_idx = int(choice) - 1
        if 0 <= choice_idx < len(options):
            return options[choice_idx]

    print("❌ השיר לא נבחר.")
    return None, None


# 🔹 הוספת שיר לפלייליסט
def add_song_to_playlist(playlist_id, track_id):
    try:
        sp.playlist_add_items(playlist_id, [track_id])
        print("✅ השיר נוסף בהצלחה!")
    except spotipy.exceptions.SpotifyException as e:
        print(f"❌ שגיאה בהוספת השיר: {e}")


# 🔹 עדכון סטטוס
def update_song_status(song_name, status):
    try:
        with open("songs.csv", "r", encoding="utf-8") as file:
            rows = list(csv.DictReader(file))

        fieldnames = ["שם שיר", "אמן", "אורך", "סטטוס"]

        for row in rows:
            if row["שם שיר"] == song_name:
                row["סטטוס"] = status

        with open("songs.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    except FileNotFoundError:
        print("⚠ הקובץ songs.csv לא נמצא.")
