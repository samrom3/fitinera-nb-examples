import matplotlib.pyplot as plt
import numpy as np

from fitinera.results import SimulationResult
from scipy.interpolate import make_interp_spline
from typing import List, Optional

def format_money(value: float, _) -> str:
    """
    Formats numerical values into human-readable currency strings (e.g., $1.20M).

    :param value: The numerical value to be formatted.
    :param _: The position of the tick (not used in formatting but required by FuncFormatter).
    :returns: A formatted string representation of the value.
    """
    if value >= 1_000_000_000:
        return f'${(value/1_000_000_000):.2f}B'
    if value >= 1_000_000:
        return f'${(value/1_000_000):.2f}M'
    if value >= 1_000:
        return f'${(value/1_000):.2f}k'
    return f'${value:.2f}'

def smooth_data(x, y, smooth_x) -> np.ndarray:
    """
    Applies cubic spline interpolation to smooth data points.

    :param x: Original x-axis data points.
    :param y: Original y-axis data points.
    :param smooth_x: New x-axis points for the interpolated curve.
    :returns: Interpolated y-axis values.
    """
    spl = make_interp_spline(x, y, k=3) # Cubic spline
    return spl(smooth_x)

class Charting:
    """
    A utility class for visualizing Fitinera simulation results using Matplotlib.
    """
    def __init__(self, simulation_result: SimulationResult):
        """
        Initializes the Charting class by extracting and flattening history data from a SimulationResult.

        :param simulation_result: The SimulationResult object containing the data to be visualized.
        """
        self._ages: List[float] = []
        self._asset_balances: List[float] = []
        self._total_active_incomes: List[float] = []
        self._total_spendings: List[float] = []
        self._total_asset_growths: List[float] = []
        self._total_retirement_incomes: List[float] = []

        for turn in simulation_result.history:
          flattened_turn_age: float = turn.current_age.year + turn.current_age.month / 12
          self._ages.append(flattened_turn_age)
          self._asset_balances.append(turn.total_next_assets)
          self._total_active_incomes.append(turn.current_income_breakdown.total_active)
          self._total_spendings.append(turn.total_expenses)
          self._total_asset_growths.append(turn.total_asset_growth)
          self._total_retirement_incomes.append(turn.total_asset_growth + turn.current_income_breakdown.total_passive)

        self._retirement_age: Optional[float] = None
        if simulation_result.scenario.retirement_goal and simulation_result.scenario.retirement_goal.retirement_age:
            ra = simulation_result.scenario.retirement_goal.retirement_age
            self._retirement_age = ra.year + ra.month / 12

    def plot_retirement_assets(self):
        """
        Generates a smooth area chart showing the progression of total asset balances over time.
        """
        plt.figure(figsize=(10, 6))

        # 1. Create a "smooth" curve using Spline Interpolation
        # We create 300 points between the min and max year for a fluid look
        ages_new = np.linspace(min(self._ages), max(self._ages), 300)
        balance_smooth = smooth_data(self._ages, self._asset_balances, ages_new)

        # 2. Plot the filled area (using the smooth data)
        plt.fill_between(ages_new, balance_smooth, color='skyblue', alpha=0.3)

        # 3. Plot the line (No markers, smooth data)
        plt.plot(ages_new, balance_smooth, color='dodgerblue', linewidth=2, label='Year End Savings Balance')

        # 4. Display retirement age as a vertical dotted line if provided
        if self._retirement_age is not None:
            plt.axvline(x=self._retirement_age, color="#000000AC", linestyle=':', linewidth=2, label='Retirement Age')

        plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(format_money))
        plt.title('Assets', fontsize=18, fontweight='bold', loc='left', pad=25)
        plt.xlabel('Age', fontsize=12, labelpad=10)
        plt.grid(True, linestyle='--', alpha=0.4)
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False, fontsize=10)

        plt.xlim(min(self._ages), max(self._ages))
        plt.ylim(0, max(self._asset_balances) * 1.1)
        plt.tight_layout()
        plt.show()

    def plot_cash_flows(self):
        """
        Generates a smooth multi-line chart for a scenario result's 'Cash Flows'.
        """
        plt.figure(figsize=(10, 6))
        
        # 1. Create high-density x-values for smooth curves
        ages_smooth = np.linspace(min(self._ages), max(self._ages), 300)

        # 2. Smooth all three data series
        spending_s = smooth_data(self._ages, self._total_spendings, ages_smooth)
        total_active_income_s = smooth_data(self._ages, self._total_active_incomes, ages_smooth)
        total_growth_s = smooth_data(self._ages, self._total_asset_growths, ages_smooth)
        total_retirement_income_s = smooth_data(self._ages, self._total_retirement_incomes, ages_smooth)

        # 3. Plotting with colors matching the website's palette
        plt.plot(ages_smooth, spending_s, color="#d8450b", linewidth=2, label='Expenses')
        plt.plot(ages_smooth, total_active_income_s, color="#04961d", linewidth=2, label='Active Income')
        plt.plot(ages_smooth, total_growth_s, color="#7ef3f7", linewidth=2, label='Total Asset Growth')
        plt.plot(ages_smooth, total_retirement_income_s, color='#3498db', linewidth=2, label='Total Retirement Income')

        # 4. Display retirement age as a vertical dotted line if provided
        if self._retirement_age is not None:
            plt.axvline(x=self._retirement_age, color="#000000AC", linestyle=':', linewidth=2, label='Retirement Age')
        
        plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(format_money))

        # 5. Styling and Layout
        plt.title('Cash Flows', fontsize=18, fontweight='bold', loc='left', pad=25)
        plt.xlabel('Age', fontsize=12, labelpad=10)
        plt.grid(True, linestyle='-', alpha=0.2)
            # Place legend at the bottom to mimic the site
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), 
                    ncol=2, frameon=False, fontsize=10)

        # Clean up edges
        plt.xlim(min(self._ages), max(self._ages))
        plt.ylim(0, max(
            max(self._total_spendings),
            max(self._total_asset_growths),
            max(self._total_active_incomes),
            max(self._total_retirement_incomes)
        ) * 1.1)
        
        # Modern look: hide top and right spines
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)

        plt.tight_layout()
        plt.show()

    def plot_all(self):
        """
        Generates all available plots for the simulation results.
        """
        self.plot_retirement_assets()
        self.plot_cash_flows()
