import io

import pandas as pd
from flask import Flask
from dash import Dash, html, dcc, Output, Input, State, no_update
import jsonpickle

from checklist_maker import ChecklistMaker
from crawling_records import PIURecord


server = Flask(__name__)
app = Dash(__name__, server=server)

app.layout = html.Div([
    html.H1(children="Pump it up Phoenix", style={'textAlign':'center'}, id="title"),
    html.Hr(),
    dcc.Dropdown(["None", "Hypnosis"], "None", id="template"),
    dcc.RadioItems(["Single", "Double"], "Double", id="mode", inline=True),
    dcc.Dropdown(value=23, id="level"),
    html.Button("Load Template", id="run", n_clicks=0),
    html.Hr(),
    html.Div("기록을 불러오려면 PIU 홈페이지 아이디로 로그인하세요.", id="login_text"),
    dcc.Input(placeholder="PIU ID (e-mail)", id="username", type="email"),
    dcc.Input(placeholder="Password", id="password", type="password"),
    dcc.Store(id="login_status", data=False),
    html.Button("Login", id="login", n_clicks=0),
    html.Hr(),
    dcc.RadioItems(["red_slash", "grade", "plate", "score"], "red_slash", id="checker"),
    html.Button("Check Records", id="check", n_clicks=0, style={"display": "none"}),
    html.Hr(),
    dcc.Loading(
            id="loading",
            type="default",
            children=html.Img(id="result", width="100%")
        ),
    dcc.Store(id="piu", data=None),
    dcc.Store(id="selected", data=None),
    dcc.Store(id="records", data=None)
    ])

@app.callback(
    Output("login_text", "children"),
    Output("login", "n_clicks"),
    Output("piu", "data"),
    Output("username", "style"),
    Output("password", "style"),
    Output("login", "style"),
    Output("check", "style"),
    Output("login_status", "data"),
    Output("username", "value"),
    Output("password", "value"),
    Input("login", "n_clicks"),
    State("username", "value"),
    State("password", "value"),
    State("piu", "data")
    )
def piu_login(login, username, password, piu):
    if login > 0:
        if piu is None:
            piu = PIURecord()
        else:
            piu = jsonpickle.decode(piu)
        result = piu.login(username, password)
        piu = jsonpickle.encode(piu)
        if result:
            print(result)
            none = {"display": "none"}
            return result, 0, piu, none, none, none, None, True, "", ""
        else:
            error_text = "(오류) 아이디 혹은 비밀번호를 다시 확인해주세요."
            return [error_text, 0, piu] + [no_update] * 7
    else:
        return [no_update] * 10

@app.callback(
    Output("level", "options"),
    Input("template", "value"),
    Input("mode", "value"),
    )
def update_levels(template, mode):
    if template == "None":
        if mode == "Single":
            options = list(range(10, 27))
        else:
            options = list(range(10, 29))
    else:
        if mode == "Single":
            options = []
        else:
            options = [23, 24]
    return options

@app.callback(
    Output("result", "src"),
    Output("run", "n_clicks"),
    Output("check", "n_clicks"),
    Output("selected", "data"),
    Output("records", "data"),
    Input("run", "n_clicks"),
    Input("check", "n_clicks"),
    State("template", "value"),
    State("mode", "value"),
    State("level", "value"),
    State("checker", "value"),
    State("piu", "data"),
    State("selected", "data"),
    State("records", "data"),
    State("login_status", "data"),
    )
def update_template(click_run, click_check, template, mode, level, checker, piu, checklist, records, login_status):
    if click_run > 0:
        if template == "Hypnosis":
            template = f"hypnosis_{mode[0].lower()}{str(level)}"
        else:
            template = None
        checklist = ChecklistMaker().make(mode=mode[0], level=level, template=template)
        img = checklist.image
        checklist = jsonpickle.encode(checklist)
        return img, 0, no_update, checklist, None
    elif click_check > 0:
        if (not login_status) or (checklist is None):
            return no_update, no_update, 0, no_update, no_update
        checklist = jsonpickle.decode(checklist)
        if records is None:
            piu = jsonpickle.decode(piu)
            records = piu.parse_best_score(level=checklist.level)
        else:
            records = pd.read_json(io.StringIO(records))
        checklist.set_records(records)
        img = checklist.check(checker=checker)
        records = records.to_json()
        return img, no_update, 0, no_update, records
    else:
        return [no_update] * 5


if __name__ == '__main__':
    server.run("0.0.0.0", port=5000)
