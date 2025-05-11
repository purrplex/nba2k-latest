import random

team_selected = "lakers"
player_selected = "lebron"

offense = True
deffense = False

offense_plays = ["41", "32", "5out"]

offense_play_picked = random.choice(offense_plays)


coordmap_offense = {}
coordmap_defense ={}

coordinates_41 = [(100,100), (200,200),(300,00), (400,400), (500,800)]
coordinates_32 = [(100,100), (200,200),(300,00), (400,400), (500,800)]
coordinates_5out = [(100,100), (200,200),(300,00), (400,400), (500,800)]


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
    print(offense_play_picked)


    if offense_play_picked == "41":
        offensive_coordinates = coordinates_41
    if offense_play_picked == "32":
        offensive_coordinates = coordinates_32
    if offense_play_picked == "5out":
        offensive_coordinates = coordinates_5out

    
    for i in range(5):
        coordmap_offense.update({knicks_players[i]: offensive_coordinates[i]})

    for i in range(5):
        coordmap_defense.update({lakers_players[i]: (offensive_coordinates[i][0] + 10, offensive_coordinates[i][1] + 10 )})    

    print(coordmap_offense)
    print(coordmap_defense)


def defensive_game_play():
    print("defensive_game_play")


if offense == True:
    offensive_game_play()
else:
    defensive_game_play()