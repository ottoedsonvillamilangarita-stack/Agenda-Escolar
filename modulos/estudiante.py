# modulos/estudiante.py
import streamlit as st
import requests
from .utils import SUPABASE_URL, get_headers

def mostrar(data):
    st.title("🎓 Panel del Estudiante")
    
    # data contiene: username, password_hash, rol, documento
    documento_estudiante = data.get('documento')
    
    st.write(f"Bienvenido, Estudiante")
    st.write(f"Documento: {documento_estudiante}")
    
    # Buscar información del estudiante por documento
    headers = get_headers()
    url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{documento_estudiante}"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200 and response.json():
        estudiante_data = response.json()[0]
        st.write(f"Nombre: {estudiante_data.get('nombre_estudiante', 'N/A')}")
        st.write(f"Curso: {estudiante_data.get('curso', 'N/A')}")
    else:
        st.warning("No se pudo cargar la información del estudiante")
    
    st.subheader("📖 Mis Notas")
    st.write("**Matemáticas:** 4.5")
    st.write("**Ciencias:** 3.8")
    st.write("**Español:** 4.2")
