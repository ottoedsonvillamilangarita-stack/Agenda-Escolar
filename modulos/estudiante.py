import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from utils import SUPABASE_URL, get_headers
from modulos.features.calificaciones import mostrar_notas_estudiante
from modulos.features.asistencia import mostrar_asistencia_estudiante
from modulos.features.horarios import mostrar_horario_tabla

def mostrar(data):
    st.title("🎓 Panel del Estudiante")

    documento_estudiante = data.get('documento')
    st.write(f"Bienvenido, Estudiante")

    headers = get_headers()

    # Obtener información del estudiante
    url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{documento_estudiante}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200 and response.json():
        estudiante = response.json()[0]
        curso = estudiante.get('curso')
        nombre = estudiante.get('nombre_estudiante')
        st.success(f"✅ Bienvenido, {nombre}")
        st.info(f"📚 Curso: {curso}")

        # Horario semanal
        st.subheader("📅 Mi Horario Semanal")
        mostrar_horario_tabla(curso, headers)

    st.divider()
    st.subheader("📌 Otras funciones")

    opcion = st.selectbox(
        "Seleccionar función",
        [
            "📖 Mis Notas",
            "📋 Mi Asistencia",
            "👤 Mi Perfil"
        ]
    )

    st.divider()

    if opcion == "📖 Mis Notas":
        mostrar_notas_estudiante(data)
    elif opcion == "📋 Mi Asistencia":
        mostrar_asistencia_estudiante(data)
    elif opcion == "👤 Mi Perfil":
        st.info("🚧 Módulo en desarrollo")
