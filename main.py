import requests
from bs4 import BeautifulSoup
from transformers import pipeline
from telegram import Bot
import xml.etree.ElementTree as ET

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
        print("\u062e\u0637\u0627 \u062f\u0631 \u062f\u0631\u06cc\u0627\u0641\u062a RSS Investing:", e)
        return []

def analyze_sentiment(text):
    try:
        result = sentiment_pipeline(text)[0]  # {'label': 'positive', 'score': 0.98}
        label = result['label'].lower()
        if label == "positive":
            return "مثبت ✅"
        elif label == "negative":
            return "منفی ❌"
        else:
            return "خنثی ⚪️"
    except Exception as e:
        return "نامشخص ❓"

def send_telegram_message(message):
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception as e:
        print("\u062e\u0637\u0627 \u062f\u0631 \u0627\u0631\u0633\u0627\u0644 \u0628\u0647 \u062a\u0644\u06af\u0631\u0627\u0645:", e)

def main():
    headlines = get_investing_forex_headlines()
    if not headlines:
        send_telegram_message("\u26d4\ufe0f \u0647\u06cc\u0686 \u062a\u06cc\u062a\u0631 \u062e\u0628\u0631\u06cc \u06cc\u0627\u0641\u062a \u0646\u0634\u062f.")
        return

    message = f"\ud83c\udf10 \u062a\u062d\u0644\u06cc\u0644 \u0633\u0646\u062a\u06cc\u0645\u0646\u062a \u062c\u0641\u062a\u200c\u0627\u0631\u0632\u0647\u0627 \n\n\ud83d\udd22 \u062a\u0639\u062f\u0627\u062f \u0639\u0646\u0627\u0648\u06cc\u0646: {len(headlines)}\n"
    sentiment_score = 0

    for title, link in headlines:
        sentiment = analyze_sentiment(title)
        message += f"\n\u25b6\ufe0f {title}\n\ud83d\udd17 {link}\n\u2696\ufe0f \u0627\u062d\u0633\u0627\u0633: {sentiment}\n"

        if sentiment == "مثبت ✅":
            sentiment_score += 1
        elif sentiment == "منفی ❌":
            sentiment_score -= 1

    message += f"\n︐ \u0627\u0645\u062a\u06cc\u0627\u0632 \u0633\u0646\u062a\u06cc\u0645\u0646\u062a: {sentiment_score}\n\n\ud83d\udce1 \u0628\u0631\u0648\u0632\u0631\u0633\u0627\u0646\u06cc \u062e\u0648\u062f\u06a9\u0627\u0631 \u0647\u0631 15 \u062f\u0642\u06cc\u0642\u0647"
    send_telegram_message(message)

if __name__ == "__main__":
    main()
