import streamlit as st
import traceback
import json
from streamlit_lightweight_charts import renderLightweightCharts
import streamlit_lightweight_charts.dataSamples as data
import pickle
import pandas as pd
import numpy as np
import os


@st.cache_data
def load_dataset(ticket):
    folder_path = 'C:/Users/irvin/OneDrive/Desktop/python_scripts/codigo_proyecto_aplicacion/modelos'
    df = pd.read_csv(f'{folder_path}/{ticket}/data_input.csv', parse_dates=True)
    df = df.rename(columns={
        "Date": 'price_date',
        "Open": 'PX_OPEN',
        "Low": 'PX_LOW',
        "High": 'PX_HIGH',
        "Close": 'PX_LAST',
        "Volume": 'PX_TURNOVER'
    })
    return df


def get_current_date(ticket='WALMEX.MX'):
    arguments = {"interval": 1, 'from': pd.Timestamp.today().strftime("%Y-%m-%d") + " 09:59:00"}
    
    folder_path = 'C:/Users/irvin/OneDrive/Desktop/python_scripts/codigo_proyecto_aplicacion/modelos'
    df = pd.read_csv(f'{folder_path}/{ticket}/data_input.csv', parse_dates=['Date'])
    
    # Obtener la última fecha disponible en el archivo
    last_date = df['Date'].max()
    return pd.Timestamp(last_date).replace(hour=0, minute=0, second=0)


def get_current_candle(ticket):
    traded_date = get_current_date(ticket)
    print(traded_date)
    
    if traded_date is None:
        return None, None
    
    # Cargar los datos locales
    folder_path = 'C:/Users/irvin/OneDrive/Desktop/python_scripts/codigo_proyecto_aplicacion/modelos'
    df = pd.read_csv(f'{folder_path}/{ticket}/data_input.csv', parse_dates=['Date'])
    
    # Filtrar el DataFrame por la fecha de negociación
    ticker_prices_df = df[df['Date'] == traded_date].copy()
    
    if ticker_prices_df.empty:
        return None, None
    
    # Renombrar las columnas para que coincidan con el formato esperado
    ticker_prices_df = ticker_prices_df.rename(columns={
        "Date": 'price_date',
        "Open": 'PX_OPEN',
        "Low": 'PX_LOW',
        "High": 'PX_HIGH',
        "Close": 'PX_LAST',
        "Volume": 'PX_TURNOVER'
    })
    
    ticker_prices_df.set_index('price_date', inplace=True)
    ticker_prices_df.index = pd.to_datetime(ticker_prices_df.index)
    
    return ticker_prices_df[['PX_OPEN','PX_LOW','PX_HIGH','PX_LAST','PX_TURNOVER']], traded_date


def render_candlestick_chart(data):
    data = data.rename(
        columns={"PX_LAST": 'close', 'PX_LOW': 'low', 'PX_HIGH': 'high', 'PX_OPEN': 'open', "PX_TURNOVER": "value"}
    )

    data['time'] = data['price_date'].astype(str)
    COLOR_BULL = 'rgba(38,166,154,0.9)'  # Color para velas alcistas
    COLOR_BEAR = 'rgba(239,83,80,0.9)'  # Color para velas bajistas

    data['chg'] = (data['close'] - data['open']) / data['open']
    data['color'] = data['chg'].apply(lambda x: 'red' if x <= 0 else 'green')

    candles = json.loads(data.to_json(orient="records"))
    volume = json.loads(data.to_json(orient="records"))

    # Configuración del gráfico de velas
    chartMultipaneOptions = [
        {
            "height": 550,
            "handleScroll": False,
            "handleScale": False,
            "layout": {
                "background": {"type": "solid", "color": 'transparent'},
                "textColor": "white"
            },
            "grid": {
                "vertLines": {"color": "rgba(33, 47, 60, 0.5)"},
                "horzLines": {"color": "rgba(33, 47, 60, 0.5)"}
            },
            "crosshair": {"mode": 0},
            "priceScale": {"borderColor": "rgba(197, 203, 206, 0.8)"},
            "timeScale": {"borderColor": "rgba(197, 203, 206, 0.8)", "barSpacing": 5},
        },
        {
            "height": 100,
            "handleScroll": False,
            "handleScale": False,
            "layout": {
                "background": {"type": 'solid', "color": 'transparent'},
                "textColor": 'white',
            },
            "grid": {
                "vertLines": {"color": "rgba(33, 47, 60, 0.5)"},
                "horzLines": {"color": "rgba(33, 47, 60, 0.5)"}
            },
            "timeScale": {"borderColor": "rgba(197, 203, 206, 0.8)", "barSpacing": 5},
            "priceScale": {"borderColor": "rgba(197, 203, 206, 0.8)"},
        },
    ]

    seriesCandlestickChart = [
        {
            "type": 'Candlestick',
            "data": candles,
            "options": {
                "upColor": COLOR_BULL,
                "downColor": COLOR_BEAR,
                "borderVisible": False,
                "wickUpColor": COLOR_BULL,
                "wickDownColor": COLOR_BEAR
            }
        }
    ]

    seriesVolumeChart = [
        {
            "type": 'Histogram',
            "data": volume,
            "options": {
                "priceFormat": {"type": 'volume'},
            }
        }
    ]

    renderLightweightCharts([
        {
            "chart": chartMultipaneOptions[0],
            "series": seriesCandlestickChart
        },
        {
            "chart": chartMultipaneOptions[1],
            "series": seriesVolumeChart
        },
    ], 'multipane')



st.set_page_config(
    page_title="Superchart",
    page_icon="📈",
    layout='wide'
)
st.sidebar.subheader("""📈 Superchart""")

selected_stock = st.sidebar.selectbox("Select asset:", ['WALMEX.MX'])
st.subheader(f"""{selected_stock} dividend adjusted""")

df = load_dataset(selected_stock)
stock_data = df[['price_date','PX_OPEN', 'PX_LAST', 'PX_LOW', 'PX_HIGH', 'PX_TURNOVER']]  

try:
    rt_candle, time_updated = get_current_candle(selected_stock)
    if rt_candle is None:
        st.markdown(f"Última actualización de precio: **{rt_candle.index[0].strftime("%d %m %Y")}**")
    elif len(rt_candle.dropna()) == 1:
            st.markdown(f"Última actualización de precio: **{rt_candle.index[0].strftime("%d %m %Y")}** ")
except Exception:
    st.markdown(f"Última actualización de precio: **{rt_candle.index[0].strftime("%d %m %Y")}**")

#st.markdown(f"Promedio de volumen en los últimos 90 días: **{int(ticker_turnovers.loc[selected_stock] / 1e6)} M RUB**")
selected_timeframe = st.selectbox("Seleccionar periodo:", ['Diario', 'Semanal', 'Mensual'])

if selected_timeframe == 'Diario':
    render_candlestick_chart(stock_data.dropna().iloc[-80:])
# elif selected_timeframe == 'Semanal':
#     render_candlestick_chart(resample_candlestick(stock_data[['PX_OPEN', 'PX_LAST', 'PX_LOW', 'PX_HIGH', 'PX_TURNOVER']].dropna().iloc[-252 * 5:], 'W-FRI'))
# elif selected_timeframe == 'Mensual':
#     render_candlestick_chart(resample_candlestick(stock_data[['PX_OPEN', 'PX_LAST', 'PX_LOW', 'PX_HIGH', 'PX_TURNOVER']].dropna().iloc[-252 * 15:], 'M'))

