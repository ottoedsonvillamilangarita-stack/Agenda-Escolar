import streamlit as st
import requests
from utils import SUPABASE_URL, get_headers

def mostrar(data):
    st.title("👨‍🏫 Panel del Docente")
    
    # data contiene: username, password_hash, rol, documento
    documento_docente = data.get('documento')
    
    st.write(f"Bienvenido, Docente")
    st.write(f"Documento: {documento_docente}")
    
    headers = get_headers()
    
    # Buscar en la tabla docentes por documento_docente
    url = f"{SUPABASE_URL}/rest/v1/docentes?documento_docente=eq.{documento_docente}"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        datos = response.json()
        if datos:
            docente = datos[0]
            st.success(f"✅ Docente encontrado: {docente.get('nombre_docente', 'N/A')}")
            st.write(f"**Nombre:** {docente.get('nombre_docente', 'N/A')}")
            st.write(f"**Apellidos:** {docente.get('apellidos_docente', 'N/A')}")
            st.write(f"**Email:** {docente.get('email_docente', 'N/A')}")
        else:
            st.warning("No se encontró el docente en la tabla 'docentes'")
    else:
        st.error(f"Error {response.status_code}: {response.text}")
        st.write("Detalles del error:", response.text)
    
    st.subheader("📚 Mis Cursos")
    st.write("**Matemáticas - 901**")
    st.write("**Español - 902**")
    st.write("**Ciencias - 903**")
