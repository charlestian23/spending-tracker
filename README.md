# Spending Tracker

A local-first discretionary spending tracker that uses AI to parse receipt photos. Upload a photo of any receipt or order confirmation and the app extracts the total, merchant, category, and date — all of which you can review and edit before saving. You can also enter transactions manually.

**Everything runs on your machine.** No data is sent to any external server. Receipt parsing is handled by [Ollama](https://ollama.com) + [Llama 3.2 Vision](https://ollama.com/library/llama3.2-vision) running locally.

---

## Features

- Upload receipt photos (JPEG, PNG, WEBP) via drag and drop or file picker
- AI extracts total amount, merchant, category, date, and notes
- Review and edit all fields before saving — including a built-in calculator for adjusting the amount
- Manual entry tab for adding transactions without a receipt
- Categories: food, shopping, entertainment, transportation, gas, other
- Editable transaction date, defaults to today if the model can't determine it
- Month-to-month bar chart with $50 Y-axis gridlines
- Dark mode with system preference detection and localStorage persistence
- Transaction log sortable by date
- All data stored locally in SQLite
- Structured stdout logging for visibility into model output and performance

---

## Requirements

- Ubuntu (or any Linux distro)
- Python 3.8+
- [Ollama](https://ollama.com) with the `llama3.2-vision:latest` model
- An NVIDIA GPU with 8GB+ VRAM recommended (runs on CPU but slowly)

---

## Setup

### 1. Install Ollama

```bash
sudo apt install curl
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Configure model storage (optional)

If you want models stored on a specific drive, set `OLLAMA_MODELS` permanently:

```bash
# Create the directory
mkdir -p /your/drive/ai-models/llava

# Set permissions
sudo chown -R ollama:ollama /your/drive/ai-models/llava
sudo chmod 755 /your/drive/ai-models
sudo chmod 755 /your/drive

# Add to the ollama systemd service
sudo systemctl edit ollama
```

In the editor, add:

```ini
[Service]
Environment="OLLAMA_MODELS=/your/drive/ai-models/llava"
```

Then reload:

```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

### 3. Pull the vision model (~8GB)

```bash
ollama pull llama3.2-vision:latest
```

### 4. Set up a virtual environment

```bash
cd spending-tracker

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

---

## Running the app

You need two terminals open.

**Terminal 1 — start Ollama:**
```bash
ollama serve
```

**Terminal 2 — start the web app:**
```bash
cd spending-tracker
source venv/bin/activate
python app.py
```

Then open **http://localhost:5000** in your browser.

---

## Usage

### Uploading a receipt

1. Click the **Upload receipt** tab and drag or click to upload a photo
2. The model will parse the total, merchant, category, and date (~10–20 seconds)
3. Review the pre-filled fields and correct anything the model got wrong
4. Use the **▾ calculator** toggle under the amount field to open a built-in calculator if you need to adjust the total (e.g. to split a bill or exclude items someone else is paying for). The numpad works when the calculator is open and no text field is focused
5. Click **Add to log** to save

### Manual entry

Click the **Manual entry** tab to type in a transaction directly without uploading a receipt. Fill in the merchant, amount, category, date, and optional notes, then click **Add to log**.

### Dark mode

Click the **🌙 Dark** button in the top right to toggle dark mode. Your preference is saved and the app also respects your system's dark mode setting on first visit.

---

## Transferring receipt photos from your phone

[KDE Connect](https://kdeconnect.kde.org) is the easiest way to send photos wirelessly.

```bash
sudo apt install kdeconnect
```

Install KDE Connect on your phone, make sure both devices are on the same WiFi, pair them, then use **Share → KDE Connect** after taking a receipt photo.

---

## Project structure

```
spending-tracker/
├── app.py              # Flask server, API routes, and logging
├── database.py         # SQLite helpers
├── requirements.txt    # Python dependencies
├── tracker.db          # Created on first run — your spending data
├── .gitignore
└── static/
    └── index.html      # Frontend UI
```

---

## Configuration

To switch models, edit the `MODEL` variable at the top of `app.py`:

| Model                    | VRAM   | Notes                        |
|--------------------------|--------|------------------------------|
| llama3.2-vision:latest   | ~8GB   | Recommended                  |
| llama3.2-vision:11b      | ~8GB   | Same as latest               |
| llava:13b                | ~9GB   | Alternative, less accurate   |
| llava:7b                 | ~5GB   | Faster, lower accuracy       |

Model inference options (also in `app.py`):

```python
"options": {
    "temperature": 0.2,   # Lower = more consistent, 0 = sometimes too conservative
    "num_ctx": 4096,
    "num_predict": 256,
}
```

---

## Data

Spending data is stored in `tracker.db` (SQLite) in the project root. Back this file up to preserve your history. You can inspect or edit it with any SQLite browser such as [DB Browser for SQLite](https://sqlitebrowser.org).

To migrate existing `transport` category entries to `transportation`:

```bash
sqlite3 tracker.db "UPDATE entries SET category='transportation' WHERE category='transport';"
```