import random

team_selected = "lakers"
player_selected = "lebron"

offense = True
deffense = False

offenseive_plays = ["4:1", "3:2", "5out"]
offense_play = random.choice(offenseive_plays)


def offensive_game_play():
    knicks_players = ["brunson", "melo", "og", "hart", "kat"]
    lakers_players = ["lebron", "kobe", "reeves", "luka", "hachi"]

    random.shuffle(knicks_players)
    random.shuffle(lakers_players)

    matchups = []

    for i in range(5):
        matchup = [knicks_players[i], lakers_players[i], i + 1]
        matchups.append(matchup)

    print("offensive_game_play:")
    print(matchups)
    print(offense_play)


def defensive_game_play():
    print("defensive_game_play")


if offense == True:
    offensive_game_play()
else:
    defensive_game_play()
