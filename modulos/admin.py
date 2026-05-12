import streamlit as st
import pandas as pd
import requests
from utils import SUPABASE_URL, get_headers
from perfil import mostrar_perfil
def mostrar(data):
    st.title("⚙️ Administración")
    
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
    
    tab_perfil, tab_usuarios, tab_carga, tab_config = st.tabs(["👤 Mi Perfil", "👥 Usuarios", "📤 Carga Masiva", "⚙️ Configuración"])
    
    with tab_perfil:
        mostrar_perfil(usuario)
    
    with tab_usuarios:
        st.subheader("Usuarios del Sistema")
        url_users = f"{SUPABASE_URL}/rest/v1/usuarios_login"
        response_users = requests.get(url_users, headers=headers)
        if response_users.status_code == 200 and response_users.json():
            for user in response_users.json():
                st.write(f"• **{user['username']}** - {user.get('rol', 'sin rol')} - {user['nombre']}")
        else:
            st.info("No hay usuarios registrados")
    
    with tab_carga:
        st.subheader("📤 Carga Masiva de Datos")
        st.info("Aquí se cargarán los archivos Excel con estudiantes y docentes")
        archivo = st.file_uploader("Seleccionar archivo", type=["xlsx"])
        if archivo:
            st.success(f"Archivo recibido: {archivo.name}")
    
    with tab_config:
        st.subheader("Configuración General")
        st.write("**Periodos académicos:** Periodo I, II, III, IV")
        st.write("**Escala de notas:** 0 a 5")
        st.write("**Nota mínima aprobatoria:** 3.0")
