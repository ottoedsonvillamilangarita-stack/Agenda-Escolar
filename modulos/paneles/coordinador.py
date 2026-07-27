import streamlit as st
import requests
import pandas as pd
from utils import SUPABASE_URL, get_headers
from modulos.features.horarios import mostrar_horario_unificado

def mostrar(data):
    st.title("📋 Panel de Coordinador")
    st.write(f"Bienvenido, {data.get('username', 'Coordinador')}")
    
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
            "📊 Reportes"
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
    elif opcion == "📊 Reportes":
        mostrar_reportes()


def mostrar_dashboard():
    st.subheader("📊 Dashboard Coordinador")
    
    headers = get_headers()
    
    response_est = requests.get(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers)
    total_estudiantes = len(response_est.json()) if response_est.status_code == 200 else 0
    
    response_doc = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
    total_docentes = len(response_doc.json()) if response_doc.status_code == 200 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("👨‍🎓 Estudiantes", total_estudiantes)
    col2.metric("👨‍🏫 Docentes", total_docentes)
    col3.metric("📚 Cursos", "7")
    
    st.info("📊 Supervisión académica")


def rendimiento_academico():
    st.subheader("📈 Rendimiento Académico")
    
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
    
    tipo = st.radio("Ver horario de:", ["Curso", "Docente"], key="horario_tipo_coordinador")
    
    if tipo == "Curso":
        cursos = ["901", "902", "903", "1001", "1002", "1003", "1101"]
        curso = st.selectbox("Seleccionar curso", cursos, key="horario_curso_coordinador")
        
        if st.button("Ver horario", type="primary", key="ver_horario_curso_coordinador"):
            mostrar_horario_tabla(curso, headers)
    
    else:
        url = f"{SUPABASE_URL}/rest/v1/docentes"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            docentes = response.json()
            docentes_opciones = [f"{d['nombre_docente']} {d['apellidos_docente']}" for d in docentes]
            docente_seleccionado = st.selectbox("Seleccionar docente", docentes_opciones, key="horario_docente_coordinador")
            
            if st.button("Ver horario", type="primary", key="ver_horario_docente_coordinador"):
                idx = docentes_opciones.index(docente_seleccionado)
                documento_docente = docentes[idx]['documento_docente']
                
                url_horario = f"{SUPABASE_URL}/rest/v1/horario_base?documento_docente=eq.{documento_docente}"
                response_horario = requests.get(url_horario, headers=headers)
                
                if response_horario.status_code == 200:
                    horarios = response_horario.json()
                    if horarios:
                        cursos_dict = {}
                        for h in horarios:
                            curso = h.get('curso')
                            if curso not in cursos_dict:
                                cursos_dict[curso] = []
                            cursos_dict[curso].append(h)
                        
                        for curso, clases in cursos_dict.items():
                            st.write(f"**Curso {curso}**")
                            mostrar_horario_tabla(curso, headers)
                    else:
                        st.info("Este docente no tiene horario asignado")
                else:
                    st.info("No se pudo cargar el horario del docente")


def mostrar_reportes():
    st.subheader("📊 Reportes")
    st.info("🚧 Módulo en desarrollo - Próximamente")
    st.write("Reportes disponibles:")
    st.write("- Reporte de asistencia por curso")
    st.write("- Reporte de rendimiento académico")
    st.write("- Reporte de evaluación docente")
