import streamlit as st
import requests
import pandas as pd
from utils import SUPABASE_URL, get_headers

def mostrar(data):
    st.title("🔍 Panel de Supervisor")
    st.write(f"Bienvenido, {data.get('username', 'Supervisor')}")
    
    opcion = st.sidebar.selectbox(
        "Seleccionar función",
        ["📊 Dashboard", "📈 Rendimiento Académico", "👨‍🏫 Evaluación Docente", "📊 Estadísticas", "📋 Reportes"]
    )
    
    if opcion == "📊 Dashboard":
        mostrar_dashboard()
    elif opcion == "📈 Rendimiento Académico":
        rendimiento_academico()
    elif opcion == "👨‍🏫 Evaluación Docente":
        evaluacion_docente()
    elif opcion == "📊 Estadísticas":
        estadisticas()
    elif opcion == "📋 Reportes":
        reportes()

def mostrar_dashboard():
    st.subheader("📊 Dashboard Supervisor")
    
    headers = get_headers()
    
    url_est = f"{SUPABASE_URL}/rest/v1/estudiantes"
    response_est = requests.get(url_est, headers=headers)
    total_estudiantes = len(response_est.json()) if response_est.status_code == 200 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("👨‍🎓 Estudiantes", total_estudiantes)
    col2.metric("📚 Cursos", "7")
    col3.metric("👨‍🏫 Docentes", "Por definir")
    
    st.info("📊 Supervisión académica - Vista general del sistema")

def rendimiento_academico():
    st.subheader("📈 Rendimiento Académico por Curso")
    
    curso = st.selectbox("Seleccionar curso", ["901", "902", "903", "1001", "1002", "1003", "1101"])
    
    st.write(f"**Rendimiento del curso {curso}:**")
    st.write("- Promedio general: 4.2 (próximamente)")
    st.write("- Materias con mejor rendimiento: (próximamente)")
    st.write("- Materias con menor rendimiento: (próximamente)")

def evaluacion_docente():
    st.subheader("👨‍🏫 Evaluación Docente")
    
    headers = get_headers()
    url = f"{SUPABASE_URL}/rest/v1/docentes?select=nombre_docente,asignatura,curso"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        docentes = response.json()
        if docentes:
            df = pd.DataFrame(docentes)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hay docentes registrados")
    else:
        st.error(f"Error {response.status_code}")

def estadisticas():
    st.subheader("📊 Estadísticas Avanzadas")
    st.write("Próximamente: Estadísticas detalladas por curso y materia")

def reportes():
    st.subheader("📋 Reportes de Supervisión")
    st.write("**Reportes disponibles:**")
    st.write("- Reporte de rendimiento por curso (próximamente)")
    st.write("- Reporte de evaluación docente (próximamente)")
