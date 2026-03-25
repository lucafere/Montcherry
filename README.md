# Econopoly Scoreboard

A web-based scoreboard for the Econopoly classroom board game.

## Game Rules Summary
- **4 Industries**: Fishing, Hotelery, Tourism, Restaurants
- **Starting state**: Growth 0 | Inflation 100 | Unemployment 100 | $1500
- **Win condition**: Growth ≥ 100 AND Inflation ≤ 5 AND Unemployment ≤ 5

---

## Run Locally (for testing)

```bash
pip install -r requirements.txt
python app.py
```
Open http://localhost:5000 — anyone on the same WiFi can access it at your local IP.

---

## Deploy Free Online (Render.com) — Anyone Gets a Link

### Step 1: Push to GitHub
1. Create a free account at github.com
2. Create a new repository called `econopoly`
3. Upload all files: `app.py`, `requirements.txt`, and the `templates/` folder

### Step 2: Deploy on Render
1. Create a free account at render.com
2. Click **New → Web Service**
3. Connect your GitHub repo
4. Set these settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Free
5. Click **Deploy**

After ~2 minutes, you'll get a URL like:
`https://econopoly-xxxx.onrender.com`

Share this link with your class — anyone can open it on their phone or laptop!

---

## How the Scoreboard Works

### Scorecard (Top Section)
Each industry shows:
- 📈 Growth bar (0 → 100 goal)
- 🔥 Inflation bar (starts 100, goal ≤ 5)
- 👷 Unemployment bar (starts 100, goal ≤ 5)
- 💰 Balance
- Manual +/- buttons to adjust any stat

### Shocks Tab
- All 10 demand shocks (5 good, 5 bad) and 10 supply shocks
- Check which industries are affected before clicking "Apply Shock"
- Stats update instantly for all players

### Advantage Cards Tab
- Select which player receives a secret advantage card
- The card appears on their scorecard
- Players click their own card to play it

### Properties Tab
- All 18 properties listed with cost and effects
- Select the buyer and click Buy
- Deducted from their balance, effects applied automatically

---

## Notes
- The server stores state in memory — restarting it resets the game
- Use the "Reset Game" button at the top to start a new game
- The page auto-refreshes every 4 seconds so all players see live updates
