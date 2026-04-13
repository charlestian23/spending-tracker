import os
import base64
import json
import requests
from flask import Flask, request, jsonify, send_from_directory
from database import init_db, add_entry, get_all_entries, get_totals, get_monthly_totals, delete_entry

app = Flask(__name__, static_folder="static")
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2-vision:latest"

def parse_receipt_with_ollama(image_b64: str) -> dict:
    prompt = (
        "You are a receipt parser. Look at this receipt image and extract the total amount paid, "
        "the merchant or store name, and a short description of what was purchased. "
        "Respond ONLY with a valid JSON object in exactly this format: "
        '{"merchant": "Whole Foods", "amount": 47.82, "category": "food", "notes": "Weekly groceries"}. '
        "The amount must be the final total including tax. "
        "Categories must be one of: food, shopping, entertainment, transportation, gas, other. "
        "If you cannot determine the total, set amount to null. "
        "No explanation, no markdown, just the raw JSON object."
    )
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "images": [image_b64],
        "stream": False,
        "format": "json"
    }
    resp = requests.post(OLLAMA_URL, json=payload, timeout=60)
    resp.raise_for_status()
    raw = resp.json().get("response", "{}")
    return json.loads(raw)

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/api/parse", methods=["POST"])
def parse():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400
    img = request.files["image"]
    img_b64 = base64.b64encode(img.read()).decode("utf-8")
    try:
        result = parse_receipt_with_ollama(img_b64)
    except Exception as e:
        return jsonify({"error": f"Ollama error: {str(e)}"}), 500
    if not result.get("amount"):
        return jsonify({"error": "Could not detect a total amount on the receipt"}), 422
    return jsonify(result)

@app.route("/api/entries", methods=["GET"])
def entries():
    return jsonify(get_all_entries())

@app.route("/api/entries", methods=["POST"])
def add():
    data = request.json
    entry = add_entry(
        amount=data["amount"],
        merchant=data["merchant"],
        category=data.get("category", "other"),
        notes=data.get("notes", "")
    )
    return jsonify(entry), 201

@app.route("/api/entries/<int:entry_id>", methods=["DELETE"])
def delete(entry_id):
    delete_entry(entry_id)
    return jsonify({"deleted": entry_id})

@app.route("/api/totals", methods=["GET"])
def totals():
    return jsonify(get_totals())

@app.route("/api/monthly", methods=["GET"])
def monthly():
    return jsonify(get_monthly_totals())

if __name__ == "__main__":
    init_db()
    print("Starting spending tracker at http://localhost:5000")
    app.run(debug=False, port=5000)