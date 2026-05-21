import streamlit as st
import requests
from utils import SUPABASE_URL, get_headers
from modulos.features.calificaciones import mostrar_notas_estudiante
from modulos.features.asistencia import mostrar_asistencia_estudiante


def mostrar(data):
    st.title("🎓 Panel del Estudiante")
    
    documento_estudiante = data.get('documento')
    st.write(f"Bienvenido, Estudiante")
    st.write(f"Documento: {documento_estudiante}")
    
    headers = get_headers()
    
    # Consultar la tabla estudiantes
    url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{documento_estudiante}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        datos = response.json()
        
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
    
    st.divider()
    st.subheader("📌 Funciones disponibles")
    
    opcion = st.selectbox(
        "Seleccionar función",
        [
            "📖 Mis Notas",
            "📅 Mi Horario",
            "📋 Asistencia",
            "👤 Mi Perfil"
        ]
    )
    
    st.divider()
    
    if opcion == "📖 Mis Notas":
        mostrar_notas_estudiante(data)
    elif opcion == "📅 Mi Horario":
        st.info("🚧 Módulo en desarrollo")
      elif opcion == "📋 Asistencia":
        mostrar_asistencia_estudiante(data)
    elif opcion == "👤 Mi Perfil":
        st.info("🚧 Módulo en desarrollo")
