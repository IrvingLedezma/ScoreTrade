import streamlit as st
import traceback
import json
from streamlit_lightweight_charts import renderLightweightCharts
import streamlit_lightweight_charts.dataSamples as data
import pickle
import pandas as pd
import numpy as np
import os
import apimoex
from requests.auth import HTTPBasicAuth
import requests
from dotenv import load_dotenv
from moexalgo.session import authorize
from moexalgo import Ticker, Market

load_dotenv()
# authorize(os.getenv("MOEX_LOGIN"), os.getenv("MOEX_PASSWORD"))
# url = 'https://passport.moex.com/authenticate'
# username = os.getenv("MOEX_LOGIN")
# password = os.getenv("MOEX_PASSWORD")
# response = requests.get(url, auth=HTTPBasicAuth(username, password))
# cert = response.cookies['MicexPassportCert']

EXCHANGE_MAP = {"MOEX": {"market": "shares", "engine": "stock", "board": "tqbr"},
                "MOEX CETS": {"market": "selt", "engine": "currency", "board": "cets"},
                "MOEX SPBFUT": {"market": "forts", "engine": "futures", "board": "spbfut"}}


class APIMOEXError(Exception):
    pass


with open(os.path.join(os.getenv("PATH_TO_DATA_FOLDER"), 'cert.p'), 'rb') as f:
    cert = pickle.load(f)


def get_current_date(t='SBER', exchange='MOEX'):
    arguments = {"interval": 1, 'from': pd.Timestamp.today().strftime(
        "%Y-%m-%d") + " 09:59:00"}  # (pd.Timestamp.today()-pd.Timedelta(days=5)).strftime("%Y-%m-%d") + " 09:59:00"}
    response = requests.get(f"https://iss.moex.com/iss/engines/{EXCHANGE_MAP[exchange]['engine']}/"
                            f"markets/{EXCHANGE_MAP[exchange]['market']}/boards/{EXCHANGE_MAP[exchange]['board']}/securities/{t}/candles.json",
                            cookies={'MicexPassportCert': cert},
                            params=arguments)
    data = response.json()
    if len(data['candles']['data']) == 0:
        return None
    else:
        return pd.Timestamp(data['candles']['data'][-1][-1]).replace(hour=0, minute=0, second=0)


def get_current_candle(exchange, ticker, div_table):
    traded_date = get_current_date()
    print(traded_date)
    if traded_date is None:
        return None, None
    ticker_divs_on_date = div_table[(div_table['ex_date'] == traded_date) & (div_table['ticker'] == ticker)]

    arguments = {'marketdata.columns': ('SECID,'
                                        'TIME,'
                                        'OPEN,'
                                        'LOW,'
                                        'HIGH,'
                                        'LAST,'
                                        'VOLTODAY,'
                                        'VALTODAY_RUR')}
    response = requests.get(f"https://iss.moex.com/iss/engines/{EXCHANGE_MAP[exchange]['engine']}/"
                            f"markets/{EXCHANGE_MAP[exchange]['market']}/boards/{EXCHANGE_MAP[exchange]['board']}/securities/{ticker}.json",
                            cookies={'MicexPassportCert': cert},
                            params=arguments)
    data = response.json()
    if len(data['marketdata']['data']) == 1:
        data = dict(zip(data['marketdata']['columns'], data['marketdata']['data'][0]))
    else:
        raise APIMOEXError(f"Error when loading realtime price for {ticker}")
    ticker_prices_df = pd.DataFrame(
        [{'price_date': traded_date, 'PX_OPEN': data['OPEN'], 'PX_HIGH': data['HIGH'], 'PX_LOW': data['LOW'],
          'PX_LAST': data['LAST'], 'PX_VOLUME': data['VOLTODAY'], 'PX_TURNOVER': data['VALTODAY_RUR']}]).set_index('price_date')
    ticker_prices_df.index = pd.to_datetime(ticker_prices_df.index)
    if len(ticker_divs_on_date) > 0:
        ticker_prices_df[['PX_OPEN', 'PX_HIGH', 'PX_LOW', 'PX_LAST']] += float(
            ticker_divs_on_date['dividend_amount'].sum())
        st.markdown(
            f"Today dividend: **{float(ticker_divs_on_date['dividend_amount'].sum())} RUB**")
    return ticker_prices_df, data['TIME']


