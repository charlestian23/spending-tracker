# Spending Tracker (100% Local)

Receipt parsing runs entirely on your machine via Ollama + LLaVA.
No data ever leaves your computer.

---

## Setup (one time)

### 1. Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Pull the LLaVA vision model

With your RTX 4080 Super (16GB VRAM), use the 13B model for best accuracy:

```bash
ollama pull llava:13b
```

This downloads ~8GB. For a faster/lighter option use `llava:7b` (~4GB).
If you switch models, update the MODEL variable in app.py.

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

---

## Running the app

### Terminal 1 — start Ollama

```bash
ollama serve
```

### Terminal 2 — start the web app

```bash
python app.py
```

Then open http://localhost:5000 in your browser.

---

## Usage

1. Click or drag a receipt photo onto the upload area
2. Wait 10–20 seconds for LLaVA to parse it (GPU speeds this up significantly)
3. Review the detected merchant, amount, and category
4. Click "Add to log" to save it

All data is stored in `tracker.db` (SQLite) in the project folder.
You can back it up, inspect it with any SQLite browser, or delete it to start fresh.

---

## Project structure

```
spending-tracker/
├── app.py          # Flask server
├── database.py     # SQLite helpers
├── requirements.txt
├── tracker.db      # Created on first run
└── static/
    └── index.html  # Web UI
```

---

## Switching models

Edit the `MODEL` variable at the top of `app.py`:

| Model       | VRAM  | Speed  | Accuracy |
|-------------|-------|--------|----------|
| llava:7b    | ~5GB  | Fast   | Good     |
| llava:13b   | ~9GB  | Medium | Better   |
| llava:34b   | ~20GB | Slow   | Best     |

Your 4080 Super handles up to llava:13b comfortably.
llava:34b may be too large for 16GB VRAM.
