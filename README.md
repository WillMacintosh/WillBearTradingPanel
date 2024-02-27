# WillBear Trading Panel

## Introduction
WillBear Trading Panel is a comprehensive trading analysis and management tool designed to provide traders and financial analysts with real-time economic data, risk analysis, and trade management capabilities. Leveraging advanced algorithms and data from the Federal Reserve Economic Data (FRED), the panel offers insights into unemployment rates, inflation, interest rates, and GDP growth, alongside a sophisticated trade journal for trade tracking.

![Screenshot of output](https://i.imgur.com/RkCbeLa.png)
![Screenshot of output](https://i.imgur.com/jkRVLie.png)

## Features
- **Economic Analysis**: Utilises real-time data from FRED to analyze key economic indicators and assess market risks.
- **Trade Journal**: Manages and tracks trades with detailed entries, including pair, confidence level, entry and exit prices.
- **Risk Assessment**: Calculates and displays the risk associated with current economic conditions and individual trades.
- **Forex Session Timings**: Identifies the active Forex market sessions and suggested currency pairs to trade.
- **Custom Analysis**: Generates detailed economic situation analyses with integrated GPT-3.5 insights.

## Installation

### Prerequisites
- Python 3.8 or higher
- Pandas
- NumPy
- Requests (for FRED API)
- pytz

### Setup
Clone the repository to your local machine:
```bash
 pip install Fred pandas openai==0.28 pytz
```

### Usage
To start the WillBear Trading Panel, run the following command in the terminal:
```bash
 python main.py
```
