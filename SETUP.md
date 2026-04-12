# Spending Tracker — Full Setup Guide

---

## Step 1 — Install Ollama

```bash
sudo apt install curl
curl -fsSL https://ollama.com/install.sh | sh
```

---

## Step 2 — Set up the model storage directory

Create a dedicated folder for the LLaVA model on your chosen drive:

```bash
mkdir -p /mnt/Linux/ai-models/llava
```

Tell Ollama to use that location permanently:

```bash
echo 'export OLLAMA_MODELS=/mnt/Linux/ai-models/llava' >> ~/.bashrc
source ~/.bashrc
```

---

## Step 3 — Download the LLaVA vision model (~8GB)

```bash
ollama pull llava:13b
```

The model will be saved to `/mnt/Linux/ai-models/llava`.

---

## Step 4 — Set up the spending tracker

Create the project folder and copy in your files:

```bash
mkdir spending-tracker
cd spending-tracker
mkdir static
```

Your folder should look like this:

```
spending-tracker/
├── app.py
├── database.py
├── requirements.txt
└── static/
    └── index.html
```

---

## Step 5 — Install Python dependencies

```bash
pip install -r requirements.txt
```

---

## Step 6 — Run the app

You need two terminals open.

**Terminal 1 — start Ollama:**
```bash
ollama serve
```

**Terminal 2 — start the web app:**
```bash
cd spending-tracker
python app.py
```

Then open http://localhost:5000 in your browser.

---

## Step 7 — Set up KDE Connect (phone → computer transfers)

**On your computer:**
```bash
sudo apt install kdeconnect
```

**On your phone:** install KDE Connect from the App Store or Play Store.

Make sure both devices are on the same WiFi, then:

1. Open KDE Connect on your phone
2. It should detect your computer — tap it and click "Pair"
3. Accept the pairing request on your computer

From then on, take a receipt photo on your phone, hit **Share → KDE Connect**,
and it will land on your computer ready to drag into the tracker.

---

## Day-to-day usage

Each time you want to use the tracker, just run Steps 6 and 7 (send photo via
KDE Connect, then upload at http://localhost:5000).

---

## Notes

- Your spending data is stored in `spending-tracker/tracker.db` — back this file
  up to keep your history safe.
- To use a lighter/faster model, change `MODEL = "llava:13b"` in `app.py` to
  `llava:7b` and run `ollama pull llava:7b`.
- If you ever move the model folder, update `OLLAMA_MODELS` in `~/.bashrc` to
  the new path.
