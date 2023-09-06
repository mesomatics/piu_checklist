import pandas as pd

from config import SONGS


class RatingCalculator:
    COEFFICIENT = {
        "SSS_P": 1.5, "SSS": 1.44, "SS_P": 1.38, "SS": 1.32, "S_P": 1.26, "S": 1.2,
        "AAA_P": 1.15, "AAA" : 1.1, "AA_P": 1.05, "AA": 1., "A_P": 0.9, "A": 0.8, "B": 0.7,
        "C": 0.0, "D": 0.0, "F": 0.0
    }

    def __init__(self):
        self.songs_info = self.get_songs_info()

    def get_base(self, level):
        return 100 + (level - 10) * (level - 9) * 5

    def get_songs_info(self):
        level_all = {
            "S": [],
            "D": []
        }
        for song in SONGS.values():
            for mode in ["S", "D"]:
                if mode in song:
                    level_all[mode].extend(song[mode])

        counts = []
        for mode in ["S", "D"]:
            count = pd.Series(level_all[mode]).value_counts()
            count.name = mode
            counts.append(count)
        songs_info = pd.concat(counts, axis=1).fillna(0).astype(int)
        songs_info = songs_info.loc[10:]

        base = self.get_base(songs_info.index)
        for mode in ["S", "D"]:
            songs_info[f"MAX_{mode}"] = (songs_info[mode] * base * 1.5).astype(int)
        return songs_info

    def calc(self, df, level, mode):
        df = df.query("mode == @mode")
        base = self.get_base(level)
        score = (df["grade"].map(self.COEFFICIENT) * base).round()
        rating = score.sum().astype(int)
        return rating, len(df)

    def result(self, df, level, mode):
        rating, n_clear = self.calc(df, level, mode)
        def get_text(a, b, name):
            return f"{name} : {a} / {b} ({a / b:.1%})"
        t1 = get_text(n_clear, self.songs_info.loc[level, mode], "Clear")
        t2 = get_text(rating, self.songs_info.loc[level, f"MAX_{mode}"], "Rating")
        return t1, t2
