import matplotlib.pyplot as plt
import numpy as np

from fitinera.results import SimulationResult
from scipy.interpolate import make_interp_spline

def format_money(value, tick_number):
    if value >= 1_000_000_000:
        return f'${(value/1_000_000_000):.2f}B'
    if value >= 1_000_000:
        return f'${(value/1_000_000):.2f}M'
    if value >= 1_000:
        return f'${(value/1_000):.2f}k'
    return f'${value:.2f}'

def smooth_data(x, y, smooth_x):
    spl = make_interp_spline(x, y, k=3) # Cubic spline
    return spl(smooth_x)

class Charting:
    def __init__(self, simulation_result: SimulationResult):
        self.ages = []
        self.asset_balances = []
        self.total_active_incomes = []
        self.total_spendings = []
        self.total_asset_growths = []
        self.total_retirement_incomes = []

        for turn in simulation_result.history:
          flattened_turn_age: float = turn.current_age.year + turn.current_age.month / 12
          self.ages.append(flattened_turn_age)
          self.asset_balances.append(turn.total_next_assets)
          self.total_active_incomes.append(turn.current_income_breakdown.total_active)
          self.total_spendings.append(turn.total_expenses)
          self.total_asset_growths.append(turn.total_asset_growth)
          self.total_retirement_incomes.append(turn.total_asset_growth + turn.current_income_breakdown.total_passive)

        self.retirement_age = None
        if simulation_result.scenario.retirement_goal and simulation_result.scenario.retirement_goal.retirement_age:
            ra = simulation_result.scenario.retirement_goal.retirement_age
            self.retirement_age = ra.year + ra.month / 12

    def plot_retirement_assets(self):

        plt.figure(figsize=(10, 6))

        # 1. Create a "smooth" curve using Spline Interpolation
        # We create 300 points between the min and max year for a fluid look
        ages_new = np.linspace(min(self.ages), max(self.ages), 300)
        balance_smooth = smooth_data(self.ages, self.asset_balances, ages_new)

        # 2. Plot the filled area (using the smooth data)
        plt.fill_between(ages_new, balance_smooth, color='skyblue', alpha=0.3)

        # 3. Plot the line (No markers, smooth data)
        plt.plot(ages_new, balance_smooth, color='dodgerblue', linewidth=2, label='Year End Savings Balance')

        # 4. Display retirement age as a vertical dotted line if provided
        if self.retirement_age is not None:
            plt.axvline(x=self.retirement_age, color="#000000AC", linestyle=':', linewidth=2, label='Retirement Age')

        plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(format_money))
        plt.title('Assets', fontsize=18, fontweight='bold', loc='left', pad=25)
        plt.xlabel('Age', fontsize=12, labelpad=10)
        plt.grid(True, linestyle='--', alpha=0.4)
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False, fontsize=10)

        plt.xlim(min(self.ages), max(self.ages))
        plt.ylim(0, max(self.asset_balances) * 1.1)
        plt.tight_layout()
        plt.show()

    def plot_cash_flows(self):
        """
        Generates a smooth multi-line chart for a scenario result's 'Cash Flows'.
        """
        ages = self.ages
        spending = self.total_spendings
        total_active_income = self.total_active_incomes
        total_growth = self.total_asset_growths
        total_retirement_income = self.total_retirement_incomes
        retirement_age = self.retirement_age

        plt.figure(figsize=(10, 6))
        
        # 1. Create high-density x-values for smooth curves
        ages_smooth = np.linspace(min(ages), max(ages), 300)

        # 2. Smooth all three data series
        spending_s = smooth_data(ages, spending, ages_smooth)
        total_active_income_s = smooth_data(ages, total_active_income, ages_smooth)
        total_growth_s = smooth_data(ages, total_growth, ages_smooth)
        total_retirement_income_s = smooth_data(ages, total_retirement_income, ages_smooth)

        # 3. Plotting with colors matching the website's palette
        plt.plot(ages_smooth, spending_s, color="#d8450b", linewidth=2, label='Expenses')
        plt.plot(ages_smooth, total_active_income_s, color="#04961d", linewidth=2, label='Active Income')
        plt.plot(ages_smooth, total_growth_s, color="#7ef3f7", linewidth=2, label='Total Asset Growth')
        plt.plot(ages_smooth, total_retirement_income_s, color='#3498db', linewidth=2, label='Total Retirement Income')
        # 4. Display retirement age as a vertical dotted line if provided
        if retirement_age is not None:
            plt.axvline(x=retirement_age, color="#000000AC", linestyle=':', linewidth=2, label='Retirement Age')
        
        plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(format_money))

        # 5. Styling and Layout
        plt.title('Cash Flows', fontsize=18, fontweight='bold', loc='left', pad=25)
        plt.xlabel('Age', fontsize=12, labelpad=10)
        plt.grid(True, linestyle='-', alpha=0.2)
            # Place legend at the bottom to mimic the site
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), 
                    ncol=2, frameon=False, fontsize=10)

        # Clean up edges
        plt.xlim(min(ages), max(ages))
        plt.ylim(0, max(max(spending), max(total_growth), max(total_active_income), max(total_retirement_income)) * 1.1)
        
        # Modern look: hide top and right spines
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)

        plt.tight_layout()
        plt.show()
