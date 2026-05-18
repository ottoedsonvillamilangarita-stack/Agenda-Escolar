import streamlit as st
import requests
import pandas as pd
from utils import SUPABASE_URL, get_headers

def mostrar(data):
    st.title("📋 Panel de Secretaria")
    st.write(f"Bienvenida, {data.get('username', 'Secretaria')}")
    
    opcion = st.sidebar.selectbox(
        "Seleccionar función",
        ["📊 Dashboard", "👨‍🎓 Gestión de Estudiantes", "👨‍🏫 Gestión de Docentes", "📚 Gestión de Cursos", "📈 Reportes"]
    )
    
    if opcion == "📊 Dashboard":
        mostrar_dashboard()
    elif opcion == "👨‍🎓 Gestión de Estudiantes":
        gestion_estudiantes()
    elif opcion == "👨‍🏫 Gestión de Docentes":
        gestion_docentes()
    elif opcion == "📚 Gestión de Cursos":
        gestion_cursos()
    elif opcion == "📈 Reportes":
        mostrar_reportes()

def mostrar_dashboard():
    st.subheader("📊 Dashboard Secretaria")
    
    headers = get_headers()
    
    url_est = f"{SUPABASE_URL}/rest/v1/estudiantes"
    response_est = requests.get(url_est, headers=headers)
    total_estudiantes = len(response_est.json()) if response_est.status_code == 200 else 0
    
    url_doc = f"{SUPABASE_URL}/rest/v1/docentes"
    response_doc = requests.get(url_doc, headers=headers)
    if response_doc.status_code == 200:
        datos = response_doc.json()
        docentes_unicos = set([d.get('documento_docente') for d in datos])
        total_docentes = len(docentes_unicos)
    else:
        total_docentes = 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("👨‍🎓 Total Estudiantes", total_estudiantes)
    col2.metric("👨‍🏫 Total Docentes", total_docentes)
    col3.metric("📚 Cursos Activos", "7")
    
    st.info("📌 Módulo de secretaría - Gestión administrativa")

def gestion_estudiantes():
    st.subheader("👨‍🎓 Gestión de Estudiantes")
    
    tab1, tab2 = st.tabs(["📋 Lista de Estudiantes", "🔍 Buscar Estudiante"])
    
    with tab1:
        headers = get_headers()
        url = f"{SUPABASE_URL}/rest/v1/estudiantes?select=nombre_estudiante,apellidos_estudiante,documento_estudiante,curso"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            datos = response.json()
            if datos:
                df = pd.DataFrame(datos)
                st.dataframe(df, use_container_width=True)
                st.caption(f"Total: {len(datos)} estudiantes")
            else:
                st.info("No hay estudiantes registrados")
        else:
            st.error(f"Error {response.status_code}")
    
    with tab2:
        buscar = st.text_input("Buscar por documento o nombre")
        if buscar:
            headers = get_headers()
            url = f"{SUPABASE_URL}/rest/v1/estudiantes?or=(documento_estudiante.eq.{buscar},nombre_estudiante.ilike.%25{buscar}%25)"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                datos = response.json()
                if datos:
                    st.json(datos[0])
                else:
                    st.warning("No encontrado")

def gestion_docentes():
    st.subheader("👨‍🏫 Gestión de Docentes")
    
    headers = get_headers()
    url = f"{SUPABASE_URL}/rest/v1/docentes?select=nombre_docente,apellidos_docente,documento_docente,curso,asignatura"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        datos = response.json()
        if datos:
            df = pd.DataFrame(datos)
            st.dataframe(df, use_container_width=True)
            st.caption(f"Total asignaciones: {len(datos)}")
        else:
            st.info("No hay docentes registrados")
    else:
        st.error(f"Error {response.status_code}")

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
                        # Línea corregida:
                        st.write(f"- {m.get('asignatura')}: {m.get('nombre_docente')}")
                else:
                    st.write("Sin asignaturas asignadas")

def mostrar_reportes():
    st.subheader("📈 Reportes")
    st.write("**Reportes disponibles:**")
    st.write("- Listado de estudiantes por curso")
    st.write("- Listado de docentes por asignatura")
    st.write("- Horarios de clase (próximamente)")
