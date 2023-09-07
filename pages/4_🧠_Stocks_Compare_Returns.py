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
hide_streamlit_style = """
            <style>
            [data-testid="stToolbar"] {visibility: hidden !important;}
            footer {visibility: hidden !important;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
st.header("Closing price and daily returns comparator")

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

@st.cache_data
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Take Raw Fidelity Dataframe and return usable dataframe.
    - snake_case headers
    - Include 401k by filling na type
    - Drop Cash accounts and misc text
    - Clean $ and % signs from values and convert to floats

    Args:
        df (pd.DataFrame): Raw fidelity csv data

    Returns:
        pd.DataFrame: cleaned dataframe with features above
    """
    df = df.copy()
    df.columns = df.columns.str.lower().str.replace(" ", "_", regex=False).str.replace("/", "_", regex=False)

    df.type = df.type.fillna("unknown")
    df = df.dropna()

    price_index = df.columns.get_loc("last_price")
    cost_basis_index = df.columns.get_loc("cost_basis_per_share")
    df[df.columns[price_index : cost_basis_index + 1]] = df[
        df.columns[price_index : cost_basis_index + 1]
    ].transform(lambda s: s.str.replace("$", "", regex=False).str.replace("%", "", regex=False).astype(float))

    quantity_index = df.columns.get_loc("quantity")
    most_relevant_columns = df.columns[quantity_index : cost_basis_index + 1]
    first_columns = df.columns[0:quantity_index]
    last_columns = df.columns[cost_basis_index + 1 :]
    df = df[[*most_relevant_columns, *first_columns, *last_columns]]
    return df


#-------------------------------------------------------
# Stock data 
#-------------------------------------------------------
uploaded_data = open("example.csv", "r")
raw_data = pd.read_csv(uploaded_data)
final_data = clean_data(raw_data)

#-------------------------------------------------------
# Set up sidebar #
#-------------------------------------------------------
accounts = list(final_data.account_name.unique())
account_selections = st.sidebar.multiselect(
    "Select Accounts to View", options=accounts, default=accounts
)

symbols = list(final_data.loc[final_data.account_name.isin(account_selections), "symbol"].unique())
symbol_list = st.sidebar.multiselect(
    "Select Ticker Symbols to View", options=symbols, default=symbols
)

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

            st.write('Closing price by stock symbol')
            st.line_chart(df_data)
            with st.expander("What is closing price?"):
                st.write(
                    """The closing price is the raw price or cash value of the last transacted price in a security before the market officially closes for normal trading. It is often the reference point used by investors to compare a stock's performance since the previous day""")

            daily_returns = compute_daily_returns(df_data)
            st.write('Daily returns by stock symbol')
            st.line_chart(daily_returns)
            with st.expander("What is daily return?"):
                st.write(
                    """Daily return is calculated by subtracting the opening price from the closing price. If you are calculating for a per-share gain, you simply multiply the result by your share amount. If you are calculating for percentages, you divide by the opening price, then multiply by 100.""")
        else:
            st.error("Please fill all fields!")

