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
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.title = "Job Finder"

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H4("💪 Your skills:"),
            html.Div(id="badge-container"),

            html.Hr(),

            html.H5("What's more? Click to add:"),
            dcc.Dropdown(
                id="skill-dropdown",
                options=[{"label": s, "value": s} for s in all_skills],
                placeholder="Choose a skill",
                clearable=False
            ),
            dcc.Store(id="selected-skills", data=[]),
        ], width=3, style={"backgroundColor": "#2e2e2e", "margin": "1rem"}),

        dbc.Col([
            html.H1("🔍 Interactive Job Report"),
            html.H4(id="found-count"),
            dash_table.DataTable(
                id="offers-table",
                columns=[
                    {"name":"Title","id":"Job Title"},
                    {"name":"Company","id":"Company"},
                    {"name":"Location","id":"Location"},
                    {"name":"Score","id":"match_score"}
                ],
                data=[],
                page_size=10,
                style_header={"fontWeight":"bold"},
                style_cell={"textAlign":"left"},
            )
        ], width=9)
    ], style={"height": "100vh"})  # Set row height to full viewport height
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
                id={"type":"remove-btn", "index":s},
                className="skill-badge"
            )
        )

    # 2) Filtrowanie i punktacja
    df2 = df.copy()
    df2["match_score"] = df2["skills_list"].apply(lambda row: match_score(skills, row))
    filtered = df2[df2["match_score"] > 0].sort_values("match_score", ascending=False)
    data = filtered[["ID","Job Title","Company","Location","match_score"]].to_dict("records")

    return badges, data, f"Found {len(filtered)} matching offers"


if __name__ == "__main__":
    app.run(debug=True, dev_tools_hot_reload=True)