import streamlit as st
import requests
import pandas as pd
from utils import SUPABASE_URL, get_headers
from modulos.features.calificaciones import mostrar_notas_estudiante
from modulos.features.asistencia import mostrar_asistencia_estudiante
from modulos.features.horarios import mostrar_horario_unificado


def mostrar(data):
    st.title("👨‍🎓 Panel del Estudiante")
    
    documento_estudiante = data.get('documento')
    st.write(f"Bienvenido, {data.get('username', 'Estudiante')}")
    
    headers = get_headers()
    
    # Obtener datos del estudiante
    url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{documento_estudiante}"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200 or not response.json():
        st.error("No se encontró el estudiante")
        return
    
    estudiante = response.json()[0]
    nombre = estudiante.get('nombre_estudiante')
    curso = estudiante.get('curso')
    
    st.success(f"📌 Estudiante: {nombre} - Curso: {curso}")
    
    # =============================================
    # HORARIO DEL ESTUDIANTE
    # =============================================
    if curso:
        url_horario = f"{SUPABASE_URL}/rest/v1/horario_base?curso=eq.{curso}&order=dia_semana.asc,orden_clase.asc"
        response_horario = requests.get(url_horario, headers=headers)
        
        if response_horario.status_code == 200:
            horarios = response_horario.json()
            if horarios:
                mostrar_horario_unificado(horarios, f"📅 Mi Horario ({curso})", "estudiante")
            else:
                st.info("No hay horario configurado para tu curso")
        else:
            st.info("No se pudo cargar el horario")
    
    st.divider()
    st.subheader("📌 Funciones disponibles")
    
    opcion = st.selectbox(
        "Seleccionar función",
        [
            "📖 Mis Notas",
            "📋 Mi Asistencia",
            "📊 Mi Rendimiento"
        ]
    )
    
    st.divider()
    
    if opcion == "📖 Mis Notas":
        mostrar_notas_estudiante(data)
    elif opcion == "📋 Mi Asistencia":
        mostrar_asistencia_estudiante(data)
    else:
        st.info("🚧 Módulo en desarrollo")
