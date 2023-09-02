from itertools import chain
import pandas as pd
import requests
import time

from bs4 import BeautifulSoup


class PIURecord:
    LOGIN_URL = "https://piugame.com/bbs/login_check.php"
    SCORE_URL = "https://piugame.com/my_page/my_best_score.php"

    def __init__(self):
        self.session = self._open_session()

    def __del__(self):
        self.session.close()

    def _open_session(self):
        session = requests.Session()
        session.post(self.LOGIN_URL)
        return session
    
    def login(self, username, password):
        login_data = {
            'mb_id': username,
            'mb_password': password
        }
        response = self.session.post(self.LOGIN_URL, data=login_data)
        soup = BeautifulSoup(response.text, "html.parser")
        result = soup.select("div.txtw")
        if len(result) == 0:
            return False
        else:
            return result[0].text.replace("\r", "").replace("\n", "").replace("\t", "")

    def _parse_song_content(self, content):
        title = content.text.replace("\n", "")
        return title

    def _parse_level_content(self, content):
        level = ""
        for splitter, img in zip(("/", "_", "_"), content.select("img")):
            level += img.get("src").split(splitter)[-1][0].upper()
        mode = level[0]
        level = int(level[1:])
        return mode, level

    def _parse_etc_content(self, content):
        score = int(content.text.replace("\n", "").replace(",", ""))
        grade, plate = [
            item.get("src").split("/")[-1].split(".")[0].upper()
            for item in content.select("img")
        ]
        return score, grade, plate

    def _parse_contents(self, contents, ctype):
        parsing_method = getattr(self, f"_parse_{ctype}_content")
        result = [parsing_method(content) for content in contents]
        return result

    def parse_best_score(self, level=None):
        page = 1
        ctypes = {
            "song": ["title"],
            "level": ["mode", "level"],
            "etc": ["score", "grade", "plate"]
        }
        params = {}
        if level is not None:
            params.update(lv=level)
        result = {ctype: [] for ctype in ctypes}
        while page < 100:
            params.update(page=page)
            response = self.session.get(self.SCORE_URL, params=params)
            if page != int(response.url.split("=")[-1]):
                break
            soup = BeautifulSoup(response.text, "html.parser")
            for ctype in ctypes:
                contents = soup.select(f"div.{ctype}_con")
                result[ctype].append(self._parse_contents(contents, ctype))
            page += 1
        if page == 100:
            raise Exception("Something went wrong")

        dfs = [self._lol_to_df(result[ctype], cols) for ctype, cols in ctypes.items()]
        result = pd.concat(dfs, axis=1)

        return result

    def _lol_to_df(self, list_of_lists, cols):
        df = pd.DataFrame(chain.from_iterable(list_of_lists), columns=cols)
        return df
