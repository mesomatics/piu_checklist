import os
import json

PATH = os.getcwd()
PATH_SONGS = os.path.join(PATH, "songs", "songs_all.json")
PATH_IMAGES = os.path.join(PATH, "songs", "images")
PATH_FONT = os.path.join(PATH, "font", "HMKMMAG.ttf")

with open(PATH_SONGS, "r", encoding="utf-8") as s:
    SONGS = json.load(s)
