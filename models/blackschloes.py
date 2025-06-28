import numpy as np
from scipy.stats import norm
import plotly.graph_objects as go

class BlackSchloes:
    def __init__(self, r, s, k, t, sigma):
        self.r = r            # risk-free rate
        self.s = s            # spot price
        self.k = k            # strike price
        self.t = t            # time to maturity (in years)
        self.sigma = sigma    # volatility

    def option(self, option_type):
        d1, d2 = self._calculate_d1_d2()
        if option_type.lower() == 'call':
            return self.s * norm.cdf(d1) - self.k * np.exp(-self.r * self.t) * norm.cdf(d2)
        elif option_type.lower() == 'put':
            return self.k * np.exp(-self.r * self.t) * norm.cdf(-d2) - self.s * norm.cdf(-d1)
        else:
            raise ValueError("Invalid option type. Must be 'call' or 'put'.")

    def _calculate_d1_d2(self):
        if self.t is None or self.t <= 0 or self.sigma is None or self.sigma <= 0:
            raise ValueError("Invalid time to expiry or volatility.")
        d1 = (np.log(self.s / self.k) + (self.r + 0.5 * self.sigma ** 2) * self.t) / (self.sigma * np.sqrt(self.t))
        d2 = d1 - self.sigma * np.sqrt(self.t)
        return d1, d2

    def greek_visualisation(self, option_type, greek):
        steps = 100
        x = np.linspace(self.s * 0.5, self.s * 1.5, steps)
        y = []

        for s_new in x:
            bs = BlackSchloes(self.r, s_new, self.k, self.t, self.sigma)
            value = getattr(bs, greek)(option_type)
            y.append(value)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=greek))
        fig.update_layout(
            title=f"{greek.capitalize()} vs Spot Price",
            xaxis_title="Spot Price",
            yaxis_title=greek.capitalize(),
            template="plotly_dark"
        )
        return fig

    # --- Greeks ---
    def delta(self, option_type):
        d1, _ = self._calculate_d1_d2()
        if option_type.lower() == 'call':
            return norm.cdf(d1)
        elif option_type.lower() == 'put':
            return norm.cdf(d1) - 1

    def gamma(self, _):
        d1, _ = self._calculate_d1_d2()
        return norm.pdf(d1) / (self.s * self.sigma * np.sqrt(self.t))

    def theta(self, option_type):
        d1, d2 = self._calculate_d1_d2()
        first_term = - (self.s * norm.pdf(d1) * self.sigma) / (2 * np.sqrt(self.t))
        if option_type.lower() == 'call':
            second_term = self.r * self.k * np.exp(-self.r * self.t) * norm.cdf(d2)
            return (first_term - second_term) / 252  # daily theta
        elif option_type.lower() == 'put':
            second_term = self.r * self.k * np.exp(-self.r * self.t) * norm.cdf(-d2)
            return (first_term + second_term) / 252

    def vega(self, _):
        d1, _ = self._calculate_d1_d2()
        return self.s * norm.pdf(d1) * np.sqrt(self.t) / 100  # per 1% change

    def rho(self, option_type):
        _, d2 = self._calculate_d1_d2()
        if option_type.lower() == 'call':
            return self.k * self.t * np.exp(-self.r * self.t) * norm.cdf(d2) / 100
        elif option_type.lower() == 'put':
            return -self.k * self.t * np.exp(-self.r * self.t) * norm.cdf(-d2) / 100

    def vanna(self, _):
        d1, d2 = self._calculate_d1_d2()
        return np.exp(-d1 ** 2 / 2) * d2 / (self.sigma * np.sqrt(2 * np.pi))

    def vomma(self, _):
        d1, d2 = self._calculate_d1_d2()
        return self.s * norm.pdf(d1) * np.sqrt(self.t) * d1 * d2 / self.sigma

    def charm(self, option_type):
        d1, d2 = self._calculate_d1_d2()
        term = norm.pdf(d1) * (2 * self.r * self.t - d2 * self.sigma * np.sqrt(self.t)) / (2 * self.t * self.sigma * np.sqrt(self.t))
        if option_type.lower() == 'call':
            return -term / 252
        elif option_type.lower() == 'put':
            return term / 252

    def zomma(self, _):
        d1, d2 = self._calculate_d1_d2()
        gamma_val = self.gamma('call')  # doesn't depend on type
        return gamma_val * ((d1 * d2 - 1) / self.sigma)

    # --- Monte Carlo (for reuse) ---
    def monte_carlo_pricing(self, num_simulations):
        z = np.random.standard_normal(num_simulations)
        st = self.s * np.exp((self.r - 0.5 * self.sigma ** 2) * self.t + self.sigma * np.sqrt(self.t) * z)
        payoff = np.maximum(st - self.k, 0)  # call
        return np.exp(-self.r * self.t) * np.mean(payoff)

    # --- Binomial Tree (American Option Pricing) ---
    def american_option_pricing(self, s, k, t, r, n, sigma, option_type):
        dt = t / n
        u = np.exp(sigma * np.sqrt(dt))
        d = 1 / u
        p = (np.exp(r * dt) - d) / (u - d)
        disc = np.exp(-r * dt)

        prices = [s * (u ** j) * (d ** (n - j)) for j in range(n + 1)]
        if option_type == 'call':
            values = [max(price - k, 0) for price in prices]
        else:
            values = [max(k - price, 0) for price in prices]

        for i in range(n - 1, -1, -1):
            for j in range(i + 1):
                spot = s * (u ** j) * (d ** (i - j))
                exercise = max((spot - k) if option_type == 'call' else (k - spot), 0)
                values[j] = max(exercise, disc * (p * values[j + 1] + (1 - p) * values[j]))

        return values[0]
