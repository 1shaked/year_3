from fastapi import FastAPI
from typing import Dict, Tuple
from pydantic import BaseModel

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}




def calculate_shapely_value(N, v):
    import numpy as np
    from itertools import combinations

    players = list(N)
    n = len(players)
    factorial = np.math.factorial

    def marginal_contribution(S, i):
        S_with_i = tuple(sorted(S + (i,)))
        S_without_i = tuple(sorted(S))
        return v.get(S_with_i, 0) - v.get(S_without_i, 0)

    shapely_values = {i: 0 for i in players}

    for i in players:
        for S in combinations(players, len(players) - 1):
            if i not in S:
                S = tuple(sorted(S))
                weight = factorial(len(S)) * factorial(n - len(S) - 1) / factorial(n)
                shapely_values[i] += weight * marginal_contribution(S, i)

    return shapely_values


class GameData(BaseModel):
    v: Dict[str, float]

# input of { (string , string , string) , number }
@app.post("/shapely_value")
async def shapely_value(game_data: GameData):
    # Extract the players from the keys of the characteristic function
    game = gameDataGetPlayersSet(game_data.v)
    # Calculate the Shapley values
    shapely_values = calculate_shapely_value(game['players'], game['game'])
    
    # calculate_shapely_value(game_data.v.keys(), game_data.v)
    # return {"shapely_values": shapely_values}
    print(game)
    print('-'*100)
    print(shapely_values)
    return shapely_values

def gameDataGetPlayersSet(game_data: Dict[str, float]):
    keys_game = game_data.keys() # the format is [p1,p2] etc
    players = set() 
    game = dict()
    for key in keys_game:
        # remove the first and last char
        key_shorted = key[1:-1]
        if (key_shorted == ""):
            game[()] = 0
            continue
        # split by the , in the string
        key_spited = key_shorted.split(',')
        for player in key_spited:
            players.add(player)
        print(tuple(sorted(key_spited)))

        game[tuple(sorted(key_spited))] = game_data[key]
    return {"players" :players, "game": game}

