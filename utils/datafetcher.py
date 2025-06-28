import streamlit as st
import yfinance as yf
from datetime import datetime

def fetch_data(selected_index):
    """Fetches the latest price for the given index."""
    try:
        data = yf.download(selected_index, interval='1m', period='1d')
        if not data.empty:
            latest_price = round(data['Close'].iloc[-1], 1)
            return latest_price
        else:
            return ["No price data"]
    except Exception as e:
        return [f"Error: {e}"]

def fetch_expiry_dates(selected_index):
    """Retrieves available options expiry dates for the selected index."""
    try:
        ticker = yf.Ticker(selected_index)
        expiry_list = ticker.options
        return expiry_list if expiry_list else ["No options available"]
    except Exception as e:
        st.sidebar.warning(f"Couldn't fetch expiry dates for {selected_index}: {e}")
        return ["Error fetching expiry dates"]

def calculate_time_to_expiry(expiration_date):
    """Computes time to expiry in trading years (252 days)."""
    today = datetime.now().date()
    expiry = datetime.strptime(expiration_date, "%Y-%m-%d").date()
    return (expiry - today).days / 252.0

def get_option_strike_prices(ticker):
    """Returns available strike prices for calls and puts across all expiry dates."""
    strike_data = {}
    try:
        stock = yf.Ticker(ticker)
        for expiry in stock.options:
            try:
                chain = stock.option_chain(expiry)
                calls = chain.calls['strike'].tolist() if hasattr(chain, 'calls') else []
                puts = chain.puts['strike'].tolist() if hasattr(chain, 'puts') else []
                strike_data[expiry] = {'calls': calls, 'puts': puts}
            except Exception as e:
                st.sidebar.warning(f"Could not fetch strikes for {expiry}: {e}")
    except Exception as e:
        st.sidebar.warning(f"Failed to load options for {ticker}: {e}")

    return strike_data
