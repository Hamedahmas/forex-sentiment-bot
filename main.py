import requests
from bs4 import BeautifulSoup
from transformers import pipeline
from telegram import Bot

# تنظیمات تلگرام
TELEGRAM_TOKEN = "7880802479:AAHKKofxfO1BdxPUqryLupyhM6N6tafNBt8"
TELEGRAM_CHAT_ID = "-1002814094030"

# مدل FinBERT برای تحلیل سنتیمنت
sentiment_pipeline = pipeline("sentiment-analysis", model="ProsusAI/finbert")

def get_investing_forex_headlines():
    url = "https://www.investing.com/news/forex-news"
    headers = {
        "User-Agent": "Mozilla/5.0",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # پیدا کردن تمام بلوک‌های خبر
        blocks = soup.find_all("div", class_="news-analysis-v2_content__z0iLP")

        headlines = []

        for block in blocks[:5]:  # فقط 5 خبر اول
            title_tag = block.find("a", attrs={"data-test": "article-title-link"})
            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            href = title_tag.get("href")
            full_link = "https://www.investing.com" + href if href.startswith("/") else href

            headlines.append((title, full_link))

        return headlines

    except Exception as e:
        print("خطا در دریافت خبرها از Investing.com:", e)
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
        print("خطا در ارسال به تلگرام:", e)

def main():
    headlines = get_investing_forex_headlines()
    if not headlines:
        send_telegram_message("⛔️ هیچ تیتر خبری یافت نشد.")
        return

    message = f"🌐 تحلیل سنتیمنت جفت‌ارزها \n\n🔢 تعداد عناوین: {len(headlines)}\n"
    sentiment_score = 0

    for title, link in headlines:
        sentiment = analyze_sentiment(title)
        message += f"\n▶️ {title}\n🔗 {link}\n⚖️ احساس: {sentiment}\n"

        if sentiment == "مثبت ✅":
            sentiment_score += 1
        elif sentiment == "منفی ❌":
            sentiment_score -= 1

    message += f"\n۰ امتیاز سنتیمنت: {sentiment_score}\n\n📡 بروزرسانی خودکار هر 15 دقیقه"
    send_telegram_message(message)

if __name__ == "__main__":
    main()
