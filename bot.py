import os
import threading
import time
from flask import Flask
import requests
import telebot
from google import genai

# ---------------- CONFIGURATION ----------------
BOT_TOKEN = "8858083307:AAH0Wks0eHdmalUaZu1NmDd8qsTyE6u1d-Q"
CHAT_ID = "@pak92_qayoom"
REGISTER_LINK = "https://92blaze99.com/register?inviteCode=HD6Y3BN&from=web"
API_URL = "https://sky-predictor-1012593186417.asia-southeast1.run.app/api/wingo-history-30s-100"

# Gemini AI Setup
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
ai_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE" else None

bot = telebot.TeleBot(BOT_TOKEN)

WIN_STICKER_ID = "CAACAgIAAxkBAAEZ78pl3gAB1QAB..."

last_processed_period = ""
active_prediction = None

# --- Flask Server (Keep-Alive Guard on Port 10000) ---
app = Flask(__name__)

@app.route("/")
@app.route("/health")
def home():
    return "WILD KING ADVANCED GEMINI AI BOT IS LIVE 24/7", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

# --- Safe Message & Sticker Sender ---
def safe_send_message(chat_id, text, parse_mode="Markdown", disable_web_page_preview=True):
    for attempt in range(3):
        try:
            bot.send_message(chat_id, text, parse_mode=parse_mode, disable_web_page_preview=disable_web_page_preview, timeout=20)
            return True
        except Exception as e:
            print(f"Telegram Send Attempt {attempt+1} Failed: {e}")
            time.sleep(2)
    return False

def safe_send_sticker(chat_id, sticker_id):
    for attempt in range(3):
        try:
            bot.send_sticker(chat_id, sticker_id, timeout=20)
            return True
        except Exception as e:
            print(f"Telegram Sticker Attempt {attempt+1} Failed: {e}")
            time.sleep(2)
    return False

# --- Fetch Live API Data ---
def get_live_data():
    try:
        response = requests.get(API_URL, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0 and "data" in data and "list" in data["data"]:
                return data["data"]["list"]
    except Exception as e:
        print(f"API Fetch Error: {e}")
    return None

# --- POWERFUL GEMINI AI & ULTRA TREND ENGINE (BIG / SMALL ONLY) ---
def gemini_ultra_engine(history_list):
    if not history_list or len(history_list) < 20:
        return "BIG", "GEMINI ULTRA AI", "NEUTRAL PATTERN"

    recent = history_list[:20]
    history_summary = []
    for item in recent:
        number = int(item.get("number", 0))
        size = item.get("size", "").upper()
        if not size:
            size = "BIG" if number >= 5 else "SMALL"
        history_summary.append(f"{size}({number})")

    # 1. Primary: Google Gemini AI Analysis
    if ai_client:
        try:
            prompt = (
                f"You are the world's most accurate WinGo 30s prediction engine. "
                f"Analyze this recent history sequence: {history_summary}. "
                f"Predict ONLY 'BIG' or 'SMALL' for the next round based on mathematical probability and Markov chains. "
                f"Respond STRICTLY in this format with no extra text: PREDICTION|CONFIDENCE_TAG|ENGINE_TAG\n"
                f"Example: BIG|STRONG BIG MOMENTUM|GEMINI 2.5 FLASH MATRIX"
            )
            response = ai_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            res_text = response.text.strip()
            if "|" in res_text:
                parts = res_text.split("|")
                pred = parts[0].strip().upper()
                if pred in ["BIG", "SMALL"]:
                    trend_tag = parts[1].strip()
                    engine_type = parts[2].strip()
                    return pred, engine_type, trend_tag
        except Exception as e:
            print(f"Gemini API Engine Error: {e}")

    # 2. Advanced Fallback Math Engine (In case API fails)
    sizes = [s.split("(")[0] for s in history_summary]
    
    # Dragon Pattern Lock
    if sizes[0] == sizes[1] == sizes[2] == sizes[3]:
        return sizes[0], "SUPER TREND LOCK", f"DRAGON STREAK ({sizes[0]})"

    # Alternating 1-by-1
    if sizes[0] != sizes[1] and sizes[1] != sizes[2] and sizes[2] != sizes[3]:
        next_pred = "SMALL" if sizes[0] == "BIG" else "BIG"
        return next_pred, "PATTERN MATRIX", "ZIG-ZAG 1-BY-1"

    # Probability Equalizer
    big_count = sizes[:10].count("BIG")
    final_pred = "SMALL" if big_count >= 5 else "BIG"
    return final_pred, "PROBABILITY EQUALIZER", f"VOLUME SHIFT ({final_pred})"

# --- Send Live Signal to Channel ---
def send_live_prediction_signal(period, prediction, engine_type, trend_tag):
    message = (
        f"👑 **WILD KING GEMINI AI SIGNAL** 👑\n\n"
        f"🎮 **Game:** WinGo 30 Seconds\n"
        f"📌 **Period:** `{period}`\n"
        f"🎯 **AI Prediction:** **{prediction}**\n"
        f"📈 **Live Trend:** `{trend_tag}`\n"
        f"🧠 **Engine:** `{engine_type}`\n\n"
        f"🔗 **Register & Play:** [Click Here to Join]({REGISTER_LINK})"
    )
    safe_send_message(CHAT_ID, message)

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
                f"🔥 *WILD KING GEMINI AI PASSED!*"
            )
            sent = safe_send_message(CHAT_ID, result_text)
            if sent:
                sticker_sent = safe_send_sticker(CHAT_ID, WIN_STICKER_ID)
                if not sticker_sent:
                    safe_send_message(CHAT_ID, "🏆🏆 WINNER WINNER! STREAK ACTIVE! ✨")
        else:
            result_text = (
                f"❌ **RESULT: LOSS ⚠️**\n"
                f"📌 **Period:** `{latest_period}`\n"
                f"📊 **Actual:** `{actual_size}` | **Predicted:** `{predicted}`"
            )
            safe_send_message(CHAT_ID, result_text)

        active_prediction = None

# --- Main Bot Loop ---
def bot_main_loop():
    global last_processed_period, active_prediction
    print("🚀 WILD KING Gemini AI Broadcaster Bot Running...")

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
                    prediction, engine_type, trend_tag = gemini_ultra_engine(history_list)

                    active_prediction = {
                        "period": upcoming_period,
                        "prediction": prediction,
                    }

                    send_live_prediction_signal(upcoming_period, prediction, engine_type, trend_tag)
        except Exception as main_err:
            print(f"Main Loop Recovered: {main_err}")
            time.sleep(3)

        time.sleep(2)

if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    while True:
        try:
            bot_main_loop()
        except Exception as crash_err:
            print(f"Auto Restarting Loop... Error: {crash_err}")
            time.sleep(5)
            
