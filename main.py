from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import json
import os

app = Flask(__name__)
CORS(app)

# -----------------------------
# File Setup
# -----------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data.json")

def load_data():
    if not os.path.exists(DATA_FILE):
        save_data({
            "roblox": {},
            "stats": {
                "api_calls": 0,
                "last_update": None
            }
        })
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


# -----------------------------
# STATUS ENDPOINT
# -----------------------------

@app.route("/api/status")
def status():
    return jsonify({
        "status": "online",
        "version": "1.0",
        "timestamp": datetime.now().isoformat()
    })


# -----------------------------
# ROBLOX API — UPDATE PLAYER DATA
# -----------------------------

@app.route("/api/roblox/update", methods=["POST"])
def roblox_update():
    try:
        incoming = request.json
        user_id = str(incoming.get("userId"))

        if not user_id:
            return jsonify({"error": "Missing userId"}), 400

        db = load_data()
        db["stats"]["api_calls"] += 1

        db["roblox"][user_id] = {
            "userId": user_id,
            "name": incoming.get("name"),
            "position": incoming.get("position"),
            "updated": datetime.now().isoformat()
        }

        save_data(db)

        return jsonify({"status": "saved", "data": db["roblox"][user_id]})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -----------------------------
# ROBLOX API — GET PLAYER DATA
# -----------------------------

@app.route("/api/roblox/get/<user_id>", methods=["GET"])
def roblox_get(user_id):
    db = load_data()
    entry = db["roblox"].get(str(user_id))

    return jsonify({
        "status": "success" if entry else "not_found",
        "data": entry
    })


# -----------------------------
# ROOT INDEX
# -----------------------------

@app.route("/")
def home():
    return jsonify({
        "message": "Pagesoftwo API",
        "endpoints": {
            "/api/status": "API status check",
            "/api/roblox/update": "POST player data",
            "/api/roblox/get/<userId>": "GET player data",
        }
    })


# -----------------------------
# RUN (Railway uses gunicorn)
# -----------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
