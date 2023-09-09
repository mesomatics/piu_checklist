import os
import numpy as np
from PIL import Image, ImageDraw

from config import PATH_IMAGES, SONGS
from utils import get_font
from image_builder import JacketBuilder


class TierBlock:
    def __init__(self, tier, color, width=1000, songs_per_row=7, margin=5, text_margin=100):
        self.tier = tier
        self.color = color
        self.width = width
        self.songs_per_row = songs_per_row
        self.margin = margin
        self.text_margin = text_margin
        self.songs = []

        jacket_width = (width - text_margin - 2 * margin) // songs_per_row
        jacket_height = jacket_width * 9 // 16
        self.jacket_size = (jacket_width, jacket_height)

        self.n_rows = None
        self.height = None
        self.songs_location = {}

    def add_songs(self, songs):
        if isinstance(songs, str):
            self.songs.append(songs)
        else:
            self.songs.extend(songs)

    def _compute_size(self):
        self.n_rows = int(np.ceil(len(self.songs) / self.songs_per_row))
        self.height = self.n_rows * self.jacket_size[1] + 2 * self.margin

    def _compute_location(self):
        x = self.text_margin + self.margin
        y = self.margin
        for i, song in enumerate(self.songs):
            self.songs_location.update({song: (x, y)})
            x += self.jacket_size[0]
            if (i + 1) % self.songs_per_row == 0:
                y += self.jacket_size[1]
                x = self.text_margin + self.margin

    def _get_jacket_component(self):
        jb = JacketBuilder()
        image = Image.new("RGB", (self.width, self.height), self.color)
        x = self.text_margin + self.margin
        y = self.margin
        for song, loc in self.songs_location.items():
            try:
                path = SONGS[song]["image"]
                jacket_image = Image.open(os.path.join(PATH_IMAGES, path))
            except:
                song_type = SONGS[song]["Type"]
                jacket_image = jb.make_image(song, song_type=song_type)
            image.paste(jacket_image.resize(self.jacket_size, resample=Image.BOX), loc)
        return image

    def _get_text_component(self):
        image_text = Image.new("RGB", (self.text_margin, self.height), "white")
        draw = ImageDraw.Draw(image_text)
        
        font = get_font(size=40)
        text_x =(self.text_margin - font.getsize(self.tier)[0]) // 2
        text_y =(self.height - 40) // 2
        draw.text((text_x, text_y), self.tier, fill=self.color, font=font)
        return image_text

    def get_tier_image(self):
        self._compute_size()
        self._compute_location()
        image = self._get_jacket_component()
        image_text = self._get_text_component()
        image.paste(image_text)
        self.image = image
        return image
