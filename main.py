from full_fred.fred import Fred
import pandas as pd
import openai
import datetime
import pytz
import re
import os

# Not included the analysis algo - can't give away all the sauce for free :)
from WBAnalysisModule import eocp

INTERVAL_1_MINUTE = "1m"
INTERVAL_5_MINUTES = "5m"
INTERVAL_15_MINUTES = "15m"
INTERVAL_30_MINUTES = "30m"
INTERVAL_1_HOUR = "1h"
INTERVAL_2_HOURS = "2h"
INTERVAL_4_HOURS = "4h"
INTERVAL_1_DAY = "1d"
INTERVAL_1_WEEK = "1W"
INTERVAL_1_MONTH = "1M"


class EconomicRiskAnalyzer:
    def __init__(self, fred_api_key_file):
        self.fred = Fred(api_key_file=fred_api_key_file)

    def analyze_unemployment_rate(self, series_code='UNRATE'):
        data = self.fred.get_series_df(series_code)
        unemployment_rate = float(data['value'].iloc[-1])
        risk = min(max((unemployment_rate - 4) / 6, 0), 1)
        return risk * 100, unemployment_rate

    def analyze_inflation(self, series_code='CPIAUCSL'):
        data = self.fred.get_series_df(series_code)
        data['value'] = pd.to_numeric(data['value'])
        inflation_rate = (data['value'].iloc[-1] - data['value'].iloc[-12]) / data['value'].iloc[-12] * 100
        risk = min(max((inflation_rate - 2) / 3, 0), 1)
        return risk * 100, inflation_rate

    def analyze_interest_rate(self, series_code='FEDFUNDS'):
        data = self.fred.get_series_df(series_code)
        data['value'] = pd.to_numeric(data['value'])
        interest_rate = data['value'].iloc[-1]
        risk = min(max(abs(interest_rate - 2.75) / 2.25, 0), 1)
        return risk * 100, interest_rate

    def analyze_gdp_growth(self, series_code='GDPC1'):
        data = self.fred.get_series_df(series_code)
        data['value'] = pd.to_numeric(data['value'])
        gdp_growth = (data['value'].iloc[-1] - data['value'].iloc[-5]) / data['value'].iloc[-5] * 100
        risk = min(max(abs(gdp_growth - 2.5) / 2.5, 0), 1)
        return risk * 100, gdp_growth

    def get_openai_analysis(self, metrics_analysis, detailed_analysis):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": metrics_analysis + detailed_analysis},
                {"role": "user",
                 "content": "Provide an in-depth analysis of the current US economic situation based on the following data:"}
            ]
        )
        return response['choices'][0]['message']['content']

    def generate_analysis(self):
        analysis = "========== Current Economic Situation Analysis ==========\n"
        metrics_analysis = ""
        detailed_analysis = "\nEconomic Metrics:\n"

        unemployment_risk, unemployment_rate = self.analyze_unemployment_rate()
        metrics_analysis += f"• Unemployment Rate: {unemployment_rate:.2f} (Risk: {unemployment_risk:.2f}%)\n"
        detailed_analysis += f"  - Situation is stable and within expected parameters.\n"

        inflation_risk, inflation_rate = self.analyze_inflation()
        metrics_analysis += f"• Inflation Rate: {inflation_rate:.2f} (Risk: {inflation_risk:.2f}%)\n"
        detailed_analysis += f"  - Low risk, indicating stable prices and economic conditions.\n"

        interest_rate_risk, interest_rate = self.analyze_interest_rate()
        metrics_analysis += f"• Interest Rate: {interest_rate:.2f} (Risk: {interest_rate_risk:.2f}%)\n"
        detailed_analysis += f"  - High risk, that could impact borrowing costs and investment returns.\n"

        gdp_growth_risk, gdp_growth = self.analyze_gdp_growth()
        metrics_analysis += f"• GDP Growth Rate: {gdp_growth:.2f} (Risk: {gdp_growth_risk:.2f}%)\n"
        detailed_analysis += f"  - Situation is stable and within expected parameters.\n"

        total_risk = (unemployment_risk + inflation_risk + interest_rate_risk + gdp_growth_risk) / 4

        openai_analysis = self.get_openai_analysis(metrics_analysis, detailed_analysis)
        analysis += metrics_analysis + "\n========== Economic Metrics ==========\n" + detailed_analysis
        analysis += f"\n========== Total Economic Risk: {total_risk:.2f}% ==========\n\n" + openai_analysis
        #analysis += f"\n========== Total Economic Risk: {total_risk:.2f}% ==========\n\n"

        class TextStyle:
            DARK_BLUE = '\033[34m'
            BOLD = '\033[1m'
            END = '\033[0m'

        max_line_length = 80
        equal_sign_length = max_line_length - 2
        d = f"{TextStyle.DARK_BLUE}{'=' * 24}  Total Economic Risk: {total_risk:.2f}%  {'=' * 23}{TextStyle.END}\n"
        print(d)
        print(analysis)
        print(f"{TextStyle.DARK_BLUE}Total Macro Risk: {total_risk:.2f}%{TextStyle.END}".center(max_line_length))
        equal_sign_line = f"{TextStyle.DARK_BLUE}{'=' * equal_sign_length}{TextStyle.END}"
        d += equal_sign_line.center(max_line_length)

        return ""


