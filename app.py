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
    "properties": [],
    "active": True,
    "round": 0,
}

GOALS = {"growth": 100, "inflation": 5, "unemployment": 5}

# Wild card decks
DEMAND_SHOCKS = [
    {"id":"d1","type":"demand","valence":"good","title":"Scuba Discovery! New Resources","desc":"AD ↑ — Underwater resources discovered, boosting the economy.","effects":{"growth":15,"unemployment":-10,"inflation":5}},
    {"id":"d2","type":"demand","valence":"good","title":"Tourism Influencer Boom","desc":"AD ↑ — A viral influencer campaign floods the region with tourists.","effects":{"inflation":-5}},
    {"id":"d3","type":"demand","valence":"good","title":"Food Festival","desc":"AD ↑ — A major food festival drives spending across the region.","effects":{"growth":10,"unemployment":-5,"inflation":5}},
    {"id":"d4","type":"demand","valence":"good","title":"Luxury Tourism Trend","desc":"AD ↑ — High-end tourists flock to the region, boosting revenues.","effects":{"growth":15,"unemployment":-5,"inflation":10}},
    {"id":"d5","type":"demand","valence":"good","title":"Strong Tourist Season","desc":"AD ↑ — Record tourist arrivals boost all industries.","effects":{"growth":10,"unemployment":-10,"inflation":5}},
    {"id":"d6","type":"demand","valence":"good","title":"Seafood Export Deal","desc":"AD ↑ — A new international deal opens export markets for seafood.","effects":{"growth":15,"unemployment":-5,"inflation":5}},
    {"id":"d7","type":"demand","valence":"good","title":"Low Interest Rates","desc":"AD ↑ — Cheap credit encourages investment and consumer spending.","effects":{"growth":10,"unemployment":-5,"inflation":10}},
    {"id":"d8","type":"demand","valence":"good","title":"Coconut Trend","desc":"AD ↑ — Global coconut craze drives up demand for local products.","effects":{"growth":10,"unemployment":-5,"inflation":5}},
    {"id":"d9","type":"demand","valence":"bad","title":"Tourism Crash","desc":"AD ↓ — A global travel scare collapses tourist arrivals overnight.","effects":{"growth":-20,"unemployment":15,"inflation":-5}},
    {"id":"d10","type":"demand","valence":"bad","title":"Global Recession","desc":"AD ↓ — Worldwide economic downturn hammers all sectors.","effects":{"growth":-25,"unemployment":20,"inflation":-10}},
    {"id":"d11","type":"demand","valence":"bad","title":"High Interest Rates","desc":"AD ↓ — Expensive credit chills investment and consumer spending.","effects":{"growth":-10,"unemployment":5,"inflation":-5}},
    {"id":"d12","type":"demand","valence":"bad","title":"Bad Reviews","desc":"AD ↓ — Viral negative reviews drive away customers and tourists.","effects":{"growth":-10,"unemployment":5,"inflation":-5}},
]

SUPPLY_SHOCKS = [
    {"id":"s1","type":"supply","valence":"good","title":"Fishing Technology Upgrade","desc":"AS ↑ — New fishing tech raises output and cuts costs.","effects":{"growth":15,"unemployment":-5,"inflation":-5}},
    {"id":"s2","type":"supply","valence":"good","title":"Infrastructure Upgrade","desc":"AS ↑ — New roads, ports and utilities boost productive capacity.","effects":{"growth":20,"unemployment":-10,"inflation":-5}},
    {"id":"s3","type":"supply","valence":"bad","title":"Coral Reef Damage","desc":"AS ↓ — Environmental damage cripples fishing and tourism.","effects":{"growth":-15,"unemployment":10,"inflation":5}},
    {"id":"s4","type":"supply","valence":"bad","title":"Food Safety Issue","desc":"AS ↓ — A contamination scandal forces closures and hits output.","effects":{"growth":-10,"unemployment":5,"inflation":5}},
    {"id":"s5","type":"supply","valence":"bad","title":"Overfishing Crisis","desc":"AS ↓ — Fish stocks collapse, devastating the fishing industry.","effects":{"growth":-15,"unemployment":10,"inflation":5}},
    {"id":"s6","type":"supply","valence":"bad","title":"Hurricane","desc":"AS ↓ — A devastating hurricane destroys infrastructure and jobs.","effects":{"growth":-20,"unemployment":15,"inflation":10}},
    {"id":"s7","type":"supply","valence":"bad","title":"Supply Shortage","desc":"AS ↓ — Key inputs run dry, raising costs and cutting output.","effects":{"growth":-10,"unemployment":5,"inflation":10}},
    {"id":"s8","type":"supply","valence":"bad","title":"Worker Strike","desc":"AS ↓ — A major strike halts production across the economy.","effects":{"growth":-15,"unemployment":10,"inflation":5}},
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
