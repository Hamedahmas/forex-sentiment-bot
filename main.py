import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from datetime import datetime

# اطلاعات ربات تلگرام برای جفت ارزها
TELEGRAM_TOKEN = "7880802479:AAHKKofxfO1BdxPUqryLupyhM6N6tafNBt8"
TELEGRAM_CHAT_ID = "-1002814094030"

# دریافت تیترها از DailyFX (برای شروع)
def fetch_forex_headlines():
    url = "https://www.dailyfx.com/news"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        articles = soup.select("a.dYFjJe")  # انتخاب تیترها از DailyFX (تغییر در صورت تغییر DOM)
        headlines = []
        for a in articles[:5]:
            title = a.get_text(strip=True)
            link = a["href"] if a["href"].startswith("http") else f"https://www.dailyfx.com{a['href']}"
            headlines.append((title, link))
        return headlines
    except Exception as e:
        print("خطا در دریافت تیترها:", e)
        return []

# تحلیل سنتیمنت با TextBlob و تعیین پایداری

def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    sentiment = "خنثی ⚪️"
    if polarity > 0.1:
        sentiment = "مثبت ✅"
    elif polarity < -0.1:
        sentiment = "منفی ❌"
    return sentiment, polarity

def classify_sentiment_stability(title):
    keywords_persistent = ["interest rate", "inflation", "central bank", "ECB", "FED", "GDP"]
    for word in keywords_persistent:
        if word.lower() in title.lower():
            return "پایدار 🧭"
    return "موقتی ⏱"

# ارسال پیام به تلگرام
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("خطا در ارسال پیام تلگرام:", e)

# اجرای برنامه اصلی
def main():
    headlines = fetch_forex_headlines()
    if not headlines:
        send_telegram_message("⛔️ هیچ تیتر خبری برای جفت‌ارزها یافت نشد.")
        return

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    message = f"📊 <b>تحلیل سنتیمنت جفت‌ارزها</b>\n⏰ {now}\n\n"
    score = 0

    for title, link in headlines:
        sentiment, polarity = analyze_sentiment(title)
        stability = classify_sentiment_stability(title)
        message += f"📰 <b>{title}</b>\n🔗 {link}\n📊 احساس: {sentiment} ({polarity:.2f})\n🧭 نوع سنتیمنت: {stability}\n\n"
        if sentiment == "مثبت ✅":
            score += 1
        elif sentiment == "منفی ❌":
            score -= 1

    message += f"<b>امتیاز کلی سنتیمنت:</b> {score}\n\n📡 سیستم تحلیل جفت‌ارز | بروزرسانی خودکار"
    send_telegram_message(message)

if __name__ == "__main__":
    main()
