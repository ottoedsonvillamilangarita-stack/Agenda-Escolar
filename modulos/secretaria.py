import streamlit as st
import requests
import pandas as pd
from utils import SUPABASE_URL, get_headers
from modulos.features.horarios import mostrar_horario_semanal_detallado

def mostrar(data):
    st.title("📋 Panel de Secretaria")
    st.write(f"Bienvenida, {data.get('username', 'Secretaria')}")
    
    headers = get_headers()
    
    st.divider()
    st.subheader("📌 Funciones disponibles")
    
    opcion = st.selectbox(
        "Seleccionar función",
        [
            "📊 Dashboard",
            "👨‍🎓 Gestión de Estudiantes",
            "👨‍🏫 Gestión de Docentes",
            "📚 Gestión de Cursos",
            "📅 Consultar Horarios",
            "📄 Certificados",
            "📊 Reportes"
        ]
    )
    
    st.divider()
    
    if opcion == "📊 Dashboard":
        mostrar_dashboard()
    elif opcion == "👨‍🎓 Gestión de Estudiantes":
        gestion_estudiantes()
    elif opcion == "👨‍🏫 Gestión de Docentes":
        gestion_docentes()
    elif opcion == "📚 Gestión de Cursos":
        gestion_cursos()
    elif opcion == "📅 Consultar Horarios":
        consultar_horarios()
    elif opcion == "📄 Certificados":
        st.info("🚧 Módulo en desarrollo")
    elif opcion == "📊 Reportes":
        st.info("🚧 Módulo en desarrollo")


def mostrar_dashboard():
    st.subheader("📊 Dashboard Secretaria")
    
    headers = get_headers()
    
    response_est = requests.get(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers)
    total_estudiantes = len(response_est.json()) if response_est.status_code == 200 else 0
    
    response_doc = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
    total_docentes = len(response_doc.json()) if response_doc.status_code == 200 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("👨‍🎓 Total Estudiantes", total_estudiantes)
    col2.metric("👨‍🏫 Total Docentes", total_docentes)
    col3.metric("📚 Cursos Activos", "7")
    
    st.info("📌 Panel de gestión administrativa")


def gestion_estudiantes():
    st.subheader("👨‍🎓 Gestión de Estudiantes")
    
    headers = get_headers()
    response = requests.get(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers)
    
    if response.status_code == 200:
        estudiantes = response.json()
        if estudiantes:
            df = pd.DataFrame(estudiantes)
            st.dataframe(df, use_container_width=True)
            st.caption(f"Total: {len(estudiantes)} estudiantes")
        else:
            st.info("No hay estudiantes registrados")


def gestion_docentes():
    st.subheader("👨‍🏫 Gestión de Docentes")
    
    headers = get_headers()
    response = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
    
    if response.status_code == 200:
        docentes = response.json()
        if docentes:
            df = pd.DataFrame(docentes)
            st.dataframe(df, use_container_width=True)
            st.caption(f"Total: {len(docentes)} docentes")
        else:
            st.info("No hay docentes registrados")


def gestion_cursos():
    st.subheader("📚 Gestión de Cursos")
    
    cursos = ["901", "902", "903", "1001", "1002", "1003", "1101"]
    
    for curso in cursos:
        with st.expander(f"Curso {curso}"):
            st.write(f"**Asignaturas del curso {curso}:**")
            headers = get_headers()
            url = f"{SUPABASE_URL}/rest/v1/docentes?curso=eq.{curso}&select=asignatura,nombre_docente"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                materias = response.json()
                if materias:
                    for m in materias:
                        st.write(f"- {m.get('asignatura')}: {m.get('nombre_docente')}")
                else:
                    st.write("Sin asignaturas asignadas")


def consultar_horarios():
    st.subheader("📅 Consultar Horarios")
    
    headers = get_headers()
    
    tipo = st.radio("Ver horario de:", ["Curso", "Docente"])
    
    if tipo == "Curso":
        cursos = ["901", "902", "903", "1001", "1002", "1003", "1101"]
        curso = st.selectbox("Seleccionar curso", cursos)
        
        if st.button("Ver horario", type="primary"):
            mostrar_horario_semanal_detallado(curso, headers)
    
    else:  # Docente
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
