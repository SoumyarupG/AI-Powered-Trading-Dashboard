import streamlit as st
import requests
import plotly.graph_objects as go

API_URL = "http://127.0.0.1:8000"  # Backend URL

st.set_page_config(page_title="AI Fintech SaaS", layout="wide")
st.title("📈 AI-Powered Trading Dashboard")

ticker = st.text_input("Enter Stock Symbol (e.g. AAPL):", "AAPL")

if st.button("Analyze"):
    with st.spinner("Fetching market data..."):
        try:
            url = f"{API_URL}/predict/{ticker}"
            data = requests.get(url).json()

            if "error" in data:
                st.error(data["error"])
            else:
                st.subheader(f"{ticker.upper()} Analysis")

                # Display metrics safely
                col1, col2, col3 = st.columns(3)
                col1.metric("Current Price", f"${data.get('last_price', 'N/A')}")
                col2.metric("Next-Day Forecast", f"${data.get('prediction', 'N/A')}")
                col3.metric("Volatility", f"{data.get('volatility', 'N/A')}%")

                st.metric("RSI (14-day)", data.get('rsi', 'N/A'))
                st.write(f"Bollinger Bands: Upper={data.get('upper_band', 'N/A')}, Lower={data.get('lower_band', 'N/A')}")

                # Forecast Plot
                if "forecast" in data:
                    st.subheader("📊 7-Day Price Forecast")
                    forecast = data["forecast"]
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=[f['ds'] for f in forecast],
                        y=[f['yhat'] for f in forecast],
                        mode='lines+markers',
                        name='Forecast'
                    ))
                    st.plotly_chart(fig, use_container_width=True)

                # News Sentiment
                if "sentiment" in data:
                    st.subheader("📰 News Sentiment")
                    for s in data["sentiment"]:
                        st.write(f"- **{s['headline']}** ({s['sentiment']['label']}: {s['sentiment']['score']:.2f})")

                # AI Recommendation
                st.success(f"🤖 AI Recommendation: {data.get('ai_insight', 'No AI insight available')}")

        except Exception as e:
            st.error(f"Error: {e}")
