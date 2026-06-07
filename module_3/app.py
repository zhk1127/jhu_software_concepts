from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    results = {
        "Q1": "33,051 Fall 2026 entries",
        "Q2": "44.85% International students",
        "Q3": "GPA = 3.77, GRE = 325.08, GRE-V = 160.64, GRE-AW = 4.35",
        "Q4": "Average GPA of American Fall 2026 applicants = 3.79",
        "Q5": "Acceptance rate = 35.84%",
        "Q6": "Average GPA of accepted Fall 2026 applicants = 3.77",
        "Q7": "JHU Computer Science Master's applicants = 9",
        "Q8": "Accepted 2026 PhD Computer Science applicants from Georgetown, MIT, Stanford, and CMU = 15",
        "Q9": "LLM-generated fields produced the same result as Q8 (15)",
        "Q10": "JHU biology-related PhD applicants = 39",
        "Q11": "Acceptance rate for JHU biology-related PhD applicants = 20.51%"
    }

    return render_template("index.html", results=results)

if __name__ == "__main__":
    app.run(debug=True)