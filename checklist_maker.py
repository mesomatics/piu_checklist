import os
import json

import numpy as np

from checklist import Checklist
from config import SONGS


class ChecklistMaker:
    def _make_default(self, mode, level):
        songs_by_type = {x: [] for x in range(1, 5)}

        for title, levels in SONGS.items():
            if mode in levels:
                if level in levels[mode]:
                    songs_by_type[levels["Type"]].append(title)

        n_songs = sum([len(x) for x in songs_by_type.values()])
        songs_per_row = max(int(np.sqrt(0.7 * n_songs)), 6)

        checklist = Checklist(mode=mode, level=level, songs_per_row=songs_per_row)
        type_order = [2, 4, 3, 1]
        type_texts = ["아케", "풀송", "리믹", "숏컷"]
        colors = ["red", "yellow", "green", "blue"]
        for song_type, type_text, color in zip(type_order, type_texts, colors):
            songs = songs_by_type[song_type] 
            if len(songs) > 0:
                checklist.add_tier_block(type_text, color)
                checklist.add_songs(type_text, songs)
        return checklist

    def _load_template(self, template):
        kwargs = {}
        for keyword in ["mode", "level", "width", "songs_per_row", "margin", "text_margin"]:
            if keyword in template:
                kwargs[keyword] = template[keyword]
        checklist = Checklist(**kwargs)
        for tier, value in template["songs"].items():
            checklist.add_tier_block(tier, color=value["color"])
            checklist.add_songs(tier, value["titles"])
        return checklist

    def make(self, mode="D", level=23, template=None):
        if template is None:
            checklist = self._make_default(mode, level)
        else:
            path = os.path.join("templates", template + ".json")
            with open(path, "r", encoding="utf-8") as f:
                template = json.load(f)
            checklist = self._load_template(template)
        img = checklist.get_checklist_image()
        return checklist
