import streamlit as st
import numpy as np
import pandas as pd
import requests
import matplotlib.pyplot as plt
import os
import datetime
from prophet import Prophet
import requests
import pandas as pd

#-------------------------------------------------------
# Set up main app #
#-------------------------------------------------------
st.set_page_config(
        page_title="Portfolio Stock Compare View", 
        page_icon="📊", 
        initial_sidebar_state="expanded",
        layout="wide",
)


def get_stock_data_by_symbol(symbol: str):
    url = "https://alpha.financeapi.net/symbol/get-chart?period=MAX&symbol=" + symbol
    token =  API_KEY = st.secrets["api"]["YAHOO_TOKEN"] 
    payload = {}
    headers = {
        'X-API-KEY': token
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    response_json = response.json()
    if 'attributes' in response_json:
        return pd.DataFrame(response_json['attributes']).T
    else:
        return pd.DataFrame()


def fill_missing_values(dataframe):
    return dataframe.ffill().bfill()


def get_data(symbols, dates):
    df_final = pd.DataFrame(index=dates)
    for symbol in symbols:
        df_temp = get_stock_data_by_symbol(symbol)
        if not df_temp.empty:
            df_temp = df_temp[['close']]
            df_temp.index = pd.to_datetime(df_temp.index)
            df_temp = df_temp.rename(columns={"close": symbol})
            df_final = df_final.join(df_temp)

    return df_final


def get_data_for_training(symbol, start_date, end_date):
    """Read stock data (adjusted close) for given symbols from CSV files."""
    df_final = pd.DataFrame(index=pd.date_range(start_date, end_date))
    #  file_path = symbol_to_path(symbol)
    df_temp = get_stock_data_by_symbol(symbol)
    if df_temp.empty:
        raise 'Symbol invalid or with empty stock data!'
    df_temp = df_temp[['close']]
    df_temp.index = pd.to_datetime(df_temp.index)
    df_final = df_final.join(df_temp)
    df_final = df_final.ffill().bfill()
    return df_final


def compute_daily_returns(df):
    """Compute and return the daily return values."""
    # TODO: Your code here
    # Note: Returned DataFrame must have the same number of rows
    return df[:-1] / df[1:].values - 1


def get_data_for_training(symbol, start_date, end_date):
    """Read stock data (adjusted close) for given symbols from CSV files."""
    df_final = pd.DataFrame(index=pd.date_range(start_date, end_date))
    df_temp = get_stock_data_by_symbol(symbol)
    if not df_temp.empty:
        df_temp = df_temp[['close']]
        df_temp.index = pd.to_datetime(df_temp.index)
        df_final = df_final.join(df_temp)
        df_final = df_final.ffill().bfill()
        return df_final
    return False

st.header("Closing price and daily returns comparator")

#-------------------------------------------------------
# Set up sidebar #
#-------------------------------------------------------
today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)
yesterday = today - datetime.timedelta(days=1)
start_default = yesterday - datetime.timedelta(days=30)
start_date = st.sidebar.date_input('Start date', datetime.date(1993, 1, 1), min_value=datetime.date(1993, 1, 1))
end_date = st.sidebar.date_input('End date', yesterday)
if not start_date < end_date:
    st.sidebar.error('Error: End date must fall after start date.')

if end_date > yesterday:
    st.sidebar.error('Error: End date must be equal or older than yesterday.')

# Get symbols from user
symbol_list = st.sidebar.text_input("Enter Symbols Separated by comma (,)", value='GOOG,TSLA,MSFT',
                            key='symbols').upper().split(',')

st.info('The chart will not display invalid symbols or symbols that are not listed in the USA market.', icon="⚠️")

if st.sidebar.button('Run'):
    valid_input = True
    if not start_date < end_date:
        st.sidebar.error('Error: End date must fall after start date.')
        valid_input = False

    if end_date > yesterday:
        st.sidebar.error('Error: End date must be equal or older than yesterday.')
        valid_input = False

    if symbol_list[0] == '':
        st.sidebar.error('Error: You must have at least one stock symbol.')
        valid_input = False

    with st.spinner("Processing..."):
        # check if all fields are filled
        if valid_input:
            dates = pd.date_range(start_date, end_date)  # date range as index
            df_data = get_data(symbol_list, dates)  # get data for each symbol

            # Fill missing values
            df_data = fill_missing_values(df_data)

            st.header('Closing price by stock symbol')
            st.line_chart(df_data)
            with st.expander("What is closing price?"):
                st.write(
                    """The closing price is the raw price or cash value of the last transacted price in a security before the market officially closes for normal trading. It is often the reference point used by investors to compare a stock's performance since the previous day""")

            daily_returns = compute_daily_returns(df_data)
            st.header('Daily returns by stock symbol')
            st.line_chart(daily_returns)
            with st.expander("What is daily return?"):
                st.write(
                    """Daily return is calculated by subtracting the opening price from the closing price. If you are calculating for a per-share gain, you simply multiply the result by your share amount. If you are calculating for percentages, you divide by the opening price, then multiply by 100.""")
        else:
            st.error("Please fill all fields!")

