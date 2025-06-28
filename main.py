import streamlit as st
from models.blackschloes import BlackSchloes
from models.monte_carlo import monte_carlo_pricing_visualization
from models.binomial import visualize_binomial_tree
from utils.datafetcher import fetch_data, fetch_expiry_dates, get_option_strike_prices, calculate_time_to_expiry
import pandas as pd

# -- Page Setup & Styling --
st.set_page_config(page_title="Options Pricing Toolkit", layout="wide")

st.markdown("""
    <style>
        .stApp {
            background-image: url("https://www.google.com/imgres?q=options%20pricing%20wallpaper&imgurl=https%3A%2F%2Fmedia.istockphoto.com%2Fid%2F913219882%2Fphoto%2Ffinancial-graph-on-technology-abstract-background.jpg%3Fs%3D612x612%26w%3D0%26k%3D20%26c%3D0P0vbPiPsHOH_uzZEzL6CmpZwIDIArtNj_PsQVwxkEM%3D&imgrefurl=https%3A%2F%2Fwww.istockphoto.com%2Fphotos%2Foptions-trading&docid=cSEfhZUD3oIkJM&tbnid=Fv0AE_7xg4BqnM&vet=12ahUKEwj7lP_N5JSOAxXdafUHHW7nDhsQM3oECBoQAA..i&w=612&h=408&hcb=2&ved=2ahUKEwj7lP_N5JSOAxXdafUHHW7nDhsQM3oECBoQAA");
            background-size: cover;
            background-attachment: fixed;
            color: #f0f0f0;
        }

        .title {
            font-size: 2.5rem;
            color: #f9f9f9;
            font-weight: 700;
            text-shadow: 1px 1px 2px #000;
        }

        .section-header {
            font-size: 1.5rem;
            color: #f9f9f9;
            margin-top: 1rem;
            border-bottom: 1px solid #f9f9f9;
            text-shadow: 1px 1px 2px #000;
        }

        .stSidebar, .sidebar .sidebar-content {
            background-color: rgba(0, 0, 0, 0.7);
        }

        .stSelectbox > div, .stRadio > div {
            color: #ffffff !important;
        }
    </style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<div class="title">📈 Options Pricing Toolkit</div>', unsafe_allow_html=True)

    # -- Asset Selection --
    indices_names = {
        'AAPL': 'Apple Inc.', 'NVDA': 'NVIDIA Corporation', '^RUT': 'Russell 2000 Index',
        '^VIX': 'CBOE Volatility Index (VIX)', 'IWM': 'iShares Russell 2000 ETF',
        'TSLA': 'Tesla, Inc.', 'QQQ': 'Invesco QQQ Trust', '^SPX': 'S&P 500 Index'
    }

    st.sidebar.header("📊 Select Your Instrument")
    selected_index = st.sidebar.selectbox("Select an underlying asset", options=list(indices_names.keys()))
    st.sidebar.write(f"🧾 Selected: **{indices_names[selected_index]}**")

    expiration_date = st.sidebar.selectbox("Choose Expiry", fetch_expiry_dates(selected_index))
    nifty_price_data = fetch_data(selected_index)

    # -- Price Validation --
    if isinstance(nifty_price_data, pd.Series) and not nifty_price_data.empty:
        nifty_price = float(nifty_price_data.iloc[-1])
    else:
        nifty_price = 100.0

    # -- Strike Selection --
    strike_prices_data = get_option_strike_prices(selected_index)
    call_strikes = strike_prices_data.get(expiration_date, {}).get('calls', [])
    call_strikes = [float(x) for x in call_strikes if x is not None]

    closest_strike = min(call_strikes, key=lambda x: abs(x - nifty_price)) if call_strikes else 100.0
    selected_strike = st.sidebar.selectbox("Choose Strike", sorted(call_strikes), index=call_strikes.index(closest_strike) if closest_strike in call_strikes else 0)
    selected_strike = float(selected_strike)

    # -- Time to Expiry --
    time_to_expiry = calculate_time_to_expiry(expiration_date)

    st.markdown('<div class="section-header">🛠️ Choose Your Strategy</div>', unsafe_allow_html=True)
    strategy = st.sidebar.radio("Pricing Strategy", ['Black Scholes Pricing', 'Monte Carlo Simulation', 'Binomial Tree Forecasting'])

    # -- Strategy Handlers --
    if strategy == 'Black Scholes Pricing':
        option_type = st.sidebar.radio("Option Type", ['Call', 'Put'])
        volatility = st.sidebar.slider("Volatility (%)", 5, 100, 20)
        risk_free_rate = st.sidebar.slider("Risk Free Rate (%)", 0, 20, 5)
        time_days = st.sidebar.slider("Time to Expiry (days)", 1, 365, int(time_to_expiry * 252))
        time = time_days / 252

        bs = BlackSchloes(risk_free_rate / 100, nifty_price, selected_strike, time, volatility / 100)
        price = bs.option(option_type)
        st.success(f"💰 Option Price: **{price:.2f}**")

        if st.button("🔍 Visualize Greeks"):
            cols = st.columns(3)
            greeks = ['delta', 'gamma', 'theta', 'vega', 'rho', 'vanna', 'vomma', 'charm', 'zomma']
            for i, greek in enumerate(greeks):
                with cols[i % 3]:
                    fig = bs.greek_visualisation(option_type, greek)
                    st.plotly_chart(fig, use_container_width=True)

    elif strategy == 'Monte Carlo Simulation':
        num_simulations = st.sidebar.slider("Simulations", 500, 5000, 1000, step=100)
        num_steps = st.sidebar.slider("Steps", 50, 500, 252, step=10)
        volatility = st.sidebar.slider("Volatility (%)", 5, 100, 20)
        risk_free_rate = st.sidebar.slider("Risk Free Rate (%)", 0, 20, 5)
        time_days = st.sidebar.slider("Time to Expiry (days)", 1, 365, int(time_to_expiry * 252))
        time = time_days / 252

        bs = BlackSchloes(risk_free_rate / 100, nifty_price, selected_strike, time, volatility / 100)
        price = bs.monte_carlo_pricing(num_simulations)
        st.success(f"📉 Monte Carlo Price: **{price:.2f}**")

        if st.button("📊 Show Simulation"):
            fig = monte_carlo_pricing_visualization(nifty_price, selected_strike, time, volatility / 100, risk_free_rate / 100, num_simulations, num_steps)
            st.plotly_chart(fig, use_container_width=True)

    else:
        option_type = st.sidebar.radio("Option Type", ['Call', 'Put'])
        num_steps = st.sidebar.slider("Tree Steps", 10, 100, 10, step=10)
        volatility = st.sidebar.slider("Volatility (%)", 5, 100, 20)
        risk_free_rate = st.sidebar.slider("Risk Free Rate (%)", 0, 20, 5)
        time_days = st.sidebar.slider("Time to Expiry (days)", 1, 365, int(time_to_expiry * 252))
        time = time_days / 252

        bs = BlackSchloes(risk_free_rate / 100, nifty_price, selected_strike, time, volatility / 100)
        price = bs.american_option_pricing(nifty_price, selected_strike, time, risk_free_rate / 100, num_steps, volatility / 100, option_type.lower())
        st.success(f"📊 Binomial Tree Price: **{price:.2f}**")

        if st.button("🌲 Show Binomial Tree"):
            fig = visualize_binomial_tree(nifty_price, selected_strike, time, volatility / 100, risk_free_rate / 100, num_steps, option_type)
            st.plotly_chart(fig, use_container_width=True)

    st.sidebar.markdown("---")

if __name__ == "__main__":
    main()
