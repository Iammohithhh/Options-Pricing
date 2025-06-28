import numpy as np
import plotly.graph_objects as go

def monte_carlo_pricing_visualization(spot_price, strike_price, time_to_expiry, volatility, risk_free_rate, num_simulations=500, num_steps=252):
    dt = time_to_expiry / num_steps
    price_paths = np.zeros((num_steps, num_simulations))
    price_paths[0] = spot_price

    for step in range(1, num_steps):
        z = np.random.standard_normal(num_simulations)
        growth = (risk_free_rate - 0.5 * volatility**2) * dt
        diffusion = volatility * np.sqrt(dt) * z
        price_paths[step] = price_paths[step - 1] * np.exp(growth + diffusion)

    time_points = np.linspace(0, time_to_expiry, num_steps)
    fig = go.Figure()

    for i in range(num_simulations):
        fig.add_trace(go.Scatter(x=time_points, y=price_paths[:, i], mode='lines', line=dict(width=1)))

    fig.update_layout(
        title="Monte Carlo Simulation: Asset Price Paths",
        xaxis_title="Time (Years)",
        yaxis_title="Asset Price",
        showlegend=False,
        template="plotly_white"
    )

    return fig
