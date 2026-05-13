import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from utils import get_headers, SUPABASE_URL

def mostrar(data):
    st.title("🎓 Panel del Estudiante")
    
    headers = get_headers()
    
    # Obtener datos actualizados
    url = f"{SUPABASE_URL}/rest/v1/personas?id_persona=eq.{data['id_persona']}"
    response = requests.get(url, headers=headers)
    persona = response.json()[0] if response.status_code == 200 and response.json() else data
    
    # Obtener username
    url_user = f"{SUPABASE_URL}/rest/v1/usuarios_login?id_persona=eq.{data['id_persona']}"
    response_user = requests.get(url_user, headers=headers)
    username = response_user.json()[0]["username"] if response_user.status_code == 200 and response_user.json() else None
    
    usuario = {
        "id_persona": persona.get("id_persona"),
        "nombre": persona.get("nombre"),
        "email": persona.get("email"),
        "telefono": persona.get("telefono"),
        "username": username
    }
    
    # Pestañas
    tab_perfil, tab_notas = st.tabs(["👤 Mi Perfil", "📖 Mis Notas"])
    
    with tab_perfil:
        mostrar_perfil(usuario)
    
    with tab_notas:
        st.subheader("Mis Calificaciones")
        st.write("**Matemáticas:** 4.5")
        st.write("**Ciencias:** 3.8")
        st.write("**Español:** 4.2")
        st.write("**Promedio:** 4.2")
