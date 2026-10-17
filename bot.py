import os
import threading
import time
from flask import Flask
import requests
import telebot

# ---------------- CONFIGURATION ----------------
BOT_TOKEN = "8858083307:AAH0Wks0eHdmalUaZu1NmDd8qsTyE6u1d-Q"
CHAT_ID = "@pak92_qayoom"
REGISTER_LINK = "https://92blaze99.com/register?inviteCode=HD6Y3BN&from=web"
API_URL = "https://sky-predictor-1012593186417.asia-southeast1.run.app/api/wingo-history-30s-100"

# Telegram Bot Object
bot = telebot.TeleBot(BOT_TOKEN)

# Live Animated Win Sticker File ID (Apni sticker file_id yahan replace karein)
WIN_STICKER_ID = "CAACAgIAAxkBAAEZ78pl3gAB1QAB..."

last_processed_period = ""
active_prediction = None

# --- Flask Server (Render Anti-Sleep) ---
app = Flask(__name__)

@app.route("/")
def home():
    return "WILD KING SUPER AI BOT IS RUNNING 24/7 ON CLOUD!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- Live API Data Fetch ---
def get_live_data():
    try:
        response = requests.get(API_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0 and "data" in data and "list" in data["data"]:
                return data["data"]["list"]
    except Exception as e:
        print(f"API Fetch Error: {e}")
    return None

# --- Heavy AI Prediction Engine ---
def super_ai_ensemble_engine(history_list):
    if not history_list or len(history_list) < 25:
        return "BIG", "SUPER AI MATRIX"

    recent = history_list[:25]
    sizes = []
    for item in recent:
        sz = item.get("size", "").lower()
        if not sz:
            sz = "big" if int(item.get("number", 0)) >= 5 else "small"
        sizes.append(sz)

    # 1. 1-by-1 Pattern Lock
    if sizes[0] != sizes[1] and sizes[1] != sizes[2] and sizes[2] != sizes[3]:
        next_pred = "SMALL" if sizes[0] == "big" else "BIG"
        return next_pred, "SUPER AI (1-BY-1 LOCK)"

    # 2. Dragon Streak Rider
    if sizes[0] == sizes[1] and sizes[1] == sizes[2]:
        return sizes[0].upper(), "SUPER AI (DRAGON RIDER)"

    # 3. Markov State Transition
    transitions = {"big_to_big": 0, "big_to_small": 0, "small_to_big": 0, "small_to_small": 0}
    for i in range(len(sizes) - 1):
        curr = sizes[i+1]
        nxt = sizes[i]
        if curr == "big" and nxt == "big": transitions["big_to_big"] += 1
        elif curr == "big" and nxt == "small": transitions["big_to_small"] += 1
        elif curr == "small" and nxt == "big": transitions["small_to_big"] += 1
        elif curr == "small" and nxt == "small": transitions["small_to_small"] += 1

    last_state = sizes[0]
    if last_state == "big":
        markov_pred = "BIG" if transitions["big_to_big"] >= transitions["big_to_small"] else "SMALL"
    else:
        markov_pred = "SMALL" if transitions["small_to_small"] >= transitions["small_to_big"] else "BIG"

    # 4. Exponential Weighted Moving Average (EMA)
    weighted_big = 0
    weighted_small = 0
    alpha = 0.85
    for idx, sz in enumerate(sizes[:15]):
        weight = (alpha ** idx)
        if sz == "big": weighted_big += weight
        else: weighted_small += weight

    ema_pred = "BIG" if weighted_big >= weighted_small else "SMALL"

    if markov_pred == ema_pred:
        final_prediction = markov_pred
        engine_tag = "SUPER AI (HIGH CONFIDENCE)"
    else:
        big_total = sizes[:10].count("big")
        final_prediction = "SMALL" if big_total >= 5 else "BIG"
        engine_tag = "SUPER AI (PROBABILITY BALANCE)"

    return final_prediction, engine_tag

# --- Send Signal Function ---
def send_live_prediction_signal(period, prediction, trend):
    message = (
        f"👑 **WILD KING SUPER AI SIGNAL** 👑\n\n"
        f"🎮 **Game:** WinGo 30 Seconds\n"
        f"📌 **Period:** `{period}`\n"
        f"🔥 **AI Signal:** **{prediction}**\n"
        f"🧠 **Engine:** `{trend}`\n\n"
        f"🔗 **Register & Play:** [Click Here to Join]({REGISTER_LINK})\n\n"
        f"💡 *Tip: Play with strict 3-Level 2X Strategy!*"
    )
    try:
        bot.send_message(CHAT_ID, message, parse_mode="Markdown", disable_web_page_preview=True)
    except Exception as e:
        print(f"Failed to post signal: {e}")

# --- Result Tracker & Live Sticker ---
def check_and_send_result(history_list):
    global active_prediction
    if not active_prediction or not history_list:
        return

    latest = history_list[0]
    latest_period = str(latest.get("issueNumber"))

    if latest_period == active_prediction["period"]:
        actual_size = latest.get("size", "").upper()
        if not actual_size:
            actual_size = "BIG" if int(latest.get("number", 0)) >= 5 else "SMALL"

        predicted = active_prediction["prediction"]

        if actual_size == predicted:
            result_text = (
                f"✅ **RESULT: WIN 🎉**\n"
                f"📌 **Period:** `{latest_period}`\n"
                f"🎯 **Outcome:** `{actual_size}` (Matched)\n\n"
                f"🔥 *WILD KING SUPER AI ACCURACY PASSED!*"
            )
            try:
                bot.send_message(CHAT_ID, result_text, parse_mode="Markdown")
                try:
                    bot.send_sticker(CHAT_ID, WIN_STICKER_ID)
                except Exception:
                    bot.send_message(CHAT_ID, "🎯🎯 WINNER WINNER! SUPER AI STREAK! 🏆✨")
            except Exception as e:
                print(f"Error sending win update: {e}")
        else:
            result_text = (
                f"❌ **RESULT: LOSS ⚠️**\n"
                f"📌 **Period:** `{latest_period}`\n"
                f"📊 **Actual:** `{actual_size}` | **Predicted:** `{predicted}`\n\n"
                f"⚠️ *Apply 2X Martingale Strategy on Next Bet!*"
            )
            try:
                bot.send_message(CHAT_ID, result_text, parse_mode="Markdown")
            except Exception as e:
                print(f"Error sending loss update: {e}")

        active_prediction = None

# --- Main Bot Loop ---
def bot_main_loop():
    global last_processed_period, active_prediction
    print("🚀 WILD KING Super AI Prediction Bot Running on Cloud...")

    while True:
        try:
            history_list = get_live_data()
            if history_list and len(history_list) > 0:
                check_and_send_result(history_list)

                latest_item = history_list[0]
                current_issue = int(latest_item.get("issueNumber"))
                upcoming_period = str(current_issue + 1)

                if upcoming_period != last_processed_period:
                    last_processed_period = upcoming_period
                    prediction, trend = super_ai_ensemble_engine(history_list)

                    active_prediction = {
                        "period": upcoming_period,
                        "prediction": prediction,
                    }

                    send_live_prediction_signal(upcoming_period, prediction, trend)
        except Exception as main_err:
            print(f"Main Loop Error: {main_err}")

        time.sleep(2)

if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.start()
    bot_main_loop()
  
