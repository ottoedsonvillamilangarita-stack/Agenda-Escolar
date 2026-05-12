import streamlit as st
import requests
from utils import get_headers, SUPABASE_URL

def mostrar(data):
    st.title("📋 Coordinación Académica")
    
    headers = get_headers()
    
    # Obtener datos actualizados
    url = f"{SUPABASE_URL}/rest/v1/personas?id_persona=eq.{data['id_persona']}"
    response = requests.get(url, headers=headers)
    coordinador = response.json()[0] if response.status_code == 200 else data
    
    # Obtener username
    url_user = f"{SUPABASE_URL}/rest/v1/usuarios_login?id_persona=eq.{data['id_persona']}"
    response_user = requests.get(url_user, headers=headers)
    username = response_user.json()[0]["username"] if response_user.json() else None
    
    usuario_completo = {
        "id_persona": coordinador["id_persona"],
        "nombre": coordinador["nombre"],
        "email": coordinador.get("email"),
        "telefono": coordinador.get("telefono"),
        "username": username
    }
    
    tab_perfil, tab_stats = st.tabs(["👤 Mi Perfil", "📊 Estadísticas"])
    
    with tab_perfil:
        mostrar_perfil(usuario_completo)
    
    with tab_stats:
        st.subheader("Estadísticas del Colegio")
        
        # Total de estudiantes
        url_est = f"{SUPABASE_URL}/rest/v1/estudiantes_grados"
        response_est = requests.get(url_est, headers=headers)
        total_estudiantes = len(response_est.json()) if response_est.status_code == 200 else 0
        
        # Total de docentes
        url_doc = f"{SUPABASE_URL}/rest/v1/personas?rol=eq.docente"
        response_doc = requests.get(url_doc, headers=headers)
        total_docentes = len(response_doc.json()) if response_doc.status_code == 200 else 0
        
        # Total de cursos
        url_cursos = f"{SUPABASE_URL}/rest/v1/grados"
        response_cursos = requests.get(url_cursos, headers=headers)
        total_cursos = len(response_cursos.json()) if response_cursos.status_code == 200 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Estudiantes", total_estudiantes)
        with col2:
            st.metric("Total Docentes", total_docentes)
        with col3:
            st.metric("Total Cursos", total_cursos)
