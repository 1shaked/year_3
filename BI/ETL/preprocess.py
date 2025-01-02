import pandas as pd
from scipy.stats import f_oneway
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.io as pio
import seaborn as sns
from scipy.stats import pearsonr
import numpy as np
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import json as js
from scipy.stats import gaussian_kde

def determine_result(row):
    if row['goal_home_ft'] > row['goal_away_ft']:
        return 'HW'  # Home Win
    elif row['goal_home_ft'] < row['goal_away_ft']:
        return 'AW'  # Away Win
    else:
        return 'D'   # Draw
def determine_result_excel(row):
    mapping = { 'HW' : 'Home win', 'AW' : 'Away Win', 'D' : 'Draw'}
    v = row['result']
    return mapping[v]
# Set a compatible renderer
alpha = 0.05

df = pd.read_csv('../data/df_full_premierleague.csv')
laliga_df = pd.read_csv('../data/combined_data_laliga_tranform.csv')
df = pd.concat([df, laliga_df], axis=0)
df['result'] = df.apply(determine_result, axis=1)


# Define bins for possession percentage
bins = np.arange(0, 101, 5)  # Create bins from 0% to 100% in increments of 5
df['possession_bin'] = pd.cut(df['home_possession'], bins, right=False)

# Calculate total games and wins for each possession bin
game_data = df.groupby('possession_bin', observed=False).size().reset_index(name='total_games')
win_data = df[df['result'] == 'HW'].groupby('possession_bin').size().reset_index(name='home_wins')

# Merge the two DataFrames
home_win_rate_vs_possession = pd.merge(game_data, win_data, on='possession_bin', how='left')
home_win_rate_vs_possession['home_wins'] = home_win_rate_vs_possession['home_wins'].fillna(0)  # Replace NaN with 0 for bins with no wins

# Calculate the win rate
home_win_rate_vs_possession['win_rate'] = home_win_rate_vs_possession['home_wins'] / home_win_rate_vs_possession['total_games']

# Convert bin intervals to numeric (midpoints) for plotting
home_win_rate_vs_possession['possession_mid'] = home_win_rate_vs_possession['possession_bin'].apply(lambda x: x.mid)

home_win_rate_vs_possession.dropna(subset=['win_rate'], inplace=True)

X = home_win_rate_vs_possession['possession_mid'].values.reshape(-1, 1)  # Reshape for sklearn
y = home_win_rate_vs_possession['win_rate'].values
# Fit a linear regression model
reg_model = LinearRegression()
reg_model.fit(X, y)
home_win_rate_vs_possession['regression_line'] = reg_model.predict(X)
home_win_rate_vs_possession.to_excel('../data/home_win_rate_vs_possession.xlsx', sheet_name='regression')

# shots difference
df['home_shots_diff'] = df['home_shots_on_target'] - df['away_shots_on_target']

# Group by the number of shots
shots_diff_data = df.groupby('home_shots_diff').agg(
    total_games=('result', 'size'),
    wins=('result', lambda x: (x == 'HW').sum())
).reset_index()
shots_diff_data['win_percentage'] = (shots_diff_data['wins'] / shots_diff_data['total_games']) * 100
shots_data_big_only = shots_diff_data[shots_diff_data['total_games'] > 10]

# Prepare the data
X = shots_data_big_only[['home_shots_diff']].values  # Independent variable
y = shots_data_big_only['win_percentage'].values  # Dependent variable
# Initialize and fit the model
reg_model = LinearRegression()
reg_model.fit(X, y)

# Add regression points (predicted values) to the DataFrame
shots_data_big_only['regression_line'] = reg_model.predict(X)
shots_data_big_only.to_excel('../data/shots_diff_vs_win_percentage_tableau.xlsx', sheet_name='shots_diff')



#################
# Create bins of 5 for clearances
bins = range(0, int(df['home_clearances'].max()) + 5, 5)  # Ensure max is an integer
clearance_data_binned = df.copy()

# Bin the clearances into intervals of 5
clearance_data_binned['clearance_bin'] = pd.cut(clearance_data_binned['home_clearances'], bins=bins, right=False)

