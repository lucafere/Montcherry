from flask import Flask, render_template, request, jsonify
import json, copy

app = Flask(__name__)

INDUSTRIES = {
    "fishing":    {"name": "Fishing",    "emoji": "🎣", "color": "#0077b6"},
    "hotelery":   {"name": "Hotelery",   "emoji": "🏨", "color": "#8338ec"},
    "tourism":    {"name": "Tourism",    "emoji": "✈️",  "color": "#f77f00"},
    "restaurants":{"name": "Restaurants","emoji": "🍽️", "color": "#d62828"},
}

DEFAULT_STATE = {
    "growth": 0,
    "inflation": 100,
    "unemployment": 100,
    "money": 1500,
    "advantage_cards": [],
    "properties": [],
    "active": True,
    "round": 0,
}

GOALS = {"growth": 100, "inflation": 5, "unemployment": 5}

# Wild card decks
DEMAND_SHOCKS = [
    {"id":"d1","type":"demand","valence":"good","title":"Tourism Boom","desc":"A viral travel trend floods the region. All players: +8 Growth, -5 Unemployment.","effects":{"growth":8,"unemployment":-5}},
    {"id":"d2","type":"demand","valence":"good","title":"Export Surge","desc":"International demand for local goods spikes. +10 Growth, -3 Unemployment.","effects":{"growth":10,"unemployment":-3}},
    {"id":"d3","type":"demand","valence":"good","title":"Wage Increase","desc":"Workers have more to spend. +6 Growth, +5 Inflation.","effects":{"growth":6,"inflation":5}},
    {"id":"d4","type":"demand","valence":"good","title":"Infrastructure Deal","desc":"Gov't investment boosts productivity. +12 Growth, -4 Unemployment.","effects":{"growth":12,"unemployment":-4}},
    {"id":"d5","type":"demand","valence":"good","title":"Consumer Confidence High","desc":"People are spending freely. +7 Growth, +3 Inflation.","effects":{"growth":7,"inflation":3}},
    {"id":"d6","type":"demand","valence":"bad","title":"Recession Warning","desc":"Consumer spending collapses. -10 Growth, +10 Unemployment.","effects":{"growth":-10,"unemployment":10}},
    {"id":"d7","type":"demand","valence":"bad","title":"Import Flood","desc":"Cheap foreign goods undercut local producers. -8 Growth, +8 Unemployment.","effects":{"growth":-8,"unemployment":8}},
    {"id":"d8","type":"demand","valence":"bad","title":"Tax Hike","desc":"New taxes reduce disposable income. -6 Growth, +5 Unemployment.","effects":{"growth":-6,"unemployment":5}},
    {"id":"d9","type":"demand","valence":"bad","title":"Credit Crunch","desc":"Banks tighten lending. -9 Growth, +6 Unemployment.","effects":{"growth":-9,"unemployment":6}},
    {"id":"d10","type":"demand","valence":"bad","title":"Currency Crisis","desc":"Local currency loses value. -7 Growth, +15 Inflation.","effects":{"growth":-7,"inflation":15}},
]

