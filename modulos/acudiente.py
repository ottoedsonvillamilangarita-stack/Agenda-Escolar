import streamlit as st
import requests
from utils import get_headers, SUPABASE_URL
from perfil import mostrar_perfil

def mostrar(data):
    st.title("👨‍👩‍👧 Panel del Acudiente")
    
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
    
    tab_perfil, tab_hijos = st.tabs(["👤 Mi Perfil", "👨‍👩‍👧 Mis Hijos"])
    
    with tab_perfil:
        mostrar_perfil(usuario)
    
    with tab_hijos:
        st.subheader("Mis Hijos")
        st.write("Próximamente: lista de hijos y sus notas")
