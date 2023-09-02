import os

import numpy as np
from PIL import Image, ImageDraw

from tier_block import TierBlock
from utils import get_font


class Checklist:
    def __init__(self, mode="D", level=23, width=1000, songs_per_row=8,
                 margin=5, text_margin=100, check_size=0.6):
        self.mode = mode
        self.level = level
        self.width = width
        self.songs_per_row = songs_per_row
        self.margin = margin
        self.text_margin = text_margin
        self.tier_blocks = {}
        self.height = margin

        jacket_width = (width - text_margin - 2 * margin) // songs_per_row
        jacket_height = jacket_width * 9 // 16
        self.jacket_size = np.array([jacket_width, jacket_height])
        self.check_size = (self.jacket_size * check_size).astype(int)
        self.check_margin = (self.jacket_size - self.check_size) // 2

        self.image = None
        self.records = None
        self.font = get_font(size=self.check_size[1])

    def add_tier_block(self, tier, color):
        args = [self.width, self.songs_per_row, self.margin, self.text_margin]
        block = TierBlock(tier, color, *args)
        self.tier_blocks[tier] = {
            "block": block,
            "y_from": None
        }

    def add_songs(self, tier, songs):
        self.tier_blocks[tier]["block"].add_songs(songs)

    def _compute_size(self):
        self.height = self.margin
        for tier, block in self.tier_blocks.items():
            block["y_from"] = self.height
            self.height += block["block"].height + self.margin

    def get_checklist_image(self):
        for block in self.tier_blocks.values():
            block["block"].get_tier_image()
        self._compute_size()
        image = Image.new("RGB", (self.width, self.height), "white")
        for block in self.tier_blocks.values():
            image.paste(block["block"].image, (0, block["y_from"]))
        self.image = image
        return image

    def set_records(self, df):
        self.records = df.query(f"mode == '{self.mode}' and level == {self.level}")

    def check(self, checker="red_slash"):
        """
        checker : 'score', 'grade', 'plate' or a checker name.
        Current supported checker names are ['red_slash', 'red_v']
        """
        records = self.records
        image = self.image.copy()
        if checker in ["red_slash", "red_v"]:
            check_path = os.path.join("images", "checker", checker + ".png")
            checker = Image.open(check_path)
            checker = checker.resize(self.jacket_size, resample=Image.BOX)
        for _, record in records.iterrows():
            self._check(image, record, checker)
        return image

    def _check(self, image, record, checker):
        title = record["title"]
        if isinstance(checker, str):
            if checker in ["grade", "plate"]:
                path = os.path.join("images", checker, record[checker] + ".png")
                checker = Image.open(path)
                checker = checker.resize(self.check_size, resample=Image.BOX)
            check_margin = self.check_margin
        else:
            check_margin = np.array([0, 0])
        for block in self.tier_blocks.values():
            loc = block["block"].songs_location.get(title, None)
            if loc is not None:
                loc = tuple(check_margin + loc + (0, block["y_from"]))
                if checker == "score":
                    draw = ImageDraw.Draw(image)
                    score = f"{record['score'] // 1000 / 10:.1f}"
                    draw.text(loc, score, fill="red", font=self.font, stroke_width=3, stroke_fill="green")
                else:
                    image.paste(checker, loc, checker)