# Group by clearance bins and calculate win percentage
clearance_data_binned = clearance_data_binned.groupby('clearance_bin').agg(
    total_games=('result', 'size'),
    wins=('result', lambda x: (x == 'HW').sum())
).reset_index()
clearance_data_binned['win_percentage'] = (clearance_data_binned['wins'] / clearance_data_binned['total_games']) * 100

# Convert bin intervals to numeric (midpoints) for plotting
clearance_data_binned['clearance_mid'] = clearance_data_binned['clearance_bin'].apply(lambda x: x.mid)
clearance_data_binned_only_big = clearance_data_binned[clearance_data_binned['total_games'] > 10]
clearance_data_binned_only_big['clearance_mid'] = pd.to_numeric(clearance_data_binned_only_big['clearance_mid'], errors='coerce')
clearance_data_binned_only_big['win_percentage'] = pd.to_numeric(clearance_data_binned_only_big['win_percentage'], errors='coerce')
clearance_data_binned_only_big = clearance_data_binned_only_big.dropna(subset=['clearance_mid', 'win_percentage'])

# Prepare data for regression
X = clearance_data_binned_only_big[['clearance_mid']].values  # Independent variable
y = clearance_data_binned_only_big['win_percentage'].values  # Dependent variable

# Fit the model
reg_model = LinearRegression()
reg_model.fit(X, y)

# Add regression line values to the DataFrame
clearance_data_binned_only_big['regression_line_clearance'] = reg_model.predict(X)
clearance_data_binned_only_big.to_excel('../data/clearance_bins_vs_win_percentage_tableau.xlsx', sheet_name='clearance_bins_vs_win_percentage')
################ 
df['shooting_accuracy_home'] = df.home_shots_on_target / df.home_shots
df['shooting_accuracy_away'] = df.away_shots_on_target / df.away_shots
df.dropna(subset=['shooting_accuracy_home'], inplace=True) # only one row with NaN
df.dropna(subset=['shooting_accuracy_away'], inplace=True) # only one row with NaN
#############


copy_df = df.copy(deep=True)

cols = copy_df.columns
filter_col = list(filter(lambda x: '_avg_' in x or '_acum_' in x or x[0].isupper(), cols))
# copy_df = copy_df[filter_col]
copy_df.drop(columns=[
    *filter_col,
    'Unnamed: 0'
    ,'link_match'
    ,'season'
    ,'home_corners'
    ,'home_shots.1'
    ,'away_corners'
    ,'home_offsides'
    ,'away_shots.1'

], inplace=True)
# copy_df.drop('date')
# copy_df.drop('home_shots.1')


copy_df['result'] = copy_df.apply(determine_result, axis=1)
copy_df.to_excel('../data/df_full_tab.xlsx', index=False, sheet_name='data')


