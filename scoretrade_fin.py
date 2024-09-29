
import streamlit as st
import replicate
import os
import pdfplumber
from docx import Document
import pandas as pd
from io import BytesIO
from transformers import AutoTokenizer
import exifread
import requests
from PIL import Image
import numpy as np
import plotly.express as px
import matplotlib.colors as mcolorspi
import plotly.graph_objs as go
import streamlit.components.v1 as components
import random


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
    "assistant": "https://raw.githubusercontent.com/sahirmaharaj/exifa/2f685de7dffb583f2b2a89cb8ee8bc27bf5b1a40/img/assistant-done.svg",
    "user": "https://raw.githubusercontent.com/sahirmaharaj/exifa/2f685de7dffb583f2b2a89cb8ee8bc27bf5b1a40/img/user-done.svg",
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

@st.cache_data
def load_dataset(ticket):
    folder_path = 'C:/Users/irvin/OneDrive/Desktop/python_scripts/codigo_proyecto_aplicacion/modelos'
    df = pd.read_csv(f'{folder_path}/{ticket}/data_input.csv', parse_dates=True)
    df["Date"] = pd.to_datetime(df["Date"])
    df["BarColor"] = df[["Open", "Close"]].apply(lambda o: "red" if o.Open > o.Close else "green", axis=1)
    df["Date_str"] = df["Date"].astype(str)
    
    return df


st.set_page_config(page_title="ScoreTrade", page_icon="📈", layout="wide")


message = random.choice(welcome_messages)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": message}]
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": message}]
if "exif_df" not in st.session_state:
    st.session_state["exif_df"] = pd.DataFrame()
if "url_exif_df" not in st.session_state:
    st.session_state["url_exif_df"] = pd.DataFrame()
if "show_expanders" not in st.session_state:
    st.session_state.show_expanders = True
if "reset_trigger" not in st.session_state:
    st.session_state.reset_trigger = False
if "uploaded_files" not in st.session_state:
    st.session_state["uploaded_files"] = None
if "image_url" not in st.session_state:
    st.session_state["image_url"] = ""
if "follow_up" not in st.session_state:
    st.session_state.follow_up = False
if "show_animation" not in st.session_state:
    st.session_state.show_animation = True



def clear_url():
    st.session_state["image_url"] = ""

def clear_files():
    st.session_state["uploaded_files"] = None
    st.session_state["file_uploader_key"] = not st.session_state.get(
        "file_uploader_key", False
    )



with st.sidebar:

    image_logo = (
       "C:/Users/irvin/OneDrive/Desktop/python_scripts/codigo_proyecto_aplicacion/scoretrade/img/Exifa.gift"
    )

    st.markdown(
        f"""
        <div style='display: flex; align-items: center;'>
            <img src='{image_logo}' style='width: 60px; height: 60px; margin-right: 30px;'>
            <h1 style='margin: 0;'>Exifa.net</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    expander = st.expander("🗀 File Input")
    with expander:

        # Simulación de los mejores tickets
        best_tickets = ["","AAPL", "GOOGL", "AMZN", "TSLA", "MSFT", "NFLX", "NVDA", "META"]

        # Cuadro desplegable para seleccionar un ticket
        selected_ticket = st.selectbox(
            "Mejores tickets para invertir hoy:",
            best_tickets
        )
        

        image_url = st.text_input(
            "Enter image URL for EXIF analysis:",
            key="image_url",
            on_change=clear_files,
            value=st.session_state.image_url,
        )

        file_uploader_key = "file_uploader_{}".format(
            st.session_state.get("file_uploader_key", False)
        )

        uploaded_files = st.file_uploader(
            "Upload local files:",
            type=["txt", "pdf", "docx", "csv", "jpg", "png", "jpeg"],
            key=file_uploader_key,
            on_change=clear_url,
            accept_multiple_files=True,
        )

        if uploaded_files is not None:
            st.session_state["uploaded_files"] = uploaded_files
    expander = st.expander("⚒ Model Configuration")
    with expander:

        if "REPLICATE_API_TOKEN" in st.secrets:
            replicate_api = st.secrets["REPLICATE_API_TOKEN"]
        else:
            replicate_api = st.text_input("Enter Replicate API token:", type="password")
            if not (replicate_api.startswith("r8_") and len(replicate_api) == 40):
                st.warning("Please enter your Replicate API token.", icon="⚠️")
                st.markdown(
                    "**Don't have an API token?** Head over to [Replicate](https://replicate.com/account/api-tokens) to sign up for one."
                )
        os.environ["REPLICATE_API_TOKEN"] = replicate_api
        st.subheader("Adjust model parameters")
        temperature = st.slider(
            "Temperature", min_value=0.01, max_value=5.0, value=0.3, step=0.01
        )
        top_p = st.slider("Top P", min_value=0.01, max_value=1.0, value=0.2, step=0.01)
        max_new_tokens = st.number_input(
            "Max New Tokens", min_value=1, max_value=1024, value=512
        )
        min_new_tokens = st.number_input(
            "Min New Tokens", min_value=0, max_value=512, value=0
        )
        presence_penalty = st.slider(
            "Presence Penalty", min_value=0.0, max_value=2.0, value=1.15, step=0.05
        )
        frequency_penalty = st.slider(
            "Frequency Penalty", min_value=0.0, max_value=2.0, value=0.2, step=0.05
        )
        stop_sequences = st.text_area("Stop Sequences", value="<|im_end|>", height=100)
    if uploaded_files and not st.session_state["exif_df"].empty:
        with st.expander("🗏 EXIF Details"):
            st.dataframe(st.session_state["exif_df"])
    if image_url and not st.session_state["url_exif_df"].empty:
        with st.expander("🗏 EXIF Details"):
            st.dataframe(st.session_state["url_exif_df"])
    base_prompt = """
     
    You are an expert EXIF Analyser. The user will provide an image file and you will explain the file EXIF in verbose detail.
    
    Pay careful attention to the data of the EXIF image and create a profile for the user who took this image. 
    
    1. Make inferences on things like location, budget, experience, etc. (2 paragraphs) 
    2. Make as many inferences as possible about the exif data in the next 3 paragraphs.
    
    3. Please follow this format, style, pacing and structure. 
    4. In addition to the content above, provide 1 more paragraph about the users financial standing based on the equipment they are using and estimate their experience.
    
    DO NOT skip any steps.
    
    FORMAT THE RESULT IN MULTIPLE PARAGRAPHS
    
    Do not keep talking and rambling on - Get to the point. 
    
    """









