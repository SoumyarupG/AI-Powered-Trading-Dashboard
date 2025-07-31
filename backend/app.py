from fastapi import FastAPI
import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
from prophet import Prophet
from transformers import pipeline

app = FastAPI()

# Sentiment pipeline (HuggingFace)
sentiment_pipeline = pipeline("sentiment-analysis")

@app.get("/predict/{ticker}")
def predict_stock(ticker: str):
    try:
        # Fetch historical stock data
        stock = yf.Ticker(ticker)
        hist = stock.history(period="6mo")

        if hist.empty:
            return {"error": f"No data found for ticker: {ticker}"}

        # Prepare data for Prophet
        df = hist.reset_index()
        df['ds'] = df['Date'].dt.tz_localize(None)  # Remove timezone
        df['y'] = df['Close']

        # Train Prophet model
        model = Prophet(daily_seasonality=True)
        model.fit(df[['ds', 'y']])

        # Forecast next 7 days
        future = model.make_future_dataframe(periods=7)
        forecast = model.predict(future)

        next_day_prediction = round(forecast.iloc[-7]['yhat'], 2)
        last_price = round(hist['Close'].iloc[-1], 2)

        # Technical indicators
        rsi = round(RSIIndicator(close=hist['Close']).rsi().iloc[-1], 2)
        bb = BollingerBands(close=hist['Close'])
        upper_band = round(bb.bollinger_hband().iloc[-1], 2)
        lower_band = round(bb.bollinger_lband().iloc[-1], 2)
        volatility = round(((upper_band - lower_band) / last_price) * 100, 2)

        # News sentiment (mock for demo)
        news = [
            "Apple Q3 earnings beat expectations",
            "Analysts warn of market volatility",
            "Apple announces new product launch next week"
        ]
        sentiment_results = [{"headline": h, "sentiment": sentiment_pipeline(h)[0]} for h in news]

        # AI Insight (rule-based for demo)
        if rsi < 30:
            ai_insight = "RSI is low, stock may be oversold. Consider BUY."
        elif rsi > 70:
            ai_insight = "RSI is high, stock may be overbought. Consider SELL."
        else:
            ai_insight = "RSI is neutral, HOLD recommended."

        # Return structured response
        return {
            "ticker": ticker.upper(),
            "last_price": last_price,
            "prediction": next_day_prediction,
            "volatility": volatility,
            "rsi": rsi,
            "upper_band": upper_band,
            "lower_band": lower_band,
            "forecast": forecast.tail(7)[['ds', 'yhat']].to_dict(orient='records'),
            "sentiment": sentiment_results,
            "ai_insight": ai_insight
        }

    except Exception as e:
        return {"error": str(e)}
