import dash
from dash import html, dcc, dash_table, Input, Output, State
import pandas as pd
import dash_bootstrap_components as dbc
import json
from dash.dependencies import ALL

# --- data load & helpery ---
CSV_PATH = "justjoinit_offers.csv"

def load_data(path):
    df = pd.read_csv(path)
    df['skills_list'] = df['Tech Stack'].fillna('').apply(
        lambda s: [e.split(':')[0].strip() for e in s.split(';') if ':' in e]
    )
    return df

def match_score(selected, row_skills):
    if not row_skills: return 0.0
    cnt = len(set(selected) & set(row_skills))
    return cnt + round(cnt/len(row_skills), 2)

df = load_data(CSV_PATH)
all_skills = sorted({skill for skills in df['skills_list'] for skill in skills})

# --- Dash app setup ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
with open("assets/index_template.html", "r") as f:
    app.index_string = f.read()
    
app.title = "Aligno"

app.layout = dbc.Container([
    # Row 1: Header
    dbc.Row([
        dbc.Col([
            html.H1("🔎 Aligno"),
            html.H4([
                html.Em("Search smarter.")
            ])
        ], className="header")
    ]),
    
    # Row 2: Main Content
    dbc.Row([
        # Left Column: Filters
        dbc.Col([
            html.Div(className="content-box", children=[
                html.H4("Your skills. Your preferences."),
                html.Div(id="badge-container"),
                html.Hr(),
                html.H5("Add a skill:"),
                dcc.Dropdown(
                    id="skill-dropdown",
                    options=[{"label": s, "value": s} for s in all_skills],
                    placeholder="Choose a skill",
                    clearable=False
                ),
                dcc.Store(id="selected-skills", data=[])
            ])
        ], width=4),

        # Right Column: Job Offers
        dbc.Col([
            html.Div(className="content-box", children=[
                html.H4("Your next job."),
                html.H5(id="found-count"),
                dash_table.DataTable(
                    id="offers-table",
                    columns=[
                        {"name": "Title", "id": "Job Title"},
                        {"name": "Company", "id": "Company"},
                        {"name": "Location", "id": "Location"},
                        {"name": "Score", "id": "match_score"}
                    ],
                    data=[],
                    # pagination removed
                    style_header={"fontWeight": "bold"},
                    style_cell={"textAlign": "left"}
                )
            ])
        ], width=8)
    ])
], fluid=True)


# --- Callback: add or remove skills ---
@app.callback(
    Output("selected-skills", "data"),
    Input("skill-dropdown", "value"),
    Input({"type":"remove-btn", "index": ALL}, "n_clicks"),
    State("selected-skills", "data"),
    prevent_initial_call=True
)
def update_selected(chosen_skill, remove_clicks, current):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    trigger = ctx.triggered[0]["prop_id"]
    # adding a skill
    if "skill-dropdown.value" in trigger:
        if chosen_skill and chosen_skill not in current:
            return current + [chosen_skill]
        return current
    # removing a skill
    else:
        btn_id = trigger.split(".")[0]
        skill_to_remove = json.loads(btn_id)["index"]
        return [s for s in current if s != skill_to_remove]

# --- Callback: render badge'y & filtr i tabela ---
@app.callback(
    Output("badge-container", "children"),
    Output("offers-table", "data"),
    Output("found-count", "children"),
    Input("selected-skills", "data")
)
def update_report(skills):
    badges = []
    for s in skills:
        badges.append(
            dbc.Button(
                f"{s}",
                id={"type": "remove-btn", "index": s},
                className="skill-badge"
            )
        )

    # Filtrowanie danych
    filtered = df.copy()
    if skills:
        filtered["match_score"] = df["skills_list"].apply(lambda row: match_score(skills, row))
        filtered = filtered[filtered["match_score"] > 0]
        filtered = filtered.sort_values(by="match_score", ascending=False)
    else:
        filtered["match_score"] = 0
        filtered = filtered.head(0)

    # Przygotowanie danych do tabeli
    offers_data = filtered[["Job Title", "Company", "Location", "match_score"]].to_dict("records")

    # Tekst o liczbie dopasowań
    found_text = f"{len(filtered)} matches found" if skills else "No skills selected"

    return badges, offers_data, found_text

if __name__ == "__main__":
    app.run(debug=True, dev_tools_hot_reload=True)