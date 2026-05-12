import streamlit as st
import requests
from utils import get_headers, SUPABASE_URL
from comun.perfil import mostrar_perfil

def mostrar(data):
    st.title("👁️ Supervisión")
    
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
    
    tab_perfil, tab_supervision = st.tabs(["👤 Mi Perfil", "📊 Supervisión"])
    
    with tab_perfil:
        mostrar_perfil(usuario)
    
    with tab_supervision:
        st.subheader("Resumen General")
        
        url_est = f"{SUPABASE_URL}/rest/v1/estudiantes_grados"
        response_est = requests.get(url_est, headers=headers)
        total_estudiantes = len(response_est.json()) if response_est.status_code == 200 else 0
        
        url_doc = f"{SUPABASE_URL}/rest/v1/personas?rol=eq.docente"
        response_doc = requests.get(url_doc, headers=headers)
        total_docentes = len(response_doc.json()) if response_doc.status_code == 200 else 0
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Estudiantes", total_estudiantes)
        with col2:
            st.metric("Total Docentes", total_docentes)
