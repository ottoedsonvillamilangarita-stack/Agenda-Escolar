import streamlit as st
import requests
from utils import SUPABASE_URL, get_headers
from modulos.features.calificaciones import mostrar_notas_estudiante

def mostrar(data):
    st.title("🎓 Panel del Estudiante")
    
    documento_estudiante = data.get('documento')
    st.write(f"Bienvenido, Estudiante")
    st.write(f"Documento: {documento_estudiante}")
    
    headers = get_headers()
    
    # Consultar la tabla estudiantes
    url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{documento_estudiante}"
    
    # Para depuración (lo puedes quitar después)
    st.write(f"🔍 URL: {url}")
    
    response = requests.get(url, headers=headers)
    
    st.write(f"📡 Status: {response.status_code}")
    
    if response.status_code == 200:
        datos = response.json()
        st.write(f"📦 Datos recibidos: {datos}")
        
        if datos:
            estudiante = datos[0]
            st.success(f"✅ Estudiante encontrado: {estudiante.get('nombre_estudiante', 'N/A')}")
            st.write(f"**Nombre:** {estudiante.get('nombre_estudiante', 'N/A')}")
            st.write(f"**Apellidos:** {estudiante.get('apellidos_estudiante', 'N/A')}")
            st.write(f"**Curso:** {estudiante.get('curso', 'N/A')}")
        else:
            st.warning("No se encontró el estudiante en la tabla 'estudiantes'")
    else:
        st.error(f"Error {response.status_code}: {response.text}")
    
    st.subheader("📖 Mis Notas")
    st.write("**Matemáticas:** 4.5")
    st.write("**Ciencias:** 3.8")
    st.write("**Español:** 4.2")