SUPPLY_SHOCKS = [
    {"id":"s1","type":"supply","valence":"good","title":"Tech Innovation","desc":"New tech cuts production costs. +9 Growth, -8 Inflation.","effects":{"growth":9,"inflation":-8}},
    {"id":"s2","type":"supply","valence":"good","title":"Energy Price Drop","desc":"Cheaper energy lowers costs. +6 Growth, -10 Inflation.","effects":{"growth":6,"inflation":-10}},
    {"id":"s3","type":"supply","valence":"good","title":"Trade Agreement","desc":"Lower tariffs open new markets. +8 Growth, -5 Inflation.","effects":{"growth":8,"inflation":-5}},
    {"id":"s4","type":"supply","valence":"good","title":"Labor Productivity Surge","desc":"Workers produce more. +7 Growth, -4 Inflation.","effects":{"growth":7,"inflation":-4}},
    {"id":"s5","type":"supply","valence":"good","title":"Raw Materials Surplus","desc":"Abundant supplies cut input costs. +5 Growth, -7 Inflation.","effects":{"growth":5,"inflation":-7}},
    {"id":"s6","type":"supply","valence":"bad","title":"Oil Price Spike","desc":"Energy costs soar. -8 Growth, +12 Inflation.","effects":{"growth":-8,"inflation":12}},
    {"id":"s7","type":"supply","valence":"bad","title":"Natural Disaster","desc":"Production capacity destroyed. -12 Growth, +10 Inflation.","effects":{"growth":-12,"inflation":10}},
    {"id":"s8","type":"supply","valence":"bad","title":"Worker Strike","desc":"Major strike halts production. -10 Growth, +8 Unemployment.","effects":{"growth":-10,"unemployment":8}},
    {"id":"s9","type":"supply","valence":"bad","title":"Supply Chain Collapse","desc":"Inputs unavailable, costs skyrocket. -9 Growth, +14 Inflation.","effects":{"growth":-9,"inflation":14}},
    {"id":"s10","type":"supply","valence":"bad","title":"Drought","desc":"Agricultural output crashes. -7 Growth, +10 Inflation.","effects":{"growth":-7,"inflation":10}},
]

ADVANTAGE_CARDS = [
    {"id":"a1","title":"Unemployment Shield","desc":"Save and use to block ONE unemployment increase this game.","effect_type":"block","stat":"unemployment","direction":"increase"},
    {"id":"a2","title":"Inflation Hedge","desc":"Save and use to block ONE inflation increase this game.","effect_type":"block","stat":"inflation","direction":"increase"},
    {"id":"a3","title":"Growth Boost","desc":"Save and play at any time: +10 Growth instantly.","effect_type":"instant","effects":{"growth":10}},
    {"id":"a4","title":"Recession Proof","desc":"Save and use to ignore the next negative demand shock that hits you.","effect_type":"block","stat":"demand_shock","direction":"bad"},
    {"id":"a5","title":"Subsidized Loan","desc":"Save and play at any time: gain $200.","effect_type":"money","amount":200},
    {"id":"a6","title":"Price Controls","desc":"Save and use to cap inflation: set your inflation to 20 if it's above 20.","effect_type":"cap","stat":"inflation","value":20},
    {"id":"a7","title":"Job Creation Program","desc":"Save and play anytime: -15 Unemployment.","effect_type":"instant","effects":{"unemployment":-15}},
    {"id":"a8","title":"Market Monopoly","desc":"Save and use to steal $100 from any one opponent.","effect_type":"steal","amount":100},
    {"id":"a9","title":"Government Bailout","desc":"Save and use to negate a growth loss that would drop you below 0.","effect_type":"floor","stat":"growth","value":0},
    {"id":"a10","title":"Productivity Miracle","desc":"Save and play: +8 Growth, -5 Inflation, -5 Unemployment.","effect_type":"instant","effects":{"growth":8,"inflation":-5,"unemployment":-5}},
]

