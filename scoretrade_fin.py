
import streamlit as st
import os
import pandas as pd
from PIL import Image
import numpy as np
import plotly.express as px
import matplotlib.colors as mcolorspi
import plotly.graph_objs as go
import streamlit.components.v1 as components
import random
import pickle
import json
from streamlit_lightweight_charts import renderLightweightCharts
import streamlit_lightweight_charts.dataSamples as data
import sklearn
import re

config = {
    "toImageButtonOptions": {
        "format": "png",
        "filename": "custom_image",
        "height": 720,
        "width": 480,
        "scale": 6,
    }
}

icons = {
    "assistant": "https://raw.githubusercontent.com/IrvingLedezma/ScoreTrade/main/img/logo_welcome.gif"
}


particles_js = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Particles.js</title>
  <style>
  #particles-js {
    position: fixed;
    width: 100vw;
    height: 100vh;
    top: 0;
    left: 0;
    z-index: -1; /* Send the animation to the back */
  }
  .content {
    position: relative;
    z-index: 1;
    color: white;
  }
  
</style>
</head>
<body>
  <div id="particles-js"></div>
  <div class="content">
    <!-- Placeholder for Streamlit content -->
  </div>
  <script src="https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js"></script>
  <script>
    particlesJS("particles-js", {
      "particles": {
        "number": {
          "value": 300,
          "density": {
            "enable": true,
            "value_area": 800
          }
        },
        "color": {
          "value": "#ffffff"
        },
        "shape": {
          "type": "circle",
          "stroke": {
            "width": 0,
            "color": "#000000"
          },
          "polygon": {
            "nb_sides": 5
          },
          "image": {
            "src": "img/github.svg",
            "width": 100,
            "height": 100
          }
        },
        "opacity": {
          "value": 0.5,
          "random": false,
          "anim": {
            "enable": false,
            "speed": 1,
            "opacity_min": 0.2,
            "sync": false
          }
        },
        "size": {
          "value": 2,
          "random": true,
          "anim": {
            "enable": false,
            "speed": 40,
            "size_min": 0.1,
            "sync": false
          }
        },
        "line_linked": {
          "enable": true,
          "distance": 100,
          "color": "#ffffff",
          "opacity": 0.22,
          "width": 1
        },
        "move": {
          "enable": true,
          "speed": 0.2,
          "direction": "none",
          "random": false,
          "straight": false,
          "out_mode": "out",
          "bounce": true,
          "attract": {
            "enable": false,
            "rotateX": 600,
            "rotateY": 1200
          }
        }
      },
      "interactivity": {
        "detect_on": "canvas",
        "events": {
          "onhover": {
            "enable": true,
            "mode": "grab"
          },
          "onclick": {
            "enable": true,
            "mode": "repulse"
          },
          "resize": true
        },
        "modes": {
          "grab": {
            "distance": 100,
            "line_linked": {
              "opacity": 1
            }
          },
          "bubble": {
            "distance": 400,
            "size": 2,
            "duration": 2,
            "opacity": 0.5,
            "speed": 1
          },
          "repulse": {
            "distance": 200,
            "duration": 0.4
          },
          "push": {
            "particles_nb": 2
          },
          "remove": {
            "particles_nb": 3
          }
        }
      },
      "retina_detect": true
    });
  </script>
