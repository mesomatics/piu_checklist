import json

PATH_SONGS = "songs/songs_all.json"
PATH_IMAGES = "songs/images"
PATH_FONT = "font/HMKMMAG.ttf"

with open(PATH_SONGS, "r", encoding="utf-8") as s:
    SONGS = json.load(s)
