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

def mostrar_horario_estudiante(documento_estudiante, headers):
    """Muestra el horario del estudiante usando la función unificada"""
    
    # Obtener el curso del estudiante
    url_est = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{documento_estudiante}"
    response_est = requests.get(url_est, headers=headers)
    
    if response_est.status_code != 200 or not response_est.json():
        st.info("No se encontró el estudiante")
        return
    
    estudiante = response_est.json()[0]
    curso = estudiante.get('curso')
    nombre = estudiante.get('nombre_estudiante')
    
    if not curso:
        st.info("El estudiante no tiene curso asignado")
        return
    
    # Obtener horarios del curso
    url_horario = f"{SUPABASE_URL}/rest/v1/horario_base?curso=eq.{curso}&order=dia_semana.asc,orden_clase.asc"
    response_horario = requests.get(url_horario, headers=headers)
    
    if response_horario.status_code != 200:
        st.info("No hay horario configurado para este curso")
        return
    
    horarios = response_horario.json()
    
    if not horarios:
        st.info("No hay horario configurado para este curso")
        return
    
    # Usar la función unificada con tipo "estudiante"
    mostrar_horario_unificado(horarios, f"📅 Horario de {nombre} ({curso})", "estudiante")cado(horarios, f"📅 Horario de {curso}")