</body>
</html>
"""

# Mensajes de bienvenida adaptados a ScoreTrade
welcome_messages = [
    "¡Hola! Bienvenido a ScoreTrade, tu plataforma de recomendaciones bursátiles.",
    "¡Bienvenido a ScoreTrade! Aquí encontrarás las mejores recomendaciones para tus decisiones en el mercado de valores.",
    "¡Hola! ScoreTrade está aquí para ofrecerte análisis y recomendaciones personalizadas para tus inversiones.",
    "¡Bienvenido! En ScoreTrade te ayudamos a tomar decisiones informadas en la bolsa.",
    "¡Hola! Bienvenido a ScoreTrade, donde las decisiones bursátiles son más sencillas.",
    "¡Hola! Bienvenido a ScoreTrade, tu espacio para recomendaciones y análisis del mercado financiero.",
    "¡Bienvenido a ScoreTrade! Encuentra aquí recomendaciones personalizadas para tus inversiones.",
    "¡Hola! En ScoreTrade encontrarás las mejores herramientas y recomendaciones para tus estrategias en la bolsa.",
    "¡Bienvenido a ScoreTrade! Aquí podrás acceder a recomendaciones que optimicen tus decisiones en el mercado.",
    "¡Hola! Bienvenido a ScoreTrade, tu guía para tomar decisiones acertadas en el mercado de valores.",
]


st.set_page_config(page_title="ScoreTrade", page_icon="📈", layout="wide")


if "message" not in st.session_state:
    st.session_state.message = ''
if "show_animation" not in st.session_state:
    st.session_state.show_animation = True
if "folder_path" not in st.session_state:
    st.session_state.folder_path = 'C:/Users/irvin/OneDrive/Desktop/python_scripts/codigo_proyecto_aplicacion/modelos'
if "tickets_nacionales" not in st.session_state:
    st.session_state.tickets_nacionales = ['ALPEKA.MX', 'GFINBURO.MX', 'ASURB.MX', 'MEGACPO.MX', 'FEMSAUBD.MX', 'BOLSAA.MX']
if "tickets_internacionales" not in st.session_state:
    st.session_state.tickets_internacionales = ['AAPL', 'MSFT', 'AMZN', 'NVDA', 'GOOGL', 'TSLA', 'META', 'JPM']
if 'ticket_nal' not in st.session_state:
    st.session_state.ticket_nal = 'ALPEKA.MX'
if 'ticket_inter' not in st.session_state:
    st.session_state.ticket_inter = 'AAPL'
if 'ticket' not in st.session_state:
    st.session_state.ticket = ''
if 'ver_tickets' not in st.session_state:
    st.session_state.ver_tickets = False
if 'filter_pos' not in st.session_state:
    st.session_state.filter_pos = 1
if 'selected' not in st.session_state:
    st.session_state.selected = 'Detalles de score'  
if 'map_ext_ind' not in st.session_state:
    st.session_state.map_ext_ind = {} 
if 'indicators_dict' not in st.session_state:
    st.session_state.indicators_dict = {} 
if 'index_info' not in st.session_state:
    st.session_state.index_info = {} 



@st.cache_data
def load_dataset(ticket):
    df = pd.read_csv(f'{st.session_state.folder_path}/{ticket}/data_input.csv', parse_dates=True)
    df["Date"] = pd.to_datetime(df["Date"])
    df["BarColor"] = df[["Open", "Close"]].apply(lambda o: "red" if o.Open > o.Close else "green", axis=1)
    df["Date_str"] = df["Date"].astype(str)
    
    return df

@st.cache_data
def load_top():
    df = pd.read_csv(f'{st.session_state.folder_path}/top_data.csv', parse_dates=True)    
    return df

@st.cache_data
def get_current_date(ticket='WALMEX.MX'):

  df = pd.read_csv(f'{st.session_state.folder_path}/{ticket}/data_input.csv', parse_dates=['Date'])

  # Obtener la última fecha disponible en el archivo
  last_date = df['Date'].max()
  return pd.Timestamp(last_date).replace(hour=0, minute=0, second=0)

@st.cache_data
def get_metrics():
  dict_data_front = {}
  for ticket in st.session_state.tickets_nacionales: #+ st.session_state.tickets_internacionales:
    dict_data_front[ticket] = {}

    with open(f'{st.session_state.folder_path}/{ticket}/data_predict.pkl', 'rb') as f:
      dict_data_front[ticket]['data_predict'] = pd.read_pickle(f) 
    with open(f'{st.session_state.folder_path}/{ticket}/data_input.pkl', 'rb') as f:
      dict_data_front[ticket]['data_input'] = pd.read_pickle(f) 
    with open(f'{st.session_state.folder_path}/{ticket}/best_biva_lr.pkl', 'rb') as f:
      dict_data_front[ticket]['df_bivas'] = pd.read_pickle(f) 
    with open(f'{st.session_state.folder_path}/{ticket}/best_model_lr.pkl', 'rb') as f:
      dict_data_front[ticket]['best_model_lr'] = pd.read_pickle(f)
    with open(f'{st.session_state.folder_path}/{ticket}/ohe_feature_names.pkl', 'rb') as f:
      dict_data_front[ticket]['ohe_feature_names'] = pd.read_pickle(f)

  return dict_data_front

def get_maps():   
  with open(f'{st.session_state.folder_path}/map_ext_ind.pkl', 'rb') as f:
    st.session_state.map_ext_ind = pd.read_pickle(f)
  with open(f'{st.session_state.folder_path}/indicators_dict.pkl', 'rb') as f:
    st.session_state.indicators_dict = pd.read_pickle(f)
  st.session_state.indicators_dict = {
      key.replace('.', '_').replace(' ', ''): value
      for key, value in st.session_state.indicators_dict.items()
  }
  with open(f'{st.session_state.folder_path}/index_info.pkl', 'rb') as f:
    st.session_state.index_info = pd.read_pickle(f)


def get_message_welcome():
  st.session_state.message = random.choice(welcome_messages)

def select_ticket(type_):
  if type_ == 'nacional':
    st.session_state.ticket = st.session_state.ticket_nal
  elif type_ == 'internacional' :
    st.session_state.ticket = st.session_state.ticket_inter
  st.session_state.ver_tickets = True

def get_rango(value, df_biva):
  list_max = df_biva['Máx Score'].to_list()
  out = 0
  for limit in list_max:
    out += 1 
    if value<=limit:
      return out
  return out
   
def highlight_score(row):
    if row['# Rango'] == st.session_state.filter_pos:
        return ['background-color: #5d6d7e' if col in ['Min Score', 'Máx Score'] else '' for col in row.index]
    else:
        return ['' for _ in row]  # No aplicar estilo en otros casos
 
def get_df_biva_fancy(df_biva):  
  styled_df = (
      df_biva.style
      .apply(highlight_score, axis=1)  # subset=['Ticket'], Aplicar el color a la fila de GOOGL
      .format(precision=2)
      .bar(align="mid", color="#283747", vmin=0, vmax=100, subset=["% Tasa de crecimiento del precio"])
      .set_properties(**{
      "border": "1px solid #1c2833",  # Eliminar los bordes
      "border-radius": "5px",  # Hacer bordes circulares (ajustable)
      "padding": "5px",  # Agregar algo de espacio alrededor del contenido para que se vea mejor
      "width": "90px"  # Ajustar el ancho de las columnas
      })
      .set_table_styles([{
          "border": "1px solid #1c2833",  # Eliminar los bordes
          'selector': 'thead th',  # Aplicar estilo a la cabecera (header)
          'props': [('background-color', '#17202a')]  # Cambiar el color de fondo de la cabecera (hexadecimal)
      }])
      .hide(axis="index")
  )
  st.write(styled_df.to_html(), unsafe_allow_html=True)

def render_candlestick_chart(data):
    data['Date'] = data.index
    data = data.rename(columns={
          "Date": 'price_date',
          "Open": 'open',
          "Low": 'low',
          "High": 'high',
          "Close": 'close',
          "Volume": 'value'
      })
    
    data = data[['price_date','open','low','high','close','value']].copy()
    data = data.dropna()

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
            "handleScale": True,
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
            "handleScale": True,
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




with st.sidebar:

    image_logo = (
       "https://raw.githubusercontent.com/IrvingLedezma/ScoreTrade/main/img/logo_fin.gif"
    )

    st.markdown(
        f"""
        <div style='display: flex; align-items: center;'>
            <img src='{image_logo}' style='width: 130px; height: 130px; margin-right: 1px;'>
            <h1 style='margin: 0;'>ScoreTrade.Net</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)  # Agrega un espacio entre los elementos

    st.markdown(
        f"""
        <div style='display: flex; align-items: center;'>
            <h1 style='margin: 0; font-size: 18px;'>❆ Elige tus tickets</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    expander = st.expander("Tickets nacionales (BMV)", 
                            expanded=True)

    with expander:

      ticket_nal = st.selectbox(
          "Selecciona para ver detalles",
          st.session_state.tickets_nacionales,
          key='ticket_nal',
          on_change=select_ticket,
          args=('nacional',),  # Se pasa 'nacional' como una tupla
      )

    expander = st.expander("Tickets internacionales (SIC)", 
                            expanded=True)

    with expander:

      ticket_inter = st.selectbox(
          "Selecciona para ver detalles",
          st.session_state.tickets_internacionales,
          key='ticket_inter',
          on_change=select_ticket,
          args=('internacional',),  # Se pasa 'internacional' como una tupla
      )

    expander = st.expander("⚒ Strategy Lab") 
    with expander:

        st.subheader("Ajustar riesgo")
        temperature = st.slider(
            "Radio varianza media", min_value=0.01, max_value=5.0, value=0.3, step=0.01
        )

    if st.session_state.ver_tickets:    
      left, right = st.columns(2)

      if left.button("Series de tiempo", use_container_width=True):
          st.session_state.selected = 'Series de tiempo'
      if right.button("Detalles de score", use_container_width=True):
          st.session_state.selected = 'Detalles de score'
      if st.session_state.selected == 'Series de tiempo':
          left.markdown("Se están mostrando las series de tiempo")
      elif st.session_state.selected == 'Detalles de score':
          right.markdown("Se están mostrando los detalles de los scores")




# ==================================
# Main 
# ==================================


if not st.session_state.ver_tickets:

  get_message_welcome()
  with st.chat_message('assistant', avatar=icons['assistant']):
      st.write(st.session_state.message)

  topdata = load_top()
  date_updt = get_current_date()
  date_updt_str = date_updt.strftime('%d.%m.%Y')

  # Tipo de Mercado
  mercado_option = st.radio(
      "Selecciona el Tipo de Mercado",
      ("Mercado Nacional (BMV)", "Mercado Internacional (SIC)"),
      horizontal=True,
      label_visibility= "collapsed"
  )

  if mercado_option == "Mercado Nacional (BMV)":
      topdf = topdata[topdata['mercado']=='nacional']
  else:
      topdf = topdata[topdata['mercado']=='internacional']
        
  # Título para las métricas
  st.markdown(f"<h2 style='font-size: 1.1em;'>💲 Top 5 Buying Score (Mayor probabilidad de alza de precio)  {date_updt_str}</h2>", unsafe_allow_html=True)

  # Crear las columnas
  col1, col2, col3, col4, col5 = st.columns(5)

  # Definir métricas en cada columna
  with col1:
      st.metric(label=f"{topdf[topdf['tipo']=='bsscore1']['ticket'].values[0]}", 
                value=f"{topdf[topdf['tipo']=='bsscore1']['valor'].values[0]}%", 
                delta=f"{topdf[topdf['tipo']=='bsscore1']['delta'].values[0]}%")
  with col2:
      st.metric(label=f"{topdf[topdf['tipo']=='bsscore2']['ticket'].values[0]}", 
                value=f"{topdf[topdf['tipo']=='bsscore2']['valor'].values[0]}%", 
                delta=f"{topdf[topdf['tipo']=='bsscore2']['delta'].values[0]}%")
  with col3:
      st.metric(label=f"{topdf[topdf['tipo']=='bsscore3']['ticket'].values[0]}", 
                value=f"{topdf[topdf['tipo']=='bsscore3']['valor'].values[0]}%", 
                delta=f"{topdf[topdf['tipo']=='bsscore3']['delta'].values[0]}%")
  with col4:
      st.metric(label=f"{topdf[topdf['tipo']=='bsscore4']['ticket'].values[0]}", 
                value=f"{topdf[topdf['tipo']=='bsscore4']['valor'].values[0]}%", 
                delta=f"{topdf[topdf['tipo']=='bsscore4']['delta'].values[0]}%")
  with col5:
      st.metric(label=f"{topdf[topdf['tipo']=='bsscore5']['ticket'].values[0]}", 
                value=f"{topdf[topdf['tipo']=='bsscore5']['valor'].values[0]}%", 
                delta=f"{topdf[topdf['tipo']=='bsscore5']['delta'].values[0]}%")

  # Título para las métricas
  st.markdown(f"<h2 style='font-size: 1.1em;'>⛔ Top 5 Selling Score (Mayor probabilidad de baja de precio)  {date_updt_str}</h2>", unsafe_allow_html=True, help="Esto es una ayuda")

  # Crear las columnas
  col1, col2, col3, col4, col5 = st.columns(5)

  # Definir métricas en cada columna
  with col1:
      st.metric(label=f"{topdf[topdf['tipo']=='ssscore1']['ticket'].values[0]}", 
                value=f"{topdf[topdf['tipo']=='ssscore1']['valor'].values[0]}%", 
                delta=f"{topdf[topdf['tipo']=='ssscore1']['delta'].values[0]}%")
  with col2:
      st.metric(label=f"{topdf[topdf['tipo']=='ssscore2']['ticket'].values[0]}", 
                value=f"{topdf[topdf['tipo']=='ssscore2']['valor'].values[0]}%", 
                delta=f"{topdf[topdf['tipo']=='ssscore2']['delta'].values[0]}%")
  with col3:
      st.metric(label=f"{topdf[topdf['tipo']=='ssscore3']['ticket'].values[0]}", 
                value=f"{topdf[topdf['tipo']=='ssscore3']['valor'].values[0]}%", 
                delta=f"{topdf[topdf['tipo']=='ssscore3']['delta'].values[0]}%")
  with col4:
      st.metric(label=f"{topdf[topdf['tipo']=='ssscore4']['ticket'].values[0]}", 
                value=f"{topdf[topdf['tipo']=='ssscore4']['valor'].values[0]}%", 
                delta=f"{topdf[topdf['tipo']=='ssscore4']['delta'].values[0]}%")
  with col5:
      st.metric(label=f"{topdf[topdf['tipo']=='ssscore5']['ticket'].values[0]}", 
                value=f"{topdf[topdf['tipo']=='ssscore5']['valor'].values[0]}%", 
                delta=f"{topdf[topdf['tipo']=='ssscore5']['delta'].values[0]}%")



if st.session_state.ver_tickets and st.session_state.selected == 'Detalles de score':    
  with st.chat_message('assistant', avatar=icons['assistant']):
    st.markdown(f"A continuación los detalles de los scores {st.session_state.ticket}")

  dict_data_front = get_metrics()

  frebivas={
    'id_bin':'# Rango',
    'Min Range Bin':'Min Score',
    'Max Range Bin':'Máx Score',
    'Event Rate':'% Tasa de crecimiento del precio' 
    }
  
  biva_val = dict_data_front[st.session_state.ticket]['df_bivas']['val'].copy()
  biva_train = dict_data_front[st.session_state.ticket]['df_bivas']['train'].copy()
  biva_val.rename(columns=frebivas, inplace=True)
  biva_train.rename(columns=frebivas, inplace=True)
  list_num = ['Min Score', 'Máx Score', '% Tasa de crecimiento del precio']

  biva_val[list_num] = biva_val[list_num] * 100
  biva_val[list_num] = biva_val[list_num].round(1)  
  biva_train[list_num] = biva_train[list_num] * 100
  biva_train[list_num] = biva_train[list_num].round(1)

  last_date = dict_data_front[st.session_state.ticket]['data_predict'].index.max()
  last_date_str = last_date.strftime('%d.%m.%Y')

  score = dict_data_front[st.session_state.ticket]['data_predict']['probs'].iloc[0] * 100 
  delta_score = dict_data_front[st.session_state.ticket]['data_predict']['probs'].diff(-1).iloc[0] * 100  
  st.session_state.filter_pos = get_rango(score, biva_train)

  col1, col2, col3 = st.columns([1.5,2,2])

  with col1:
    st.markdown(f"Última actualización de score **{last_date_str}**")
    st.metric(label='🔮 Score estimado para los eventos significativos \n\n de subidas del precio en los sig. 3 día', 
              value=f"{format(score, '.1f')}%", 
              delta=f"{format(delta_score, '.2f')}%",)      
  with col2:
    st.markdown(f"Performance de score en el periodo de entrenamiento:\n\n**05.05.2023 - 23.04.2024**")
    get_df_biva_fancy(biva_train[list(frebivas.values())])
  with col3:
    st.markdown(f"Performance de score en el periodo de validación:\n\n **24.04.2024 - 10.09.2024**")
    get_df_biva_fancy(biva_val[list(frebivas.values())])


  st.markdown(f"<h2 style='font-size: 1.1em;'> 📚🧑‍🏫 Hora de aprender! 🎓 Características más importantes del modelo 😊</h2>", 
              unsafe_allow_html=True)
  
  col1, col2 = st.columns(2)

  with col1:

    model = dict_data_front[st.session_state.ticket]['best_model_lr']
    coefficients = model.coef_[0]

    feature_importance = pd.DataFrame({
        'Feature': dict_data_front[st.session_state.ticket]['ohe_feature_names'],
        'Coefficient': coefficients
    })

    feature_importance['Importance'] = feature_importance['Coefficient'].abs()
    feature_importance = feature_importance.sort_values(by='Importance', ascending=False)

    st.write("Importancia de las características en el score")
    st.dataframe(feature_importance[['Feature', 'Importance']])

  with col2:
    selected_feature = st.selectbox('Selecciona una característica', feature_importance['Feature'])

    # Mostrar el valor de la 'Feature' seleccionada
    get_maps()

    if selected_feature:
        # Filtrar la fila seleccionada
        selected_row = feature_importance[feature_importance['Feature'] == selected_feature]

        def separar_strings(cadena):
            cadena = cadena.replace('_STF', '')
            patron = r'([^_]+(?:_[^_]+)*)_(L\d+)_(EXTI\d+)_(BIN_\d+)'
            coincidencias = re.search(patron, cadena)
            if coincidencias:
                return (coincidencias.group(1), coincidencias.group(2), coincidencias.group(3), coincidencias.group(4))

            patron_sin_L = r'([^_]+(?:_[^_]+)*)_(EXTI\d+)_(BIN_\d+)'
            coincidencias_sin_L = re.search(patron_sin_L, cadena)
            if coincidencias_sin_L:
                return (coincidencias_sin_L.group(1), None, coincidencias_sin_L.group(2), coincidencias_sin_L.group(3))

            patron_sin_EXTI = r'([^_]+(?:_[^_]+)*)_(L\d+)_(BIN_\d+)'
            coincidencias_sin_EXTI = re.search(patron_sin_EXTI, cadena)
            if coincidencias_sin_EXTI:
                return (coincidencias_sin_EXTI.group(1), coincidencias_sin_EXTI.group(2), None, coincidencias_sin_EXTI.group(3))
            return None  # Si no hay coincidencias

        separacion = separar_strings(selected_feature)

        # Mostrar la característica seleccionada con ícono de check
        if selected_feature:
            st.write(f"✅ Has seleccionado: **{selected_feature}**")

        # Mostrar la importancia con un ícono de gráfico
        if selected_row is not None and 'Importance' in selected_row:
            importancia = selected_row['Importance'].values[0].round(4)
            st.write(f"📊 **Importancia:** {importancia}")

        # Mostrar el nombre del índice compuesto o futuro con ícono de gráfico de barras
        if separacion[2] is not None:
            indice = st.session_state.index_info[st.session_state.map_ext_ind[int(separacion[2].replace('EXTI', ''))]]
            st.write(f"📈 **Nombre del índice compuesto o futuro:** {indice['name']}")

            # Mostrar descripción del índice con ícono de nota
            if indice.get('description'):
                st.write(f"📝 **Descripción del índice:** {indice['description']}")

        # Mostrar el nombre del indicador técnico con ícono de gráfico
        if separacion[0] in st.session_state.indicators_dict:
            indicador = st.session_state.indicators_dict[separacion[0]]
            st.write(f"📉 **Nombre del indicador técnico:** {indicador['name']}")

            # Mostrar descripción del indicador con ícono de información
            if indicador.get('description'):
                st.write(f"ℹ️ **Descripción:** {indicador['description']}")

            # Mostrar la recomendación de compra o venta con ícono de flecha
            if indicador.get('buysell'):
                st.write(f"🔄 **¿Cuándo comprar o vender?:** {indicador['buysell']}")








if st.session_state.ver_tickets and st.session_state.selected == 'Series de tiempo':

  dict_data_front = get_metrics()
  last_date = dict_data_front[st.session_state.ticket]['data_predict'].index.max()
  last_date_str = last_date.strftime('%d.%m.%Y')
  
  with st.chat_message('assistant', avatar=icons['assistant']):
    st.markdown(f"A continuación se muestran las series de timepo para: {st.session_state.ticket}")
  st.markdown(f"Gráfico de velas, última actualizacion **{last_date_str}**")

  data_precios = dict_data_front[st.session_state.ticket]['data_input'].copy()   
  data_precios = dict_data_front[st.session_state.ticket]['data_input'].copy()   
  data_precios = data_precios.sort_index(ascending=True)
  render_candlestick_chart(data_precios)


if st.session_state.show_animation:
    components.html(particles_js, height=700, scrolling=False)