class TextStyle:
    DARK_BLUE = '\033[34m'
    BOLD = '\033[1m'
    END = '\033[0m'


class Trade:
    def __init__(self, pair, confidence, entry_price, exit_price=None):
        self.pair = pair
        self.confidence = confidence
        self.entry_price = entry_price
        self.exit_price = exit_price
        self.timestamp = datetime.datetime.now()

    def close(self, exit_price):
        self.exit_price = exit_price

    def profit_loss(self):
        if self.exit_price is not None:
            return self.exit_price - self.entry_price
        return None

    def close(self, closing_price):
        self.exit_price = closing_price
        self.pnl = self.exit_price - self.entry_price

    def __str__(self):
        return f"Pair: {self.pair}, Confidence: {self.confidence}, Entry: {self.entry_price}, Exit: {self.exit_price}, P/L: {self.profit_loss()}, Time: {self.timestamp}"


class TradingJournal:
    def __init__(self):
        self.trades = []

    def add_trade(self, trade):
        self.trades.append(trade)

    def list_trades(self):
        for trade in self.trades:
            print(trade)

    def close_trade(self):
        print("Select a trade to close:")
        for i, trade in enumerate(self.trades):
            if trade.exit_price is None:
                print(f"{i}. {trade}")
        index = int(input("Enter the index of the trade to close: "))
        closing_price = float(input("Enter the closing price: "))
        self.trades[index].close(closing_price)


def prompt_for_trade():
    pair = input("Enter the trading pair: ")
    confidence_map = {'H': 'High', 'M': 'Mid', 'L': 'Low'}
    confidence_input = input("Enter the confidence level (H: High, M: Mid, L: Low): ").upper()
    confidence = confidence_map.get(confidence_input, 'Unknown')
    entry_price = float(input("Enter the entry price: "))
    print("\n")
    return Trade(pair, confidence, entry_price)


def get_forex_session(current_time_utc):
    current_time_utc = current_time_utc.hour
    sessions = []

    if 22 <= current_time_utc < 7 or current_time_utc == 7:
        sessions.append(("Sydney Session", ["AUD/USD", "AUD/JPY"]))

    if 0 <= current_time_utc < 9:
        sessions.append(("Tokyo Session", ["USD/JPY", "EUR/JPY"]))

    if 7 <= current_time_utc < 17:
        sessions.append(("London Session", ["GBP/USD", "EUR/GBP"]))

    if 13 <= current_time_utc < 22:
        sessions.append(("New York Session", ["USD/CAD", "EUR/USD"]))

    return sessions


def print_formatted(text):
    max_line_length = 80
    print(f"{TextStyle.DARK_BLUE}{text.center(max_line_length)}{TextStyle.END}")