def render_diff_chart(ser, key):
    data = ser.rename("value")
    data.index.name = 'time'
    data = data.reset_index()
    data['time'] = data['time'].astype(str)
    data = data.to_dict('records')
    chartOptions = {
        "handleScroll": False,
        "handleScale": False,
        "layout": {
            "textColor": 'black',
            "background": {
                "type": 'solid',
                "color": 'white'
            }
        },
        "rightPriceScale": {
            "mode": 0,
        },
    }
    seriesBaselineChart = [{
        "type": 'Baseline',
        "data": data,
        "options": {
            "baseValue": {"type": "price", "price": 0},
            "topLineColor": 'rgba( 38, 166, 154, 1)',
            "topFillColor1": 'rgba( 38, 166, 154, 0.28)',
            "topFillColor2": 'rgba( 38, 166, 154, 0.05)',
            "bottomLineColor": 'rgba( 239, 83, 80, 1)',
            "bottomFillColor1": 'rgba( 239, 83, 80, 0.05)',
            "bottomFillColor2": 'rgba( 239, 83, 80, 0.28)'
        }
    }]
    renderLightweightCharts([
        {
            "chart": chartOptions,
            "series": seriesBaselineChart,
        }
    ], key)


def render_candlestick_chart(data):
    data = data.rename(
        columns={"PX_LAST": 'close', 'PX_LOW': 'low', 'PX_HIGH': 'high', 'PX_OPEN': 'open', "PX_TURNOVER": "value"})

    data.index.name = 'time'
    data = data.reset_index()
    data['time'] = data['time'].astype(str)
    # candle_dict = data.to_dict('records')
    # vol_dict = data[['value']].to_dict('records')

    # chartOptions = {
    #     "height": 550,
    #     "handleScroll": False,
    #     "handleScale": False,
    #     "layout": {
    #         "textColor": 'black',
    #         "background": {
    #             "type": 'solid',
    #             "color": 'white'
    #         },
    #     }
    # }
    # chartMultipaneOptions = [
    #     {
    #         "height": 550,
    #         "handleScroll": False,
    #         "handleScale": False,
    #         "layout": {
    #             "background": {
    #                 "type": "solid",
    #                 "color": 'white'
    #             },
    #             "textColor": "black"
    #         },
    #         "grid": {
    #             "vertLines": {
    #                 "color": "rgba(197, 203, 206, 0.5)"
    #             },
    #             "horzLines": {
    #                 "color": "rgba(197, 203, 206, 0.5)"
    #             }
    #         },
    #         "crosshair": {
    #             "mode": 0
    #         },
    #         "priceScale": {
    #             "borderColor": "rgba(197, 203, 206, 0.8)"
    #         },
    #         "timeScale": {
    #             "borderColor": "rgba(197, 203, 206, 0.8)",
    #             "barSpacing": 10,
    #             "minBarSpacing": 8,
    #             "timeVisible": True,
    #             "secondsVisible": False,
    #         },
    #         # "watermark": {
    #         #     "visible": True,
    #         #     "fontSize": 48,
    #         #     "horzAlign": 'center',
    #         #     "vertAlign": 'center',
    #         #     "color": 'rgba(171, 71, 188, 0.3)',
    #         #     "text": 'Intraday',
    #         # }
    #     },
    #     {
    #         "height": 100,
    #         "handleScroll": False,
    #         "handleScale": False,
    #         "layout": {
    #             "background": {
    #                 "type": 'solid',
    #                 "color": 'transparent'
    #             },
    #             "textColor": 'black',
    #         },
    #         "grid": {
    #             "vertLines": {
    #                 "color": 'rgba(42, 46, 57, 0)',
    #             },
    #             "horzLines": {
    #                 "color": 'rgba(42, 46, 57, 0.6)',
    #             }
    #         },
    #         "timeScale": {
    #             "visible": False,
    #         },
    #         # "watermark": {
    #         #     "visible": True,
    #         #     "fontSize": 18,
    #         #     "horzAlign": 'left',
    #         #     "vertAlign": 'top',
    #         #     "color": 'rgba(171, 71, 188, 0.7)',
    #         #     "text": 'Volume',
    #         # }
    #     },
    # ]
    # seriesCandlestickChart = [{
    #     "type": 'Candlestick',
    #     "data": candle_dict,
    #     "options": {
    #         "upColor": '#26a69a',
    #         "downColor": '#ef5350',
    #         "borderVisible": False,
    #         "wickUpColor": '#26a69a',
    #         "wickDownColor": '#ef5350'
    #     }
    # }]
    #
    # seriesVolumeChart = [
    #     {
    #         "type": 'Histogram',
    #         "data": vol_dict,
    #         "options": {
    #             "priceFormat": {
    #                 "type": 'volume',
    #             },
    #             "priceScaleId": ""  # set as an overlay setting,
    #         },
    #         "priceScale": {
    #             "scaleMargins": {
    #                 "top": 0,
    #                 "bottom": 0,
    #             },
    #             "alignLabels": False
    #         }
    #     }
    # ]

    # renderLightweightCharts([
    #     {
    #         "chart": chartMultipaneOptions[0],
    #         "series": seriesCandlestickChart
    #     },
    #     {
    #         "chart": chartMultipaneOptions[1],
    #         "series": seriesCandlestickChart
    #     },
    # ], 'multipane')
    COLOR_BULL = 'rgba(38,166,154,0.9)'  # #26a69a
    COLOR_BEAR = 'rgba(239,83,80,0.9)'  # #ef5350

    data['chg'] = (data['close'] - data['open']) / data['open']
    data.loc[data[data['chg'] <= 0].index, 'color'] = 'red'

    candles = json.loads(data.to_json(orient="records"))
    volume = json.loads(data.to_json(orient="records"))

    chartMultipaneOptions = [
        {
            "height": 550,
            "handleScroll": False,
            "handleScale": False,
            "layout": {
                "background": {
                    "type": "solid",
                    "color": 'white'
                },
                "textColor": "black"
            },
            "grid": {
                "vertLines": {
                    "color": "rgba(197, 203, 206, 0.5)"
                },
                "horzLines": {
                    "color": "rgba(197, 203, 206, 0.5)"
                }
            },
            "crosshair": {
                "mode": 0
            },
            "priceScale": {
                "borderColor": "rgba(197, 203, 206, 0.8)"
            },
            "timeScale": {
                "borderColor": "rgba(197, 203, 206, 0.8)",
                "barSpacing": 15
            },
            # "watermark": {
            #     "visible": True,
            #     "fontSize": 48,
            #     "horzAlign": 'center',
            #     "vertAlign": 'center',
            #     "color": 'rgba(171, 71, 188, 0.3)',
            #     "text": 'AAPL - D1',
            # }
        },
        {
            "height": 100,
            "handleScroll": False,
            "handleScale": False,
            "layout": {
                "background": {
                    "type": 'solid',
                    "color": 'transparent'
                },
                "textColor": 'black',
            },
            "grid": {
                "vertLines": {
                    "color": "rgba(197, 203, 206, 0.5)"
                },
                "horzLines": {
                    "color": "rgba(197, 203, 206, 0.5)"
                }
            },
            "timeScale": {
                "borderColor": "rgba(197, 203, 206, 0.8)",
                "barSpacing": 15
            },
            "priceScale": {
                "borderColor": "rgba(197, 203, 206, 0.8)"
            },
            # "watermark": {
            #     "visible": True,
            #     "fontSize": 18,
            #     "horzAlign": 'left',
            #     "vertAlign": 'top',
            #     "color": 'rgba(171, 71, 188, 0.7)',
            #     "text": 'Volume',
            # }
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
                "priceFormat": {
                    "type": 'volume',
                },
            #     "priceScaleId": ""  # set as an overlay setting,
            # },
            # "priceScale": {
            #     "scaleMargins": {
            #         "top": 0,
            #         "bottom": 0,
            #     },
            #     # "alignLabels": False
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


def compute_logdiff(series_1, series_2):
    logdata = np.log(pd.concat([series_1, series_2], axis=1).dropna())
    logdata = logdata - logdata.iloc[0]
    logdata.columns = [0, 1]
    return logdata[0] - logdata[1]


def resample_candlestick(stock_data, timeframe):
    apply_map = {'PX_OPEN': 'first',
                 'PX_HIGH': 'max',
                 'PX_LOW': 'min',
                 'PX_LAST': 'last',
                 'PX_TURNOVER': "sum"}
    resampled_stock_data = stock_data.copy().resample(timeframe).apply(apply_map)
    return resampled_stock_data.rename(index={resampled_stock_data.index[-1]: stock_data.index[-1]}).dropna()


def main():
    st.set_page_config(
        page_title="Superchart",
        page_icon="📈",
        layout='wide'
    )
    st.sidebar.subheader("""📈 Superchart""")
    with open(os.path.join(os.getenv("PATH_TO_DATA_FOLDER"), 'ticker_list.p'), 'rb') as f:
        ticker_turnovers = pickle.load(f)
    with open(os.path.join(os.getenv("PATH_TO_DATA_FOLDER"), 'mcftr.p'), 'rb') as f:
        benchmark_raw = pickle.load(f)
    with open(os.path.join(os.getenv("PATH_TO_DATA_FOLDER"), 'base_dict.p'), 'rb') as f:
        base_dict = pickle.load(f)
    with open(os.path.join(os.getenv("PATH_TO_DATA_FOLDER"), 'div_table.p'), 'rb') as f:
        div_table = pickle.load(f)
    selected_stock = st.sidebar.selectbox("Select asset:", ticker_turnovers.index.to_list())
    st.subheader(f"""{selected_stock} dividend adjusted""")
    stock_data = base_dict[selected_stock][['PX_OPEN', 'PX_LAST', 'PX_LOW', 'PX_HIGH', 'PX_TURNOVER']]
    try:
        rt_candle, time_updated = get_current_candle("MOEX", selected_stock, div_table)
        if rt_candle is None:
            st.markdown(f"Price updated at: **{stock_data.index[-1]:%d.%m.%Y}**")
        elif len(rt_candle.dropna()) == 1:
            # print("rt_candle is not empty")
            if not rt_candle.index[0] in stock_data.index:
                stock_data = pd.concat([stock_data, rt_candle[['PX_OPEN', 'PX_LAST', 'PX_LOW', 'PX_HIGH', 'PX_TURNOVER']]])
                print(stock_data)
                st.markdown(f"Price updated at: **{rt_candle.index[0]:%d.%m.%Y}** **{time_updated}**")
            else:
                st.markdown(f"Price updated_at: **{stock_data.index[-1]:%d.%m.%Y}**")
        else:
            st.markdown(f"Price updated at: **{stock_data.index[-1]:%d.%m.%Y}**")
    except Exception:
        print(traceback.format_exc())
        st.markdown(f"Price updated at: **{stock_data.index[-1]:%d.%m.%Y}**")
    st.markdown(
        f"Median turnover over last 90 calendar days: **{int(ticker_turnovers.loc[selected_stock] / 1e6)} M RUB**")
    selected_timeframe = st.selectbox("Select timeframe:", ['Daily', 'Weekly', 'Monthly'])

    if selected_timeframe == 'Daily':
        render_candlestick_chart(
            stock_data[['PX_OPEN', 'PX_LAST', 'PX_LOW', 'PX_HIGH', 'PX_TURNOVER']].dropna().iloc[-252:])
    elif selected_timeframe == 'Weekly':
        render_candlestick_chart(
            resample_candlestick(
                stock_data[['PX_OPEN', 'PX_LAST', 'PX_LOW', 'PX_HIGH', 'PX_TURNOVER']].dropna().iloc[-252 * 5:],
                'W-FRI'))
    elif selected_timeframe == 'Monthly':
        render_candlestick_chart(
            resample_candlestick(
                stock_data[['PX_OPEN', 'PX_LAST', 'PX_LOW', 'PX_HIGH', 'PX_TURNOVER']].dropna().iloc[-252 * 15:],
                'M'))
    st.subheader(f"""Log diff. ({selected_stock} vs MCFTR)""")
    st.markdown(f"Price updated at: **{benchmark_raw.index[-1]:%d.%m.%Y}**")
    for lookback_period, timeframe in zip([365, 1095, 1825, 5475], ['1d', '1d', 'W-FRI', 'M']):
        benchmark = benchmark_raw.resample('1d').last().ffill().dropna().iloc[
                    -lookback_period:]
        last_prices = stock_data['PX_LAST'].resample('1d').last().ffill().dropna().iloc[-lookback_period:]
        if timeframe != '1d':
            benchmark = benchmark.resample(timeframe).last().ffill()
            last_prices = last_prices.resample(timeframe).last().ffill()
        logdiff = compute_logdiff(last_prices, benchmark).reindex(
            benchmark.index).bfill()
        st.text(
            f'last {int(lookback_period / 365)} years, timeframe {timeframe.replace("W-FRI", "weekly").replace("M", "monthly").replace("1d", "daily")}')
        render_diff_chart(logdiff, f"{lookback_period}_{timeframe}")


main()












(ticker_prices_df, traded_date) = get_current_candle('WALMEX.MX')


data = load_dataset('WALMEX.MX')
data = data.rename(
    columns={"PX_LAST": 'close', 'PX_LOW': 'low', 'PX_HIGH': 'high', 'PX_OPEN': 'open', "PX_TURNOVER": "value"}
)

#data.index.name = 'time'
#data = data.reset_index()
data['time'] = data['price_date'].astype(str)
COLOR_BULL = 'rgba(38,166,154,0.9)'  # Color para velas alcistas
COLOR_BEAR = 'rgba(239,83,80,0.9)'  # Color para velas bajistas

data['chg'] = (data['close'] - data['open']) / data['open']
data['color'] = data['chg'].apply(lambda x: 'red' if x <= 0 else 'green')

candles = json.loads(data.to_json(orient="records"))
volume = json.loads(data.to_json(orient="records"))