PROPERTIES = [
    {"id":"p1","name":"Fishing Docks","cost":120,"industry_bonus":"fishing","effects":{"growth":5,"unemployment":-3},"desc":"+5 Growth, -3 Unemployment"},
    {"id":"p2","name":"Deep Sea Fleet","cost":200,"industry_bonus":"fishing","effects":{"growth":8,"unemployment":-5},"desc":"+8 Growth, -5 Unemployment"},
    {"id":"p3","name":"Fish Processing Plant","cost":160,"industry_bonus":"fishing","effects":{"growth":6,"inflation":-3},"desc":"+6 Growth, -3 Inflation"},
    {"id":"p4","name":"Budget Hotel","cost":140,"industry_bonus":"hotelery","effects":{"growth":5,"unemployment":-4},"desc":"+5 Growth, -4 Unemployment"},
    {"id":"p5","name":"Luxury Resort","cost":300,"industry_bonus":"hotelery","effects":{"growth":12,"inflation":-5},"desc":"+12 Growth, -5 Inflation"},
    {"id":"p6","name":"Hotel Chain HQ","cost":250,"industry_bonus":"hotelery","effects":{"growth":10,"unemployment":-6},"desc":"+10 Growth, -6 Unemployment"},
    {"id":"p7","name":"Airport Hub","cost":220,"industry_bonus":"tourism","effects":{"growth":9,"unemployment":-5},"desc":"+9 Growth, -5 Unemployment"},
    {"id":"p8","name":"Tour Operator License","cost":180,"industry_bonus":"tourism","effects":{"growth":7,"inflation":-4},"desc":"+7 Growth, -4 Inflation"},
    {"id":"p9","name":"Cruise Terminal","cost":260,"industry_bonus":"tourism","effects":{"growth":11,"unemployment":-7},"desc":"+11 Growth, -7 Unemployment"},
    {"id":"p10","name":"Street Food Market","cost":100,"industry_bonus":"restaurants","effects":{"growth":4,"unemployment":-4},"desc":"+4 Growth, -4 Unemployment"},
    {"id":"p11","name":"Fine Dining Chain","cost":240,"industry_bonus":"restaurants","effects":{"growth":10,"inflation":-6},"desc":"+10 Growth, -6 Inflation"},
    {"id":"p12","name":"Food Delivery Network","cost":190,"industry_bonus":"restaurants","effects":{"growth":8,"unemployment":-5},"desc":"+8 Growth, -5 Unemployment"},
    {"id":"p13","name":"National Bank Branch","cost":280,"effects":{"growth":7,"inflation":-8},"desc":"+7 Growth, -8 Inflation"},
    {"id":"p14","name":"Trade Port","cost":310,"effects":{"growth":12,"unemployment":-8},"desc":"+12 Growth, -8 Unemployment"},
    {"id":"p15","name":"Tech Park","cost":350,"effects":{"growth":15,"inflation":-5,"unemployment":-5},"desc":"+15 Growth, -5 Inflation, -5 Unemployment"},
    {"id":"p16","name":"Power Plant","cost":200,"effects":{"growth":8,"inflation":-6},"desc":"+8 Growth, -6 Inflation"},
    {"id":"p17","name":"University","cost":230,"effects":{"growth":9,"unemployment":-9},"desc":"+9 Growth, -9 Unemployment"},
    {"id":"p18","name":"Central Market","cost":170,"effects":{"growth":6,"inflation":-5,"unemployment":-3},"desc":"+6 Growth, -5 Inflation, -3 Unemployment"},
]

# Game state (in-memory; resets on server restart)
game_state = {
    ind: copy.deepcopy(DEFAULT_STATE) for ind in INDUSTRIES
}
game_log = []

def clamp(val, lo=0, hi=200):
    return max(lo, min(hi, val))

def check_winner(ind):
    s = game_state[ind]
    return (s["growth"] >= GOALS["growth"] and
            s["inflation"] <= GOALS["inflation"] and
            s["unemployment"] <= GOALS["unemployment"])

@app.route("/")
def index():
    return render_template("index.html",
        industries=INDUSTRIES,
        goals=GOALS,
        properties=PROPERTIES,
        demand_shocks=DEMAND_SHOCKS,
        supply_shocks=SUPPLY_SHOCKS,
        advantage_cards=ADVANTAGE_CARDS,
    )

@app.route("/state")
def get_state():
    winners = [ind for ind in INDUSTRIES if check_winner(ind)]
    return jsonify({"state": game_state, "log": game_log[-20:], "winners": winners})

@app.route("/apply_shock", methods=["POST"])
def apply_shock():
    data = request.json
    card_id = data.get("card_id")
    targets = data.get("targets", list(INDUSTRIES.keys()))  # list of industries affected

    card = next((c for c in DEMAND_SHOCKS + SUPPLY_SHOCKS if c["id"] == card_id), None)
    if not card:
        return jsonify({"error": "Card not found"}), 404

    for ind in targets:
        if ind in game_state:
            for stat, delta in card["effects"].items():
                game_state[ind][stat] = clamp(game_state[ind][stat] + delta)

    log_entry = f"[SHOCK] '{card['title']}' affected: {', '.join(targets)}"
    game_log.append(log_entry)
    return jsonify({"ok": True, "log": log_entry})

