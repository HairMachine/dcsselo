import time
import re
import data

def server_name(url):
    if "akrasiac" in url:
        return "CAO"
    if "underhound" in url:
        return "CUE"
    if "berotato" in url:
        return "CBRO"
    if "xtahua" in url:
        return "CXC"
    if "project357" in url:
        return "CPO"
    if "kelbi" in url:
        return "CKO"
    if "webzook" in url:
        return "CWZ"
    

# Split a log file into its constituent lines
def log_to_lines(filename):
    with open(filename) as file:
        fc = file.read()
        lines = fc.splitlines()
    return lines

# Produce a game data dictionary from a particular log line
def parse_game_data(logline, server):
    gameData = {}
    fields = re.split('(?<!:):(?!:)', logline)
    for f in fields:
        keyval = f.split("=")
        if len(keyval) > 1:
            gameData[keyval[0]] = keyval[1]
    # Add winner information
    if "ktyp" in gameData and gameData["ktyp"] == "winning":
        gameData["winner"] = 1
    else:
        gameData["winner"] = 0
    # Map draconian colours
    if "Draconian" in gameData["race"]:
        gameData["race"] = "Draconian"
    return gameData

def get_player_base_elo(gd, ed):
    # Get player elo
    if gd["name"] in ed["players"]:
        return ed["players"][gd["name"]]
    else:
        return 1000

def elo_adjust(p1, p2, k, win):
    P = (1.0 / (1.0 + (10.0 ** ((p2 - p1) / 400))))
    return p1 + k * (win - P)

# Calculate the elo adjustment for each factor and the player
def elo_calculate(gd, ed, factors):
    player_base_elo = get_player_base_elo(gd, ed)
    # Do elo calcs
    target_elo = 0
    for fk in factors:
        factor = factors[fk]
        field_str = ""
        for field in factor["fields"]:
            field_str += gd[field]
        if field_str in ed[fk]:
            target_elo = ed[fk][field_str]
        else:
            target_elo = factor["base"]
        # Player adjust
        ed["players"][gd["name"]] = elo_adjust(player_base_elo, target_elo, factor["K"], gd["winner"])
        # Factor adjust (using originally calculated base elo)
        ed[fk][field_str] = elo_adjust(target_elo, player_base_elo, factor["K"], abs(gd["winner"] - 1))

# Special function for adjusting a player's elo based on the number of runes they achieved.
# This is basically assuming the the player players 15 simultaneous games, 1 against each rune.
def rune_elo_calculate(gd, ed):
    player_base_elo = get_player_base_elo(gd, ed)
    if "nrune" in gd:
        runes = int(gd["nrune"])
    else:
        runes = 0
    for r in range(1, 16): # The range is exclusive apparently - Pythonism
        target_elo = 2000
        if str(r) in ed["runes"]:
            target_elo = ed["runes"][str(r)]
        if r <= runes:
            # player wins
            ed["players"][gd["name"]] = elo_adjust(player_base_elo, target_elo, 10, 1)
            ed["runes"][str(r)] = elo_adjust(target_elo, player_base_elo, 5, 0)
        else:
            # player loses
            ed["players"][gd["name"]] = elo_adjust(player_base_elo, target_elo, 5, 0)
            ed["runes"][str(r)] = elo_adjust(target_elo, player_base_elo, 10, 1)

def write_csv(name, data):
    f = open("output/" + name, "w")
    for d in data:
        if data[d] > 2000:
            rank = "Grand Master"
        elif data[d] > 1800:
            rank = "Master"
        elif data[d] > 1600:
            rank = "Diamond"
        elif data[d] > 1400:
            rank = "Platinum"
        elif data[d] > 1200:
            rank = "Gold"
        elif data[d] > 1000:
            rank = "Silver"
        else:
            rank = "Bronze"
        f.write(d + "," + str(round(data[d])) + "," + rank + "\n" )
    f.close()

# Set up data
logs = []

elo_data = {
    "players": {},
    "backgrounds": {},
    "species": {},
    "combos": {},
    "runes": {}
}

elo_factors = {
    "species": {
        "K": 40,
        "fields": ["race"],
        "base": 2000
    },
    "backgrounds": {
        "K": 40,
        "fields": ["cls"],
        "base": 2000
    },
    "combos": {
        "K": 40,
        "fields": ["race", "cls"],
        "base": 3000
    }
}

# Main loop
start = time.clock()
print "Populating log data from files..."
for url in data.log_urls:
    logs.append({"server": server_name(url), "file": data.filename_from_url(url)})
print "Processing elos..."
for log in logs:
    for line in log_to_lines(log["file"]):
        game_data = parse_game_data(line, log["server"])
        elo_calculate(game_data, elo_data, elo_factors)
        rune_elo_calculate(game_data, elo_data)
length = time.clock() - start
print "Processing finished, took " + str(length)
# Write files
print "Writing CSVs..."
write_csv("players.csv", elo_data["players"])
for fk in elo_factors:
    write_csv(fk + ".csv", elo_data[fk])
write_csv("runes.csv", elo_data["runes"])
print "Done!"

