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

bot = telebot.TeleBot(BOT_TOKEN)

# Animated Win Sticker ID
WIN_STICKER_ID = "CAACAgIAAxkBAAEZ78pl3gAB1QAB..."

last_processed_period = ""
active_prediction = None

# --- Flask Server (Render Uptime Check) ---
app = Flask(__name__)

@app.route("/")
@app.route("/health")
def home():
    return "WILD KING ADVANCED TREND BOT IS ONLINE!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

# --- Fetch Live API Data ---
def get_live_data():
    try:
        response = requests.get(API_URL, timeout=8)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0 and "data" in data and "list" in data["data"]:
                return data["data"]["list"]
    except Exception as e:
        print(f"API Fetch Error: {e}")
    return None

# --- ULTRA ADVANCED TREND ENGINE ---
def ultra_trend_engine(history_list):
    if not history_list or len(history_list) < 30:
        return "BIG", "TREND ANALYSIS ENGINE", "NEUTRAL"

    recent = history_list[:30]
    sizes = []
    for item in recent:
        sz = item.get("size", "").lower()
        if not sz:
            sz = "big" if int(item.get("number", 0)) >= 5 else "small"
        sizes.append(sz)

    # 1. Dragon Streak Detection
    if sizes[0] == sizes[1] and sizes[1] == sizes[2] and sizes[2] == sizes[3]:
        prediction = sizes[0].upper()
        trend_tag = f"DRAGON STREAK ({prediction})"
        engine_type = "SUPER TREND LOCK"
        return prediction, engine_type, trend_tag

    # 2. Alternating (1-by-1) Pattern Lock
    if sizes[0] != sizes[1] and sizes[1] != sizes[2] and sizes[2] != sizes[3]:
        prediction = "SMALL" if sizes[0] == "big" else "BIG"
        trend_tag = "ZIG-ZAG 1-BY-1"
        engine_type = "PATTERN MATRIX"
        return prediction, engine_type, trend_tag

    # 3. Double-Double Pattern (2-by-2)
    if sizes[0] == sizes[1] and sizes[2] == sizes[3] and sizes[0] != sizes[2]:
        prediction = "SMALL" if sizes[0] == "big" else "BIG"
        trend_tag = "DOUBLE PAIR SHIFT"
        engine_type = "PATTERN REVERSAL"
        return prediction, engine_type, trend_tag

    # 4. Markov Transition Logic
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

    # 5. EMA Weight Calculation
    weighted_big = 0
    weighted_small = 0
    alpha = 0.88
    for idx, sz in enumerate(sizes[:15]):
        weight = (alpha ** idx)
        if sz == "big": weighted_big += weight
        else: weighted_small += weight

    ema_pred = "BIG" if weighted_big >= weighted_small else "SMALL"

    if markov_pred == ema_pred:
        final_prediction = markov_pred
        engine_type = "HIGH CONFIDENCE MATRIX"
        trend_tag = f"STRONG {final_prediction} MOMENTUM"
    else:
        big_count_10 = sizes[:10].count("big")
        final_prediction = "SMALL" if big_count_10 >= 5 else "BIG"
        engine_type = "PROBABILITY EQUALIZER"
        trend_tag = "VOLUME REVERSAL"

    return final_prediction, engine_type, trend_tag

# --- Send Live Prediction Signal ---
def send_live_prediction_signal(period, prediction, engine_type, trend_tag):
    message = (
        f"👑 **WILD KING ADVANCED SIGNAL** 👑\n\n"
        f"🎮 **Game:** WinGo 30 Seconds\n"
        f"📌 **Period:** `{period}`\n"
        f"🔥 **AI Signal:** **{prediction}**\n"
        f"📈 **Live Trend:** `{trend_tag}`\n"
        f"🧠 **Engine:** `{engine_type}`\n\n"
        f"🔗 **Register & Play:** [Click Here to Join]({REGISTER_LINK})"
    )
    try:
        bot.send_message(CHAT_ID, message, parse_mode="Markdown", disable_web_page_preview=True)
    except Exception as e:
        print(f"Failed to post signal: {e}")

# --- Result Tracker & Win Sticker ---
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
                f"🔥 *WILD KING ADVANCED ACCURACY PASSED!*"
            )
            try:
                bot.send_message(CHAT_ID, result_text, parse_mode="Markdown")
                try:
                    bot.send_sticker(CHAT_ID, WIN_STICKER_ID)
                except Exception:
                    bot.send_message(CHAT_ID, "🎯🎯 WINNER WINNER! STREAK ACTIVE! 🏆✨")
            except Exception as e:
                print(f"Error sending win update: {e}")
        else:
            result_text = (
                f"❌ **RESULT: LOSS ⚠️**\n"
                f"📌 **Period:** `{latest_period}`\n"
                f"📊 **Actual:** `{actual_size}` | **Predicted:** `{predicted}`"
            )
            try:
                bot.send_message(CHAT_ID, result_text, parse_mode="Markdown")
            except Exception as e:
                print(f"Error sending loss update: {e}")

        active_prediction = None

# --- Main Bot Loop ---
def bot_main_loop():
    global last_processed_period, active_prediction
    print("🚀 WILD KING Advanced Trend Bot Running...")

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
                    prediction, engine_type, trend_tag = ultra_trend_engine(history_list)

                    active_prediction = {
                        "period": upcoming_period,
                        "prediction": prediction,
                    }

                    send_live_prediction_signal(upcoming_period, prediction, engine_type, trend_tag)
        except Exception as main_err:
            print(f"Main Loop Error: {main_err}")
            time.sleep(3)

        time.sleep(2)

if __name__ == "__main__":
    # Start Flask Server in background thread
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    # Auto-Restart Guard
    while True:
        try:
            bot_main_loop()
        except Exception as crash_err:
            print(f"Bot Crashed, Restarting... Error: {crash_err}")
            time.sleep(5)
            
