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
        "You are a receipt parser. Look at this receipt image and extract every individual line item, "
        "the merchant/store name, and categorize the overall purchase. "
        "Respond ONLY with a valid JSON object in exactly this format: "
        '{"merchant": "Whole Foods", "category": "food", "notes": "grocery run", '
        '"items": [{"name": "Organic Milk", "amount": 4.99}, {"name": "Bread", "amount": 3.49}, {"name": "Apples", "amount": 6.00}]}. '
        "Each item must have a name and amount. "
        "If you cannot read individual items, make a single item with the name being a short description of the purchase and the total as its amount. "
        "Categories must be one of: food, shopping, entertainment, transport, other. "
        "Do not include tax as a line item — roll it into the total proportionally or omit it. "
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
    result = json.loads(raw)
    # Ensure items list exists
    if "items" not in result or not result["items"]:
        result["items"] = [{"name": result.get("notes", "Purchase"), "amount": result.get("amount", 0)}]
    # Compute total from items as fallback
    if not result.get("amount"):
        result["amount"] = round(sum(i.get("amount", 0) for i in result["items"]), 2)
    return result

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
    if not result.get("items"):
        return jsonify({"error": "Could not detect any items on the receipt"}), 422
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
