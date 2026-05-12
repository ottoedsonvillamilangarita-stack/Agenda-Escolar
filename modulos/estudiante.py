import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from utils import get_headers, SUPABASE_URL

def mostrar(data):
    st.title("🎓 Panel del Estudiante")
    
    headers = get_headers()
    
    # Obtener datos actualizados del estudiante
    url = f"{SUPABASE_URL}/rest/v1/personas?id_persona=eq.{data['id_persona']}"
    response = requests.get(url, headers=headers)
    estudiante = response.json()[0] if response.status_code == 200 else data
    
    # Obtener username
    url_user = f"{SUPABASE_URL}/rest/v1/usuarios_login?id_persona=eq.{data['id_persona']}"
    response_user = requests.get(url_user, headers=headers)
    username = response_user.json()[0]["username"] if response_user.json() else None
    
    # Datos completos del usuario
    usuario_completo = {
        "id_persona": estudiante["id_persona"],
        "nombre": estudiante["nombre"],
        "email": estudiante.get("email"),
        "telefono": estudiante.get("telefono"),
        "username": username
    }
    
    # ========== PESTAÑAS ==========
    tab_perfil, tab_notas = st.tabs(["👤 Mi Perfil", "📖 Mis Notas"])
    
    # ========== PESTAÑA PERFIL (simplificada, sin errores) ==========
    with tab_perfil:
        st.subheader("👤 Mi Perfil")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Nombre:**")
            st.write(usuario_completo.get("nombre", "No registrado"))
            st.write("**Usuario:**")
            st.write(usuario_completo.get("username", "No registrado"))
        with col2:
            st.write("**Email:**")
            st.write(usuario_completo.get("email", "No registrado"))
            st.write("**Teléfono:**")
            st.write(usuario_completo.get("telefono", "No registrado"))
        
        st.info("🔧 Próximamente: editar perfil y cambiar contraseña")
    
    # ========== PESTAÑA NOTAS ==========
    with tab_notas:
        st.subheader("📖 Mis Calificaciones")
        
        # Obtener grado del estudiante
        url_grado = f"{SUPABASE_URL}/rest/v1/estudiantes_grados?id_estudiante=eq.{data['id_persona']}"
        response_grado = requests.get(url_grado, headers=headers)
        
        if response_grado.status_code == 200 and response_grado.json():
            grado_id = response_grado.json()[0]["id_grado"]
            url_nom_grado = f"{SUPABASE_URL}/rest/v1/grados?id_grado=eq.{grado_id}"
            response_nom_grado = requests.get(url_nom_grado, headers=headers)
            if response_nom_grado.status_code == 200 and response_nom_grado.json():
                st.success(f"📖 Grado: {response_nom_grado.json()[0]['nombre']}")
        
        # Notas de ejemplo (luego se conectarán a Supabase)
        st.write("**Matemáticas:** 4.5")
        st.write("**Ciencias:** 3.8")
        st.write("**Español:** 4.2")
        st.write("**Promedio:** 4.2")
        
        st.subheader("📋 Tareas Pendientes")
        st.write("• Matemáticas: Taller de fracciones - Entrega: 15/05/2026")
        
        st.subheader("💬 Comunicaciones")
        st.write("💬 Papá: 'Recuerda estudiar para el examen'")
