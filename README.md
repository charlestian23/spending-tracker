# Spending Tracker

A local-first discretionary spending tracker that uses AI to parse receipt photos. Upload a photo of any receipt or order confirmation and the app extracts the line items, lets you exclude anything you're not paying for, and saves the total to a running log with month-to-month charts.

**Everything runs on your machine.** No data is sent to any external server. Receipt parsing is handled by [Ollama](https://ollama.com) + [LLaVA](https://ollama.com/library/llava) running locally.

---

## Features

- Upload receipt photos (JPEG, PNG, WEBP) via drag and drop or file picker
- AI extracts individual line items with amounts
- Uncheck items you're not paying for — the total updates live
- Spending log with merchant, category, date, and amount
- Month-to-month bar chart
- All data stored locally in SQLite

---

## Requirements

- Ubuntu (or any Linux distro)
- Python 3.8+
- [Ollama](https://ollama.com) with the `llava:13b` model
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

# Set permissions for the ollama service user
sudo chown -R ollama:ollama /your/drive/ai-models/llava
sudo chmod 755 /your/drive/ai-models

# Make the parent directory accessible
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

### 3. Pull the LLaVA vision model (~8GB)

```bash
ollama pull llava:13b
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

## Transferring receipt photos from your phone

[KDE Connect](https://kdeconnect.kde.org) is the easiest way to send photos from your phone to your computer wirelessly.

```bash
sudo apt install kdeconnect
```

Install KDE Connect on your phone, make sure both devices are on the same WiFi, pair them, then use **Share → KDE Connect** after taking a receipt photo.

---

## Project structure

```
spending-tracker/
├── app.py              # Flask server and API routes
├── database.py         # SQLite helpers
├── requirements.txt    # Python dependencies
├── tracker.db          # Created on first run — your spending data
└── static/
    └── index.html      # Frontend UI
```

---

## Configuration

To switch to a different LLaVA model, edit the `MODEL` variable at the top of `app.py`:

| Model      | VRAM  | Speed  | Accuracy |
|------------|-------|--------|----------|
| llava:7b   | ~5GB  | Fast   | Good     |
| llava:13b  | ~9GB  | Medium | Better   |

---

## Data

Spending data is stored in `tracker.db` (SQLite) in the project root. Back this file up to preserve your history. You can open it with any SQLite browser such as [DB Browser for SQLite](https://sqlitebrowser.org).
