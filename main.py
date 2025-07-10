import requests
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import telegram
import datetime

# تنظیمات تلگرام
TELEGRAM_TOKEN = "7880802479:AAHKKofxfO1BdxPUqryLupyhM6N6tafNBt8"
CHANNEL_ID = "-1002814094030"

# بارگذاری مدل FinBERT
tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")
model = AutoModelForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")

# تحلیل احساس با FinBERT
def analyze_sentiment_finbert(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True)
    with torch.no_grad():
        logits = model(**inputs).logits
    probabilities = torch.nn.functional.softmax(logits, dim=1)[0]
    labels = ["منفی ❌", "خنثی ⚪️", "مثبت ✅"]
    confidence, label = torch.max(probabilities, dim=0)
    return labels[label.item()], float(confidence.item())

# تشخیص نوع خبر (پایدار / موقتی)
def classify_stability(text):
    keywords_persistent = ["rate", "inflation", "central bank", "interest", "policy", "ECB", "Fed", "BoJ"]
    return "پایدار 🟢" if any(k.lower() in text.lower() for k in keywords_persistent) else "موقتی 🔄"

# دریافت تیتر از Investing.com
def get_investing_forex_headlines():
    url = "https://www.investing.com/news/forex-news"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.select('a[data-test="article-title-link"]')
        headlines = []
        for link in links[:5]:
            title = link.get_text(strip=True)
            href = link.get("href")
            if title and href:
                full_link = "https://www.investing.com" + href if href.startswith("/") else href
                headlines.append((title, full_link))
        return headlines
    except Exception as e:
        print("⛔️ خطا در دریافت اخبار از Investing.com:", e)
        return []

# ارسال پیام به تلگرام
def send_to_telegram(message):
    try:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode=telegram.ParseMode.HTML)
    except Exception as e:
        print("⛔️ خطا در ارسال پیام تلگرام:", e)

# اجرای اصلی
if __name__ == "__main__":
    headlines = get_investing_forex_headlines()

    if not headlines:
        send_to_telegram("⛔️ هیچ تیتر خبری یافت نشد.")
    else:
        now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        message = f"<b>📊 تحلیل سنتیمنت جفت‌ارزها</b>\n⏰ {now}\n"

        for title, link in headlines:
            sentiment, confidence = analyze_sentiment_finbert(title)
            stability = classify_stability(title)
            message += f"\n📰 <b>{title}</b>\n📊 احساس: {sentiment} ({confidence*100:.1f}%)\n🧭 نوع سنتیمنت: {stability}\n🔗 <a href='{link}'>لینک</a>\n"

        message += "\n📡 سیستم تحلیل اتوماتیک | FinBERT | بروز‌رسانی هر ۱۵ دقیقه"
        send_to_telegram(message)

