import streamlit as st
import requests
import pandas as pd
from utils import SUPABASE_URL, get_headers
from modulos.features.horarios import mostrar_horario_semanal_detallado
from modulos.features.horarios import mostrar_horario_curso_tabla

def mostrar(data):
    st.title("🔍 Panel de Supervisor")
    st.write(f"Bienvenido, {data.get('username', 'Supervisor')}")
    
    headers = get_headers()
    
    st.divider()
    st.subheader("📌 Funciones disponibles")
    
    opcion = st.selectbox(
        "Seleccionar función",
        [
            "📊 Dashboard",
            "📈 Rendimiento Académico",
            "👨‍🏫 Evaluación Docente",
            "📅 Consultar Horarios",
            "📊 Estadísticas",
            "📋 Reportes"
        ]
    )
    
    st.divider()
    
    if opcion == "📊 Dashboard":
        mostrar_dashboard()
    elif opcion == "📈 Rendimiento Académico":
        rendimiento_academico()
    elif opcion == "👨‍🏫 Evaluación Docente":
        evaluacion_docente()
    elif opcion == "📅 Consultar Horarios":
        consultar_horarios()
    elif opcion == "📊 Estadísticas":
        st.info("🚧 Módulo en desarrollo")
    elif opcion == "📋 Reportes":
        st.info("🚧 Módulo en desarrollo")


def mostrar_dashboard():
    st.subheader("📊 Dashboard Supervisor")
    
    headers = get_headers()
    
    response_est = requests.get(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers)
    total_estudiantes = len(response_est.json()) if response_est.status_code == 200 else 0
    
    col1, col2 = st.columns(2)
    col1.metric("👨‍🎓 Estudiantes", total_estudiantes)
    col2.metric("📚 Cursos", "7")
    
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


def consultar_horarios():
    st.subheader("📅 Consultar Horarios")
    
    headers = get_headers()
    
    tipo = st.radio("Ver horario de:", ["Curso", "Docente"])
    
    if tipo == "Curso":
        cursos = ["901", "902", "903", "1001", "1002", "1003", "1101"]
        curso = st.selectbox("Seleccionar curso", cursos)
        
        if st.button("Ver horario", type="primary"):
            mostrar_horario_semanal_detallado(curso, headers)
            mostrar_horario_curso_tabla(curso, headers)
    
    else:
        url = f"{SUPABASE_URL}/rest/v1/docentes"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            docentes = response.json()
            docentes_opciones = [f"{d['nombre_docente']} {d['apellidos_docente']}" for d in docentes]
            docente_seleccionado = st.selectbox("Seleccionar docente", docentes_opciones)
            
            if st.button("Ver horario", type="primary"):
                idx = docentes_opciones.index(docente_seleccionado)
                documento_docente = docentes[idx]['documento_docente']
                
                url_asignacion = f"{SUPABASE_URL}/rest/v1/asignacion_academica?documento_docente=eq.{documento_docente}"
                response_asignacion = requests.get(url_asignacion, headers=headers)
                
                if response_asignacion.status_code == 200:
                    cursos_docente = list(set([a.get('curso') for a in response_asignacion.json() if a.get('curso')]))
                    
                    if cursos_docente:
                        for curso in cursos_docente:
                            st.write(f"**Curso {curso}**")
                            mostrar_horario_semanal_detallado(curso, headers)
                    else:
                        st.info("Este docente no tiene cursos asignados")
