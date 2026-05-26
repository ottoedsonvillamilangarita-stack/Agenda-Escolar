import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from utils import SUPABASE_URL, get_headers
from modulos.features.asistencia import mostrar_reporte_asistencia

def mostrar_reportes_docente(data):
    st.subheader("📊 Reportes")
    
    documento_docente = data.get('documento')
    headers = get_headers()
    
    # Obtener cursos del docente
    url = f"{SUPABASE_URL}/rest/v1/asignacion_academica?documento_docente=eq.{documento_docente}&asignatura=neq.Dirección de Curso"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        st.error("Error al cargar cursos")
        return
    
    asignaciones = response.json()
    cursos_unicos = list(set([a.get('curso') for a in asignaciones if a.get('curso')]))
    
    if not cursos_unicos:
        st.warning("No tienes cursos asignados")
        return
    
    # Selector de tipo de reporte
    tipo_reporte = st.selectbox(
        "Tipo de reporte",
        ["📋 Ausencias por estudiante", "📊 Resumen de ausencias por curso", "📈 Evolución de asistencia"]
    )
    
    if tipo_reporte == "📋 Ausencias por estudiante":
        mostrar_ausencias_por_estudiante(cursos_unicos, documento_docente)
    
    elif tipo_reporte == "📊 Resumen de ausencias por curso":
        mostrar_resumen_ausencias(cursos_unicos, documento_docente)
    
    elif tipo_reporte == "📈 Evolución de asistencia":
        mostrar_evolucion_asistencia(cursos_unicos, documento_docente)


def mostrar_ausencias_por_estudiante(cursos_unicos, documento_docente):
    """Reporte de ausencias por estudiante (usando función unificada)"""
    
    curso = st.selectbox("Seleccionar curso", cursos_unicos, key="reporte_ausencias_curso")
    
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Desde", datetime.now().replace(day=1), key="reporte_fecha_ini")
    with col2:
        fecha_fin = st.date_input("Hasta", datetime.now(), key="reporte_fecha_fin")
    
    if st.button("📊 Generar reporte", type="primary", use_container_width=True):
        headers = get_headers()
        mostrar_reporte_asistencia(curso, fecha_inicio, fecha_fin, headers, f"Reporte de Asistencia - Curso {curso}")


def mostrar_resumen_ausencias(cursos_unicos, documento_docente):
    """Resumen de ausencias por curso"""
    st.info("🚧 Módulo en desarrollo - Próximamente")
    st.write("Este reporte mostrará un resumen comparativo entre cursos")


def mostrar_evolucion_asistencia(cursos_unicos, documento_docente):
    """Evolución de asistencia en el tiempo"""
    st.info("🚧 Módulo en desarrollo - Próximamente")
    st.write("Este reporte mostrará gráficas de evolución de asistencia")
