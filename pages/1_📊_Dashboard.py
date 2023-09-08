import  streamlit as st
import  pandas as pd
import  altair as alt
from    urllib.error import URLError
import  functools
from    pathlib import Path
import  plotly.express as px

#-------------------------------------------------------
# Set up main app 
#-------------------------------------------------------
st.set_page_config(
        page_title="Portfolio Dashboard View", 
        page_icon="📊", 
        initial_sidebar_state="expanded",
        layout="wide",
)

padding_top = 0
st.markdown(f"""
    <style>
        .block-container{{
            padding-top: {padding_top}rem;
        }}
    </style>""",
    unsafe_allow_html=True,
)

hide_streamlit_style = """
            <style>
            [data-testid="stToolbar"] {visibility: hidden !important;}
            footer {visibility: hidden !important;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
st.header("Portfolio Dashboard")

chart = functools.partial(st.plotly_chart, use_container_width=True)
COMMON_ARGS = {
    "color": "symbol",
      "color_discrete_sequence": px.colors.sequential.Blues,
    "hover_data": [
        "account_name",
        "percent_of_account",
        "quantity",
        "total_gain_loss_dollar",
        "total_gain_loss_percent",
    ],
}

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


@st.cache_data
def filter_data(
    df: pd.DataFrame, account_selections: list[str], symbol_selections: list[str]
) -> pd.DataFrame:
    """
    Returns Dataframe with only accounts and symbols selected

    Args:
        df (pd.DataFrame): clean fidelity csv data, including account_name and symbol columns
        account_selections (list[str]): list of account names to include
        symbol_selections (list[str]): list of symbols to include

    Returns:
        pd.DataFrame: data only for the given accounts and symbols
    """
    df = df.copy()
    df = df[
        df.account_name.isin(account_selections) & df.symbol.isin(symbol_selections)
    ]

    return df


#-------------------------------------------------------
# Stock data 
#-------------------------------------------------------
uploaded_data = open("example.csv", "r")
raw_data = pd.read_csv(uploaded_data)
final_data = clean_data(raw_data)


#-------------------------------------------------------
# Set up sidebar 
#-------------------------------------------------------
accounts = list(final_data.account_name.unique())
account_selections = st.sidebar.multiselect(
    "Select Accounts to View", options=accounts, default=accounts
)

symbols = list(final_data.loc[final_data.account_name.isin(account_selections), "symbol"].unique())
symbol_selections = st.sidebar.multiselect(
    "Select Ticker Symbols to View", options=symbols, default=symbols
)


#-------------------------------------------------------
# Metrics                                             
#-------------------------------------------------------
def draw_bar(y_val: str) -> None:
    fig = px.bar(final_data, y=y_val, x="symbol", **COMMON_ARGS)
    fig.update_layout(barmode="stack", xaxis={"categoryorder": "total descending"})
    chart(fig)

account_plural = "s" if len(account_selections) > 1 else ""
### st.subheader(f"Value of Account{account_plural}")
totals = final_data.groupby("account_name", as_index=False).sum()


#-------------------------------------------------------
# Metrics - Total of All Accounts/Total per Account   
#-------------------------------------------------------
colMetric1, colMetric2 = st.columns(2)
with colMetric1:
    if len(account_selections) > 1:
        st.metric(
            "Total of All Accounts",
            f"${totals.current_value.sum():.2f}",
            f"{totals.total_gain_loss_dollar.sum():.2f}",
    ) 
with colMetric2:
    for column, row in zip(st.columns(len(totals)), totals.itertuples()):
        column.metric(
            row.account_name,
            f"${row.current_value:.2f}",
            f"{row.total_gain_loss_dollar:.2f}",
        )
progress_bar = st.progress(0)


#-------------------------------------------------------
# Charts -- Total per Account/Value of each Symbol    
#-------------------------------------------------------
colChart1, colChart2 = st.columns(2, gap = "large")
with colChart1:
    st.write("Total per Account")
    fig = px.bar(
        totals,
        y="account_name",
        x="current_value",
        color="account_name",
        color_discrete_sequence=px.colors.sequential.Blues,
    )
    fig.update_layout(barmode="stack", xaxis={"categoryorder": "total descending"})
    chart(fig)

with colChart2:
    st.write("Value of each Symbol")
    draw_bar("current_value")
progress_bar = st.progress(0)


#-------------------------------------------------------
# Charts -- Value of each Symbol/per Account          
#-------------------------------------------------------
colChart3, colChart4 = st.columns(2, gap = "large")
with colChart3:
    st.write("Value of each Symbol per Account")
    fig = px.sunburst(
        final_data, path=["account_name", "symbol"], values="current_value", **COMMON_ARGS
    )
    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
    chart(fig)

with colChart4:  
    st.write("Value of each Symbol")
    fig = px.pie(final_data, values="current_value", names="symbol", **COMMON_ARGS)
    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
    chart(fig)