#### mapping team to city
team_location_map = {
    'AFC Bournemouth': {'city': 'Bournemouth', 'country': 'England'},
    'ALAVÉS': {'city': 'Vitoria-Gasteiz', 'country': 'Spain'},
    'ALMERÍA': {'city': 'Almería', 'country': 'Spain'},
    'ATHLETIC': {'city': 'Bilbao', 'country': 'Spain'},
    'ATLETICO MADRID': {'city': 'Madrid', 'country': 'Spain'},
    'Arsenal': {'city': 'London', 'country': 'England'},
    'Aston Villa': {'city': 'Birmingham', 'country': 'England'},
    'BARCELONA': {'city': 'Barcelona', 'country': 'Spain'},
    'Birmingham City': {'city': 'Birmingham', 'country': 'England'},
    'Blackburn Rovers': {'city': 'Blackburn', 'country': 'England'},
    'Blackpool': {'city': 'Blackpool', 'country': 'England'},
    'Bolton Wanderers': {'city': 'Bolton', 'country': 'England'},
    'Brighton and Hove Albion': {'city': 'Brighton', 'country': 'England'},
    'Burnley': {'city': 'Burnley', 'country': 'England'},
    'CELTA': {'city': 'Vigo', 'country': 'Spain'},
    'Cardiff City': {'city': 'Cardiff', 'country': 'Wales'},
    'Chelsea': {'city': 'London', 'country': 'England'},
    'Crystal Palace': {'city': 'London', 'country': 'England'},
    'CÁDIZ CF': {'city': 'Cádiz', 'country': 'Spain'},
    'CÓRDOBA': {'city': 'Córdoba', 'country': 'Spain'},
    'DEPORTIVO': {'city': 'A Coruña', 'country': 'Spain'},
    'EIBAR': {'city': 'Eibar', 'country': 'Spain'},
    'ELCHE': {'city': 'Elche', 'country': 'Spain'},
    'ESPANYOL': {'city': 'Barcelona', 'country': 'Spain'},
    'Everton': {'city': 'Liverpool', 'country': 'England'},
    'Fulham': {'city': 'London', 'country': 'England'},
    'GETAFE': {'city': 'Getafe', 'country': 'Spain'},
    'GIJÓN': {'city': 'Gijón', 'country': 'Spain'},
    'GIRONA': {'city': 'Girona', 'country': 'Spain'},
    'GRANADA': {'city': 'Granada', 'country': 'Spain'},
    'HUESCA': {'city': 'Huesca', 'country': 'Spain'},
    'Huddersfield Town': {'city': 'Huddersfield', 'country': 'England'},
    'Hull City': {'city': 'Hull', 'country': 'England'},
    'LAS PALMAS': {'city': 'Las Palmas', 'country': 'Spain'},
    'LEGANÉS': {'city': 'Leganés', 'country': 'Spain'},
    'LEVANTE': {'city': 'Valencia', 'country': 'Spain'},
    'Leeds United': {'city': 'Leeds', 'country': 'England'},
    'Leicester City': {'city': 'Leicester', 'country': 'England'},
    'Liverpool': {'city': 'Liverpool', 'country': 'England'},
    'MALLORCA': {'city': 'Palma', 'country': 'Spain'},
    'Manchester City': {'city': 'Manchester', 'country': 'England'},
    'Manchester United': {'city': 'Manchester', 'country': 'England'},
    'Middlesbrough': {'city': 'Middlesbrough', 'country': 'England'},
    'MÁLAGA': {'city': 'Málaga', 'country': 'Spain'},
    'Newcastle United': {'city': 'Newcastle upon Tyne', 'country': 'England'},
    'Norwich City': {'city': 'Norwich', 'country': 'England'},
    'OSASUNA': {'city': 'Pamplona', 'country': 'Spain'},
    'Queens Park Rangers': {'city': 'London', 'country': 'England'},
    'RAYO VALLECANO': {'city': 'Madrid', 'country': 'Spain'},
    'REAL BETIS': {'city': 'Seville', 'country': 'Spain'},
    'REAL MADRID': {'city': 'Madrid', 'country': 'Spain'},
    'REAL SOCIEDAD': {'city': 'San Sebastián', 'country': 'Spain'},
    'Reading': {'city': 'Reading', 'country': 'England'},
    'SEVILLA FC': {'city': 'Seville', 'country': 'Spain'},
    'Sheffield United': {'city': 'Sheffield', 'country': 'England'},
    'Southampton': {'city': 'Southampton', 'country': 'England'},
    'Stoke City': {'city': 'Stoke-on-Trent', 'country': 'England'},
    'Sunderland': {'city': 'Sunderland', 'country': 'England'},
    'Swansea City': {'city': 'Swansea', 'country': 'Wales'},
    'Tottenham Hotspur': {'city': 'London', 'country': 'England'},
    'VALENCIA': {'city': 'Valencia', 'country': 'Spain'},
    'VALLADOLID': {'city': 'Valladolid', 'country': 'Spain'},
    'VILLARREAL': {'city': 'Villarreal', 'country': 'Spain'},
    'Watford': {'city': 'Watford', 'country': 'England'},
    'West Bromwich Albion': {'city': 'West Bromwich', 'country': 'England'},
    'West Ham United': {'city': 'London', 'country': 'England'},
    'Wigan Athletic': {'city': 'Wigan', 'country': 'England'},
    'Wolverhampton Wanderers': {'city': 'Wolverhampton', 'country': 'England'},
}
# Convert the dictionary to a DataFrame
df_teams = pd.DataFrame.from_dict(team_location_map, orient='index').reset_index()
df_teams.columns = ['team', 'city', 'country']

df_teams.to_excel('../data/teams_to_location.xlsx', sheet_name='teams')