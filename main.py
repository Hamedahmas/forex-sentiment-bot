import requests
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from datetime import datetime
import numpy as np

TELEGRAM_TOKEN = "7880802479:AAHKKofxfO1BdxPUqryLupyhM6N6tafNBt8"
TELEGRAM_CHAT_ID = "-1002814094030"

# بارگذاری مدل FinBERT
MODEL_NAME = "yiyanghkust/finbert-tone"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

LABELS = ['negative', 'neutral', 'positive']

def analyze_sentiment_finbert(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    scores = torch.nn.functional.softmax(outputs.logits, dim=1)[0].numpy()
    top = np.argmax(scores)
    return LABELS[top], float(scores[top])

def classify_stability(title):
    keywords = ["interest", "inflation", "central bank", "rate hike", "FED", "ECB", "GDP"]
    for kw in keywords:
        if kw.lower() in title.lower():
            return "پایدار 🧭"
    return "موقتی ⏱"

def get_investing_headlines():
    url = "https://www.investing.com/news/forex-news"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, "html.parser")
    return [(a.get_text(strip=True), "https://www.investing.com" + a["href"]) 
            for a in soup.select(".largeTitle a.title")][:5]

def get_reuters_headlines():
    url = "https://www.reuters.com/markets/currencies/"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.content, "html.parser")
    return [(a.get_text(strip=True), "https://www.reuters.com" + a["href"]) 
            for a in soup.select("a[data-testid='Heading']")][:5]

def get_forexfactory_headlines():
    url = "https://www.forexfactory.com/news"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.content, "html.parser")
    return [(a.get_text(strip=True), "https://www.forexfactory.com" + a["href"]) 
            for a in soup.select(".title a")][:3]

def get_all_headlines():
    return get_investing_headlines() + get_reuters_headlines() + get_forexfactory_headlines()

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    requests.post(url, data=payload)

def main():
    headlines = get_all_headlines()
    if not headlines:
        send_telegram_message("⛔️ هیچ تیتر خبری یافت نشد.")
        return

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    message = f"📊 <b>تحلیل سنتیمنت جفت‌ارزها (با FinBERT)</b>\n⏰ {now}\n\n"
    score = 0

    for title, link in headlines:
        sentiment, confidence = analyze_sentiment_finbert(title)
        stability = classify_stability(title)
        if sentiment == "positive":
            score += 1
        elif sentiment == "negative":
            score -= 1

        message += f"📰 <b>{title}</b>\n🔗 {link}\n📊 احساس: {sentiment} ({confidence:.2f})\n🧭 نوع سنتیمنت: {stability}\n\n"

    message += f"<b>امتیاز کلی سنتیمنت:</b> {score}\n\n📡 تحلیل اتوماتیک | بروزرسانی هر 2 ساعت"
    send_telegram_message(message)

if __name__ == "__main__":
    main()