def main_menu():
    print("\nChoose an option:")
    print("1. Economic Analysis")
    print("2. Trade Journal")
    print("3. Exit")
    choice = input("Enter your choice: ")
    return choice


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def startup(analyzer):
    clear_screen()
    current_datetime = datetime.datetime.now(pytz.utc)
    formatted_date = current_datetime.strftime("%d/%m/%Y")
    formatted_time = current_datetime.strftime("%H:%M:%S")

    forex_sessions = get_forex_session(current_datetime)

    panel_title = f"Welcome To The {TextStyle.END}{TextStyle.BOLD}WillBear Trading Panel"
    datetime_line = f"Current Date & Time: {formatted_date} - {formatted_time}"

    equal_sign_length = 80 - 2
    equal_sign_line = f"{TextStyle.DARK_BLUE}{'=' * equal_sign_length}{TextStyle.END}"

    print(equal_sign_line)
    print_formatted(panel_title)
    print_formatted(datetime_line)
    print(equal_sign_line)

    session_names = [session for session, _ in forex_sessions]
    all_pairs = [pair for _, pairs in forex_sessions for pair in pairs]

    session_line = f" Forex Trading Session: {TextStyle.END}{', '.join(session_names)}"
    pairs_line = f"Pairs: {TextStyle.END}{', '.join(all_pairs)}"

    print(f"{TextStyle.DARK_BLUE}{session_line.center(equal_sign_length)}{TextStyle.END}")
    print(f"{TextStyle.DARK_BLUE}{pairs_line.center(equal_sign_length)}{TextStyle.END}")
    print(equal_sign_line)
    return all_pairs


def my_num_sort(my_str):
    return list(map(int, re.findall(r'\d+', my_str)))[0]


def remove_slashes(pair):
    return pair.replace('/', '')


def get_outlooks(pairs, intervals, screener, exchange):
    outlooks = []
    for pair in pairs:
        modified_pair = remove_slashes(pair)
        outlook_for_pair = [f"{interval}: 100%".rjust(
            max(len(interval) for interval in intervals) + 7) for interval in intervals]
        outlooks.append((pair, outlook_for_pair))
    return outlooks


def print_outlooks(outlooks):
    blue_color = "\033[94m"
    reset_format = "\033[0m"
    equal_sign_length = 80

    for pair, outlook_for_pair in outlooks:
        outlooks_str = " | ".join(outlook_for_pair)
        formatted_output = f"{blue_color}{pair} {reset_format} \033[1m{outlooks_str}{reset_format}"
        centered_output = formatted_output.center(equal_sign_length)
        print(centered_output.center(equal_sign_length))


def main():
    apikey = '*********'
    openai.api_key = apikey
    analyzer = EconomicRiskAnalyzer('fred_api_key.txt')
    pairs = startup(analyzer)
    screener = "FOREX"
    exchange = "FX_IDC"
    intervals = ["1m", "5m", "15m", "1h", "1d"]

    outlooks = get_outlooks(pairs, intervals, screener, exchange)
    print_outlooks(outlooks)
    print(
        f"{TextStyle.DARK_BLUE}=============================================================================={TextStyle.END}")

    journal = TradingJournal()
    while True:
        choice = main_menu()
        if choice == "1":
            print("\n")
            analyzer.generate_analysis()
            print("\n")
        elif choice == "2":
            journal = TradingJournal()
            while True:
                current_datetime = datetime.datetime.now()
                startup(analyzer)

                print("1. Add Trade")
                print("2. List Trades")
                print("3. Close Trade")
                print("4. Return to Main Menu")
                sub_choice = input("Choose an option: ")
                print("\n")
                if sub_choice == "1":
                    trade = prompt_for_trade()
                    journal.add_trade(trade)
                elif sub_choice == "2":
                    journal.list_trades()
                elif sub_choice == "3":
                    journal.close_trade()
                elif sub_choice == "4":
                    break
        elif choice == "3":
            break


if __name__ == "__main__":
    main()
