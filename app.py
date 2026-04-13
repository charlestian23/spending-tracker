import base64
import json
import logging
import time
import requests
from flask import Flask, request, jsonify, send_from_directory
from database import init_db, add_entry, get_all_entries, get_totals, get_monthly_totals, delete_entry

# ── Logging setup ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

app = Flask(__name__, static_folder="static")
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2-vision:latest"

def parse_receipt_with_ollama(image_b64: str) -> dict:
    prompt = (
        "You are a receipt parser. Look at this receipt image and extract the total amount paid, "
        "the merchant or store name, a short description of what was purchased, and the date of the transaction. "
        "Respond ONLY with a valid JSON object in exactly this format: "
        '{"merchant": "Whole Foods", "amount": 47.82, "category": "food", "notes": "weekly groceries", "date": "2024-03-15"}. '
        "The amount must be the final total including tax. "
        "Categories must be one of: food, shopping, entertainment, transportation, gas, other. "
        "If you cannot determine the total, set amount to null. "
        "Look carefully for a date printed on the receipt — it is usually near the top and commonly formatted as MM/DD/YYYY (e.g. 04/12/2026). "
        "Convert any date you find to YYYY-MM-DD format (e.g. 04/12/2026 becomes 2026-04-12). "
        "Only set the date if you can clearly read all three parts: month, day, and year. "
        "If the date is missing, partially cut off, or you are not confident in any part of it, set date to null. "
        "No explanation, no markdown, just the raw JSON object."
    )
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "images": [image_b64],
        "stream": False,
        "format": "json",
    }

    log.info("Sending receipt to Ollama (model: %s)", MODEL)
    t0 = time.time()
    resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
    elapsed = time.time() - t0
    resp.raise_for_status()

    ollama_json = resp.json()
    raw = ollama_json.get("response", "{}")

    log.info("Ollama responded in %.1fs", elapsed)
    log.info("Raw model output:\n%s", json.dumps(json.loads(raw), indent=2))

    # Log useful Ollama metadata if available
    if "eval_count" in ollama_json:
        tokens = ollama_json["eval_count"]
        duration_ns = ollama_json.get("eval_duration", 0)
        tok_per_sec = tokens / (duration_ns / 1e9) if duration_ns else 0
        log.info("Tokens generated: %d  (%.1f tok/s)", tokens, tok_per_sec)

    return json.loads(raw)

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/api/parse", methods=["POST"])
def parse():
    if "image" not in request.files:
        log.warning("Parse request received with no image attached")
        return jsonify({"error": "No image provided"}), 400

    img = request.files["image"]
    log.info("Received image: %s (%s)", img.filename, img.content_type)

    img_bytes = img.read()
    log.info("Image size: %.1f KB", len(img_bytes) / 1024)
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")

    try:
        result = parse_receipt_with_ollama(img_b64)
    except requests.exceptions.ConnectionError:
        log.error("Could not connect to Ollama at %s — is it running?", OLLAMA_URL)
        return jsonify({"error": "Could not connect to Ollama. Is it running?"}), 500
    except Exception as e:
        log.error("Ollama error: %s", e)
        return jsonify({"error": f"Ollama error: {str(e)}"}), 500

    if not result.get("amount"):
        log.warning("Model could not detect a total amount. Parsed result: %s", result)
        return jsonify({"error": "Could not detect a total amount on the receipt"}), 422

    log.info(
        "Parsed OK — merchant: %r  amount: $%.2f  category: %s  date: %s",
        result.get("merchant"), result.get("amount", 0),
        result.get("category"), result.get("date", "not found"),
    )
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
        notes=data.get("notes", ""),
        date=data.get("date", None),
    )
    log.info(
        "Entry saved — #%d  %r  $%.2f  [%s]  %s",
        entry["id"], entry["merchant"], entry["amount"],
        entry["category"], entry["date"],
    )
    return jsonify(entry), 201

@app.route("/api/entries/<int:entry_id>", methods=["DELETE"])
def delete(entry_id):
    delete_entry(entry_id)
    log.info("Entry #%d deleted", entry_id)
    return jsonify({"deleted": entry_id})

@app.route("/api/totals", methods=["GET"])
def totals():
    return jsonify(get_totals())

@app.route("/api/monthly", methods=["GET"])
def monthly():
    return jsonify(get_monthly_totals())

if __name__ == "__main__":
    init_db()
    log.info("Spending tracker starting on http://localhost:5000")
    log.info("Model: %s  |  Ollama: %s", MODEL, OLLAMA_URL)
    app.run(debug=False, port=5000)