import  streamlit as st
import  pandas as pd
import  altair as alt
from    urllib.error import URLError
import  functools
from    pathlib import Path
from    st_aggrid import AgGrid
from    st_aggrid.shared import JsCode
from    st_aggrid.grid_options_builder import GridOptionsBuilder
import  plotly.express as px


#-------------------------------------------------------
# Set up main app 
#-------------------------------------------------------
st.set_page_config(
        page_title="Portfolio Stocks Details View", 
        page_icon="📊", 
        initial_sidebar_state="expanded",
        layout="wide",
)

chart = functools.partial(st.plotly_chart, use_container_width=True)
COMMON_ARGS = {
    "color": "symbol",
    "color_discrete_sequence": px.colors.sequential.Greens,
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
st.sidebar.subheader("Filter Accounts")

accounts = list(final_data.account_name.unique())
account_selections = st.sidebar.multiselect(
    "Select Accounts to View", options=accounts, default=accounts
)

st.sidebar.subheader("Filter Tickers")

symbols = list(final_data.loc[final_data.account_name.isin(account_selections), "symbol"].unique())
symbol_selections = st.sidebar.multiselect(
    "Select Ticker Symbols to View", options=symbols, default=symbols
)


def draw_bar(y_val: str) -> None:
    fig = px.bar(final_data, y=y_val, x="symbol", **COMMON_ARGS)
    fig.update_layout(barmode="stack", xaxis={"categoryorder": "total descending"})
    chart(fig)


#-------------------------------------------------------
# Charts -- Total Value gained each Symbol             
#           Total Percent Value gained each Symbol     
#-------------------------------------------------------  
colTable1, colTable2 = st.columns(2)
with colTable1:
        st.write("Total Value gained each Symbol")
        draw_bar("total_gain_loss_dollar")
with colTable2: 
        st.write("Total Percent Value gained each Symbol")
        draw_bar("total_gain_loss_percent")

progress_bar = st.progress(0)


#-------------------------------------------------------
# GRID Dataframe selected data                        
#-------------------------------------------------------
final_data = filter_data(final_data, account_selections, symbol_selections)
st.subheader("Selected Account and Ticker Data")
cellsytle_jscode = JsCode(
    """
function(params) {
    if (params.value > 0) {
        return {
            'color': 'white',
            'backgroundColor': 'forestgreen'
        }
    } else if (params.value < 0) {
        return {
            'color': 'white',
            'backgroundColor': 'crimson'
        }
    } else {
        return {
            'color': 'white',
            'backgroundColor': 'slategray'
        }
    }
};
"""
)

gb = GridOptionsBuilder.from_dataframe(final_data)
gb.configure_columns(
    (
        "last_price_change",
        "total_gain_loss_dollar",
        "total_gain_loss_percent",
        "today's_gain_loss_dollar",
        "today's_gain_loss_percent",
    ),
    cellStyle=cellsytle_jscode,
)
gb.configure_pagination()
gb.configure_columns(("account_name", "symbol"), pinned=True)
gridOptions = gb.build()

AgGrid(final_data, gridOptions=gridOptions, allow_unsafe_jscode=True)

### -- DATAFRAME  TABLES --
# with st.expander("Raw Dataframe"):
#     st.write(raw_data)

# with st.expander("Cleaned Data"):
#     st.write(final_data)