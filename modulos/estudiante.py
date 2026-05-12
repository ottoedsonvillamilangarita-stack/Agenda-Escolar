import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from utils import get_headers, SUPABASE_URL

def mostrar(data):
    st.title("🎓 Panel del Estudiante")
    
    headers = get_headers()
    
    # Obtener datos actualizados del estudiante
    id_persona = data.get('id_persona')
    st.write(f"🔍 Buscando estudiante con ID: {id_persona}")
    
    url = f"{SUPABASE_URL}/rest/v1/personas?id_persona=eq.{id_persona}"
    st.write(f"🔍 URL: {url}")
    
    try:
        response = requests.get(url, headers=headers)
        st.write(f"🔍 Código de respuesta: {response.status_code}")
        
        if response.status_code == 200:
            datos = response.json()
            st.write(f"🔍 Datos encontrados: {datos}")
            
            if datos and len(datos) > 0:
                estudiante = datos[0]
                st.success("✅ Datos del estudiante cargados correctamente")
            else:
                st.error(f"❌ No hay datos para id_persona = {id_persona}")
                st.info("Verifica que la tabla 'personas' tenga un registro con ese ID")
                estudiante = data
        else:
            st.error(f"❌ Error de conexión: {response.status_code}")
            estudiante = data
    except Exception as e:
        st.error(f"❌ Excepción: {e}")
        estudiante = data
    
    # Obtener username
    url_user = f"{SUPABASE_URL}/rest/v1/usuarios_login?id_persona=eq.{data['id_persona']}"
    response_user = requests.get(url_user, headers=headers)
    username = response_user.json()[0]["username"] if response_user.status_code == 200 and response_user.json() else None
    
    # Datos completos del usuario
    usuario_completo = {
        "id_persona": estudiante.get("id_persona"),
        "nombre": estudiante.get("nombre", "No registrado"),
        "email": estudiante.get("email"),
        "telefono": estudiante.get("telefono"),
        "username": username
    }
    
    # Pestañas
    tab_perfil, tab_notas = st.tabs(["👤 Mi Perfil", "📖 Mis Notas"])
    
    # Pestaña Perfil
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
    
    # Pestaña Notas
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
        
        # Notas de ejemplo
        st.write("**Matemáticas:** 4.5")
        st.write("**Ciencias:** 3.8")
        st.write("**Español:** 4.2")
        st.write("**Promedio:** 4.2")
