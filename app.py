from flask import Flask, render_template
import json
import os

app = Flask(__name__)


def load_grover_data():
    json_path = os.path.join(
        os.path.dirname(__file__),
        "grover.json"
    )

    with open(json_path, "r", encoding="utf-8") as file:
        return json.load(file)


@app.route("/")
def home():
    data = load_grover_data()

    return render_template(
        "index.html",
        data=data
    )


if __name__ == "__main__":
    app.run(debug=True)