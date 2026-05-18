# modulos/docente.py
import streamlit as st
import requests
from utils import SUPABASE_URL, get_headers

def mostrar(data):
    st.title("👨‍🏫 Panel del Docente")
    
    documento_docente = data.get('documento')
    
    # Verificar datos del docente
    headers = get_headers()
    url = f"{SUPABASE_URL}/rest/v1/docentes?documento_docente=eq.{documento_docente}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200 and response.json():
        docente = response.json()[0]
        st.success(f"Bienvenido, {docente.get('nombre_docente', 'Docente')}")
    
    # ============================================
    # MENÚ DE FUNCIONES (misma estrategia de botones)
    # ============================================
    
    # Inicializar función actual
    if "funcion_actual" not in st.session_state:
        st.session_state.funcion_actual = "mis_cursos"
    
    # Mostrar botones de funciones
    st.subheader("📌 Funciones disponibles")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📚 Mis Cursos", use_container_width=True, 
                     type="primary" if st.session_state.funcion_actual == "mis_cursos" else "secondary"):
            st.session_state.funcion_actual = "mis_cursos"
            st.rerun()
    
    with col2:
        if st.button("📝 Calificaciones", use_container_width=True,
                     type="primary" if st.session_state.funcion_actual == "calificaciones" else "secondary"):
            st.session_state.funcion_actual = "calificaciones"
            st.rerun()
    
    with col3:
        if st.button("📋 Asistencia", use_container_width=True,
                     type="primary" if st.session_state.funcion_actual == "asistencia" else "secondary"):
            st.session_state.funcion_actual = "asistencia"
            st.rerun()
    
    with col4:
        if st.button("📊 Reportes", use_container_width=True,
                     type="primary" if st.session_state.funcion_actual == "reportes" else "secondary"):
            st.session_state.funcion_actual = "reportes"
            st.rerun()
    
    st.divider()
    
    # ============================================
    # MOSTRAR FUNCIÓN SELECCIONADA
    # ============================================
    
    if st.session_state.funcion_actual == "mis_cursos":
        mostrar_mis_cursos(data)
    elif st.session_state.funcion_actual == "calificaciones":
        mostrar_calificaciones(data)
    elif st.session_state.funcion_actual == "asistencia":
        mostrar_asistencia(data)
    elif st.session_state.funcion_actual == "reportes":
        mostrar_reportes(data)

def mostrar_mis_cursos(data):
    st.subheader("📚 Mis Cursos")
    
    documento_docente = data.get('documento')
    headers = get_headers()
    url = f"{SUPABASE_URL}/rest/v1/docentes?documento_docente=eq.{documento_docente}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        cursos = response.json()
        if cursos:
            for curso in cursos:
                st.write(f"**Curso {curso.get('curso')}** - {curso.get('asignatura')}")
        else:
            st.info("No hay cursos asignados")

def mostrar_calificaciones(data):
    st.subheader("📝 Calificaciones")
    st.info("Módulo en desarrollo - Próximamente")
    st.write("Aquí podrás ingresar y editar notas de los estudiantes")

def mostrar_asistencia(data):
    st.subheader("📋 Asistencia")
    st.info("Módulo en desarrollo - Próximamente")
    st.write("Aquí podrás marcar asistencia diaria")

def mostrar_reportes(data):
    st.subheader("📊 Reportes")
    st.info("Módulo en desarrollo - Próximamente")
    st.write("Aquí podrás generar reportes de notas y asistencia")
