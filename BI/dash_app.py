import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.io as pio
import os

def get_graph(file):
    with open(f'graphs/{file}.json') as f:
        content = f.read()
    # json_data = js.loads(content)
    fig = pio.from_json(content)
    return fig

# # Sample Data
# world_cup = pd.read_csv('data/matches_world_cup.csv')
# english_league = pd.read_csv('data/df_full_premierleague.csv')
# df = pd.concat([world_cup, english_league], axis=0)


# def determine_result(row):
#     if row['goal_home_ft'] > row['goal_away_ft']:
#         return 'HW'  # Home Win
#     elif row['goal_home_ft'] < row['goal_away_ft']:
#         return 'AW'  # Away Win
#     else:
#         return 'D'   # Draw

# # Apply the function to each row
# df['result'] = df.apply(determine_result, axis=1)


math_result_distribution = get_graph('match_result_distribution')
total_fouls_vs_goal_diff = get_graph('total_fouls_vs_goal_diff')
home_win_rate_vs_possession = get_graph('home_win_rate_vs_possession')
shots_vs_win_percentage = get_graph('shots_vs_win_percentage')
shots_diff_vs_win_percentage = get_graph('shots_diff_vs_win_percentage')
clearance_bins_vs_win_percentage = get_graph('clearance_bins_vs_win_percentage')
visualization_with_regression_plane_3d_scatter = get_graph('visualization_with_regression_plane_3d_scatter')
# Initialize Dash App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# App Layout
app.layout = html.Div([
    dbc.Row([
        dbc.Col(
            dcc.Graph(figure=math_result_distribution),
            xs=12, sm=12, md=6, lg=6, xl=6  # Full width on small screens, half width on medium and larger
        ),
        dbc.Col(
            dcc.Graph(figure=total_fouls_vs_goal_diff),
            xs=12, sm=12, md=6, lg=6, xl=6
        ),
        dbc.Col(
            dcc.Graph(figure=home_win_rate_vs_possession),
            xs=12, sm=12, md=6, lg=6, xl=6
        ),
        dbc.Col(
            dcc.Graph(figure=shots_vs_win_percentage),
            xs=12, sm=12, md=6, lg=6, xl=6
        ),
        dbc.Col(
            dcc.Graph(figure=shots_diff_vs_win_percentage),
            xs=12, sm=12, md=6, lg=6, xl=6
        ),
        dbc.Col(
            dcc.Graph(figure=clearance_bins_vs_win_percentage),
            xs=12, sm=12, md=6, lg=6, xl=6
        ),
    ])
])


# Run the App
if __name__ == "__main__":
    # Get the port from the environment variable (default to 8050 if not set)
    port = int(os.environ.get("PORT", 8050))
    app.run_server(host="0.0.0.0", port=port, debug=True)