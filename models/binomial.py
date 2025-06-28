import numpy as np
import plotly.graph_objects as go

def visualize_binomial_tree(S0, K, T, sigma, r, steps, option_type='Call'):
    dt = T / steps
    u = np.exp(sigma * np.sqrt(dt))   # Up factor
    d = 1 / u                         # Down factor
    p = (np.exp(r * dt) - d) / (u - d)  # Risk-neutral probability

    # Generate asset prices at each node
    prices = np.zeros((steps + 1, steps + 1))
    for i in range(steps + 1):
        for j in range(i + 1):
            prices[j, i] = S0 * (u ** (i - j)) * (d ** j)

    # Plotting
    fig = go.Figure()

    # Add price nodes
    for i in range(steps + 1):
        for j in range(i + 1):
            fig.add_trace(go.Scatter(
                x=[i],
                y=[prices[j, i]],
                mode='markers+text',
                marker=dict(size=8, color='royalblue'),
                text=[f"{prices[j, i]:.2f}"],
                textposition='top center',
                showlegend=False
            ))

    # Add lines connecting nodes
    for i in range(steps):
        for j in range(i + 1):
            fig.add_trace(go.Scatter(
                x=[i, i+1],
                y=[prices[j, i], prices[j, i+1]],
                mode='lines',
                line=dict(color='gray', width=1),
                showlegend=False
            ))
            fig.add_trace(go.Scatter(
                x=[i, i+1],
                y=[prices[j, i], prices[j+1, i+1]],
                mode='lines',
                line=dict(color='gray', width=1),
                showlegend=False
            ))

    fig.update_layout(
        title=f"Binomial Tree for {option_type.capitalize()} Option",
        xaxis_title="Step",
        yaxis_title="Price",
        height=600,
        width=800
    )

    return fig
