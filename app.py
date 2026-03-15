import streamlit as st
import ccxt
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="Crypto Signal Bot", layout="wide")

st.title("💹 Live Crypto Buy/Sell Signals")
st.sidebar.header("Settings")

# Sidebar inputs
symbol = st.sidebar.text_input("Crypto Pair (e.g. BTC/USDT)", value="BTC/USDT")
timeframe = st.sidebar.selectbox("Timeframe", ("15m", "1h", "4h", "1d"), index=1)
sma_short = st.sidebar.number_input("Short SMA (Fast)", value=9)
sma_long = st.sidebar.number_input("Long SMA (Slow)", value=21)

# Exchange Initialization
exchange = ccxt.binance()

def get_data(symbol, timeframe):
    bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=100)
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

try:
    # Fetch Data
    df = get_data(symbol, timeframe)
    
    # Calculate Indicators
    df['SMA_S'] = ta.sma(df['close'], length=sma_short)
    df['SMA_L'] = ta.sma(df['close'], length=sma_long)
    df['RSI'] = ta.rsi(df['close'], length=14)

    # Current Stats
    last_price = df['close'].iloc[-1]
    prev_close = df['close'].iloc[-2]
    price_diff = last_price - prev_close

    # Columns for metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Live Price", f"${last_price:,.2f}", f"{price_diff:,.2f}")
    col2.metric("RSI (14)", f"{df['RSI'].iloc[-1]:.2f}")
    
    # Signal Logic
    current_sma_s = df['SMA_S'].iloc[-1]
    current_sma_l = df['SMA_L'].iloc[-1]
    prev_sma_s = df['SMA_S'].iloc[-2]
    prev_sma_l = df['SMA_L'].iloc[-2]

    if prev_sma_s <= prev_sma_l and current_sma_s > current_sma_l:
        signal = "🚀 BUY"
        color = "green"
    elif prev_sma_s >= prev_sma_l and current_sma_s < current_sma_l:
        signal = "⚠️ SELL"
        color = "red"
    else:
        signal = "😴 HOLD / NO SIGNAL"
        color = "gray"

    col3.markdown(f"### Signal: :{color}[{signal}]")

    # Interactive Chart (Plotly)
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df['timestamp'], open=df['open'], high=df['high'], low=df['low'], close=df['close'], name='Market Data'))
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['SMA_S'], line=dict(color='orange', width=1.5), name=f'SMA {sma_short}'))
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['SMA_L'], line=dict(color='blue', width=1.5), name=f'SMA {sma_long}'))
    
    fig.update_layout(title=f"{symbol} Live Chart", yaxis_title="Price (USDT)", height=600)
    st.plotly_chart(fig, use_container_width=True)

    # Show Data Table
    if st.checkbox("Show Raw Data"):
        st.write(df.tail(10))

except Exception as e:
    st.error(f"Error fetching data: {e}. Please check the symbol name.")

st.info("Note: This is a demo bot based on SMA Crossover. Always do your own research before trading.")