@app.route("/buy_property", methods=["POST"])
def buy_property():
    data = request.json
    ind = data.get("industry")
    prop_id = data.get("property_id")

    prop = next((p for p in PROPERTIES if p["id"] == prop_id), None)
    if not prop or ind not in game_state:
        return jsonify({"error": "Invalid"}), 400

    player = game_state[ind]
    if player["money"] < prop["cost"]:
        return jsonify({"error": "Not enough money"}), 400
    if prop_id in player["properties"]:
        return jsonify({"error": "Already owned"}), 400

    player["money"] -= prop["cost"]
    player["properties"].append(prop_id)
    for stat, delta in prop["effects"].items():
        player[stat] = clamp(player[stat] + delta)

    log_entry = f"[BUY] {INDUSTRIES[ind]['name']} bought '{prop['name']}' for ${prop['cost']}"
    game_log.append(log_entry)
    return jsonify({"ok": True, "log": log_entry})

@app.route("/draw_advantage", methods=["POST"])
def draw_advantage():
    data = request.json
    ind = data.get("industry")
    card_id = data.get("card_id")

    card = next((c for c in ADVANTAGE_CARDS if c["id"] == card_id), None)
    if not card or ind not in game_state:
        return jsonify({"error": "Invalid"}), 400

    game_state[ind]["advantage_cards"].append(card_id)
    log_entry = f"[ADVANTAGE] {INDUSTRIES[ind]['name']} drew an advantage card (secret)"
    game_log.append(log_entry)
    return jsonify({"ok": True, "card": card, "log": log_entry})

@app.route("/use_advantage", methods=["POST"])
def use_advantage():
    data = request.json
    ind = data.get("industry")
    card_id = data.get("card_id")
    target = data.get("target", ind)  # for steal card

    card = next((c for c in ADVANTAGE_CARDS if c["id"] == card_id), None)
    player = game_state.get(ind)
    if not card or not player or card_id not in player["advantage_cards"]:
        return jsonify({"error": "Invalid"}), 400

    player["advantage_cards"].remove(card_id)
    result = ""

    if card["effect_type"] == "instant":
        for stat, delta in card["effects"].items():
            player[stat] = clamp(player[stat] + delta)
        result = f"Applied: {card['desc']}"

    elif card["effect_type"] == "money":
        player["money"] += card["amount"]
        result = f"Gained ${card['amount']}"

    elif card["effect_type"] == "cap":
        stat = card["stat"]
        if player[stat] > card["value"]:
            player[stat] = card["value"]
        result = f"{stat} capped at {card['value']}"

    elif card["effect_type"] == "steal":
        if target in game_state and target != ind:
            amt = min(card["amount"], game_state[target]["money"])
            game_state[target]["money"] -= amt
            player["money"] += amt
            result = f"Stole ${amt} from {INDUSTRIES[target]['name']}"

    log_entry = f"[ADVANTAGE USED] {INDUSTRIES[ind]['name']} played '{card['title']}': {result}"
    game_log.append(log_entry)
    return jsonify({"ok": True, "log": log_entry})

@app.route("/manual_adjust", methods=["POST"])
def manual_adjust():
    data = request.json
    ind = data.get("industry")
    stat = data.get("stat")
    delta = int(data.get("delta", 0))

    if ind not in game_state or stat not in ["growth","inflation","unemployment","money"]:
        return jsonify({"error": "Invalid"}), 400

    game_state[ind][stat] = clamp(game_state[ind][stat] + delta, 0, 9999 if stat=="money" else 200)
    log_entry = f"[ADJUST] {INDUSTRIES[ind]['name']} {stat} {'+' if delta>=0 else ''}{delta}"
    game_log.append(log_entry)
    return jsonify({"ok": True})

@app.route("/reset_game", methods=["POST"])
def reset_game():
    global game_state, game_log
    game_state = {ind: copy.deepcopy(DEFAULT_STATE) for ind in INDUSTRIES}
    game_log = ["[GAME RESET] New game started!"]
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
