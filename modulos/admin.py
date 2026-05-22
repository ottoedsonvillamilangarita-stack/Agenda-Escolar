import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from utils import SUPABASE_URL, get_headers
from modulos.features.horarios import gestion_horarios_admin

def mostrar(data):
    st.title("🛡️ Panel de Administrador")
    st.write(f"Bienvenido, {data.get('username', 'Admin')}")
    
    if "admin_seccion" not in st.session_state:
        st.session_state.admin_seccion = "dashboard"
    
    # Menú simplificado
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        if st.button("📊 Dashboard", use_container_width=True,
                     type="primary" if st.session_state.admin_seccion == "dashboard" else "secondary"):
            st.session_state.admin_seccion = "dashboard"
            st.rerun()
    
    with col2:
        if st.button("👨‍🎓 Alumnos", use_container_width=True,
                     type="primary" if st.session_state.admin_seccion == "alumnos" else "secondary"):
            st.session_state.admin_seccion = "alumnos"
            st.rerun()
    
    with col3:
        if st.button("👨‍👩‍👧 Acudientes", use_container_width=True,
                     type="primary" if st.session_state.admin_seccion == "acudientes" else "secondary"):
            st.session_state.admin_seccion = "acudientes"
            st.rerun()
    
    with col4:
        if st.button("👨‍🏫 Docentes", use_container_width=True,
                     type="primary" if st.session_state.admin_seccion == "docentes" else "secondary"):
            st.session_state.admin_seccion = "docentes"
            st.rerun()
    
    with col5:
        if st.button("📚 Asignación", use_container_width=True,
                     type="primary" if st.session_state.admin_seccion == "asignacion" else "secondary"):
            st.session_state.admin_seccion = "asignacion"
            st.rerun()
    
    with col6:
        if st.button("📅 Horarios", use_container_width=True,
                     type="primary" if st.session_state.admin_seccion == "horarios" else "secondary"):
            st.session_state.admin_seccion = "horarios"
            st.rerun()
    
    st.divider()
    
    if st.session_state.admin_seccion == "dashboard":
        mostrar_dashboard()
    elif st.session_state.admin_seccion == "alumnos":
        mostrar_alumnos()
    elif st.session_state.admin_seccion == "acudientes":
        mostrar_acudientes()
    elif st.session_state.admin_seccion == "docentes":
        mostrar_docentes()
    elif st.session_state.admin_seccion == "asignacion":
        mostrar_asignacion()
    elif st.session_state.admin_seccion == "sistema":
        mostrar_sistema()
    elif st.session_state.admin_seccion == "horarios":
        gestion_horarios_admin(data)


def mostrar_dashboard():
    st.subheader("📊 Dashboard General")
    
    headers = get_headers()
    
    try:
        response = requests.get(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers)
        total_alumnos = len(response.json()) if response.status_code == 200 else 0
        st.metric("👨‍🎓 Total Alumnos", total_alumnos)
    except:
        st.error("Error al cargar datos")
    
    st.info("🔐 Panel de control del Administrador")


