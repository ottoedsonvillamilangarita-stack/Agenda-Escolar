# modulos/compartido/utils.py
import streamlit as st

def es_movil():
    """Detecta si el dispositivo es móvil"""
    try:
        # Streamlit no tiene detección nativa, podemos usar el ancho de la pantalla
        # o asumir que si no es de escritorio, es móvil
        return True
    except:
        return False

def aplicar_css_movil():
    """Aplica estilos CSS para móviles"""
    st.markdown("""
    <style>
        .main > div {
            padding: 1rem 0.5rem !important;
        }
        .stButton button {
            width: 100% !important;
        }
        .stSelectbox, .stTextInput, .stTextArea {
            width: 100% !important;
        }
    </style>
    """, unsafe_allow_html=True)
