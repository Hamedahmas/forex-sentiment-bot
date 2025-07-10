import requests
from bs4 import BeautifulSoup
from transformers import pipeline
from telegram import Bot
import xml.etree.ElementTree as ET
from datetime import datetime

# تنظیمات تلگرام
TELEGRAM_TOKEN = "7880802479:AAHKKofxfO1BdxPUqryLupyhM6N6tafNBt8"
TELEGRAM_CHAT_ID = "-1002814094030"

# مدل FinBERT برای تحلیل سنتیمنت
sentiment_pipeline = pipeline("sentiment-analysis", model="ProsusAI/finbert")

def get_investing_forex_headlines():
    url = "https://www.investing.com/rss/news_301.rss"
    headers = {
        "User-Agent": "Mozilla/5.0",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        root = ET.fromstring(response.text)

        headlines = []
        for item in root.findall(".//item")[:5]:
            title = item.find("title").text.strip()
            link = item.find("link").text.strip()
            headlines.append((title, link))

        return headlines

    except Exception as e:
        print("خطا در دریافت RSS Investing:", e)
        return []

def analyze_sentiment(text):
    try:
        result = sentiment_pipeline(text)[0]
        label = result['label'].lower()
        if label == "positive":
            return "مثبت ✅"
        elif label == "negative":
            return "منفی ❌"
        else:
            return "خنثی ⚪️"
    except Exception as e:
        return "نامشخص ❓"

def classify_sentiment_type(title):
    stable_keywords = ["interest rate", "inflation", "central bank", "monetary policy", "GDP", "unemployment", "ECB", "Fed", "BOJ"]
    for keyword in stable_keywords:
        if keyword.lower() in title.lower():
            return "پایدار 🟩"
    return "موقتی 🟨"

def extract_currency_pairs(title):
    pairs = {
        "EUR/USD": ["euro", "eur", "ecb"],
        "USD/JPY": ["yen", "jpy", "boj"],
        "GBP/USD": ["pound", "gbp", "boe"],
        "USD/CHF": ["swiss", "franc", "chf"],
        "AUD/USD": ["australian", "aud", "rba"],
        "USD/CAD": ["canadian", "cad", "boc"],
    }
    result = []
    for pair, keywords in pairs.items():
        for word in keywords:
            if word.lower() in title.lower():
                direction = "↑ صعودی" if "positive" in title.lower() or "rise" in title.lower() else "↓ نزولی"
                strength = "تأثیر زیاد" if any(k in title.lower() for k in ["rate", "inflation", "cut", "surge"]) else "تأثیر کم"
                result.append(f"{pair} → {direction} ({strength})")
                break
    return result if result else ["نامشخص"]

def send_telegram_message(message):
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception as e:
        print("خطا در ارسال به تلگرام:", e)

def main():
    headlines = get_investing_forex_headlines()
    if not headlines:
        send_telegram_message("⛔️ هیچ تیتر خبری یافت نشد.")
        return

    for title, link in headlines:
        sentiment = analyze_sentiment(title)
        sentiment_type = classify_sentiment_type(title)
        pairs = extract_currency_pairs(title)
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

        message = f"""
📊 تحلیل جفت‌ارزها (فارکس)
⏰ {timestamp}
📰 {title}
📊 احساس: {sentiment}
🧭 نوع سنتیمنت: {sentiment_type}
📈 جفت‌ارزهای تحت‌تأثیر:

{chr(10).join(pairs)}

🔗 {link}
📡 تحلیل اتوماتیک هوشمند
"""
        send_telegram_message(message)

if __name__ == "__main__":
    main()