def mostrar_alumnos():
    st.subheader("👨‍🎓 Gestión de Alumnos")
    
    headers = get_headers()
    
    tab1, tab2 = st.tabs(["📋 Lista de Alumnos", "➕ Nuevo Alumno"])
    
    with tab1:
        try:
            response = requests.get(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers)
            if response.status_code == 200:
                alumnos = response.json()
                if alumnos:
                    df = pd.DataFrame(alumnos)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No hay alumnos registrados")
        except:
            st.error("Error al cargar alumnos")
    
    with tab2:
        with st.form("nuevo_alumno"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre *")
                apellidos = st.text_input("Apellidos *")
                documento = st.text_input("Documento *")
                curso = st.selectbox("Curso *", ["901", "902", "903", "1001", "1002", "1003", "1101"])
            with col2:
                nombre_acudiente = st.text_input("Nombre del acudiente *")
                documento_acudiente = st.text_input("Documento del acudiente *")
                telefono = st.text_input("Teléfono del acudiente")
            
            if st.form_submit_button("💾 Guardar Alumno", type="primary"):
                if not all([nombre, apellidos, documento, curso, nombre_acudiente, documento_acudiente]):
                    st.error("❌ Completa todos los campos obligatorios")
                else:
                    data = {
                        "nombre_estudiante": nombre,
                        "apellidos_estudiante": apellidos,
                        "documento_estudiante": documento,
                        "curso": curso,
                        "nombre_acudiente": nombre_acudiente,
                        "documento_acudiente": documento_acudiente,
                        "telefono_acudiente": telefono
                    }
                    response = requests.post(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers, json=data)
                    if response.status_code == 201:
                        st.success(f"✅ Alumno {nombre} registrado")
                    else:
                        st.error("Error al registrar")


def mostrar_acudientes():
    st.subheader("👨‍👩‍👧 Gestión de Acudientes")
    
    headers = get_headers()
    response = requests.get(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers)
    
    if response.status_code == 200:
        alumnos = response.json()
        acudientes_dict = {}
        
        for alumno in alumnos:
            doc_acud = alumno.get('documento_acudiente')
            if doc_acud and doc_acud not in acudientes_dict:
                acudientes_dict[doc_acud] = {
                    "nombre": alumno.get('nombre_acudiente'),
                    "documento": doc_acud,
                    "telefono": alumno.get('telefono_acudiente'),
                    "hijos": []
                }
            if doc_acud:
                acudientes_dict[doc_acud]["hijos"].append(alumno.get('nombre_estudiante'))
        
        if acudientes_dict:
            df = pd.DataFrame([{
                "Nombre": v["nombre"],
                "Documento": v["documento"],
                "Teléfono": v["telefono"],
                "Hijos": ", ".join(v["hijos"])
            } for v in acudientes_dict.values()])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hay acudientes registrados")


def mostrar_docentes():
    st.subheader("👨‍🏫 Gestión de Docentes")
    
    headers = get_headers()
    
    tab1, tab2 = st.tabs(["📋 Lista de Docentes", "➕ Nuevo Docente"])
    
    with tab1:
        try:
            response = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
            if response.status_code == 200:
                docentes = response.json()
                if docentes:
                    df = pd.DataFrame(docentes)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No hay docentes registrados")
        except:
            st.error("Error al cargar docentes")
    
    with tab2:
        with st.form("nuevo_docente"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre *")
                apellidos = st.text_input("Apellidos *")
                documento = st.text_input("Documento *")
            with col2:
                telefono = st.text_input("Teléfono")
                email = st.text_input("Email")
            
            if st.form_submit_button("💾 Guardar Docente", type="primary"):
                if not all([nombre, apellidos, documento]):
                    st.error("❌ Completa todos los campos obligatorios")
                else:
                    data = {
                        "nombre_docente": nombre,
                        "apellidos_docente": apellidos,
                        "documento_docente": documento,
                        "telefono_docente": telefono,
                        "email_docente": email
                    }
                    response = requests.post(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers, json=data)
                    if response.status_code == 201:
                        st.success(f"✅ Docente {nombre} registrado")
                    else:
                        st.error("Error al registrar")


def mostrar_asignacion():
    st.subheader("📚 Asignación Académica")
    st.info("🚧 Módulo en construcción - Usa la sección de Horarios para configurar")


def mostrar_sistema():
    st.subheader("⚙️ Configuración del Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        nombre_colegio = st.text_input("Nombre del colegio", "Mi Colegio")
        año_lectivo = st.number_input("Año lectivo", min_value=2000, max_value=2100, value=2024)
        
        if st.button("💾 Guardar Configuración", type="primary"):
            st.success("Configuración guardada")
    
    with col2:
        if st.button("📀 Crear Respaldo", type="primary"):
            st.success("Respaldo creado")
