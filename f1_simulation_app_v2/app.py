from flask import Flask, render_template, jsonify
import random

app = Flask(__name__)

# 🏁 Current standings
points = {
    "Max Verstappen": 321,
    "Lando Norris": 357,
    "Oscar Piastri": 356
}

# Remaining races & sprint rounds
remaining_races = ["Brazil", "Las Vegas", "Qatar", "Abu Dhabi"]
sprint_races = {"Brazil", "Qatar"}  # use set for fast lookup

# F1 points system
race_points = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
sprint_points = [8, 7, 6, 5, 4, 3, 2, 1]

def get_points(position, is_sprint=False):
    table = sprint_points if is_sprint else race_points
    return table[position - 1] if 1 <= position <= len(table) else 0

def run_simulation():
    winning_scenarios = []

    # 🔁 Simulate 10 000 possible seasons
    for _ in range(10000):
        totals = points.copy()
        results = []

        for race in remaining_races:
            # 🏆 Max always wins the main race
            max_pos = 1

            # Lando & Oscar always P2–P3 (order random)
            if random.choice([True, False]):
                lando_pos, oscar_pos = 2, 3
            else:
                lando_pos, oscar_pos = 3, 2

            # Add main race points
            totals["Max Verstappen"] += get_points(max_pos)
            totals["Lando Norris"] += get_points(lando_pos)
            totals["Oscar Piastri"] += get_points(oscar_pos)

            main_str = f"Max P{max_pos}, Lando P{lando_pos}, Oscar P{oscar_pos}"

            # Sprint handling (Brazil & Qatar)
            if race in sprint_races:
                # Assume same trio in P1–P3, Max always P1
                if random.choice([True, False]):
                    sprint_lando, sprint_oscar = 2, 3
                else:
                    sprint_lando, sprint_oscar = 3, 2
                sprint_max = 1

                totals["Max Verstappen"] += get_points(sprint_max, True)
                totals["Lando Norris"] += get_points(sprint_lando, True)
                totals["Oscar Piastri"] += get_points(sprint_oscar, True)

                sprint_str = f"Max P{sprint_max}, Lando P{sprint_lando}, Oscar P{sprint_oscar}"
            else:
                sprint_str = "—"

            results.append((race, main_str, sprint_str))

        # ✅ Check if Max wins the championship
        if (totals["Max Verstappen"] > totals["Lando Norris"]
            and totals["Max Verstappen"] > totals["Oscar Piastri"]):
            winning_scenarios.append((totals, results))

    total_wins = len(winning_scenarios)
    probability = round(total_wins / 10000 * 100, 2) if total_wins is not None else 0.0

    examples = []
    if winning_scenarios:
        examples_raw = random.sample(winning_scenarios, min(3, len(winning_scenarios)))
        for totals, results in examples_raw:
            examples.append({
                "totals": totals,
                "results": [{"race": r, "main": m, "sprint": s} for r,m,s in results]
            })

    return {
        "total_wins": total_wins,
        "probability": probability,
        "note": ("These simulations consider only scenarios where Max Verstappen, "
                 "Lando Norris, and Oscar Piastri consistently finish on the podium (P1–P3) "
                 "in both main races and sprint sessions. Max is modeled to win every possible main race and sprint event."),
        "examples": examples
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/simulate')
def simulate():
    data = run_simulation()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
