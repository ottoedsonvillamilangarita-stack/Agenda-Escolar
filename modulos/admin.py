import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from utils import SUPABASE_URL, get_headers

def mostrar(data):
    st.title("🛡️ Panel de Administrador")
    st.write(f"Bienvenido, {data.get('username', 'Admin')}")
    
    # Inicializar sección actual
    if "admin_seccion" not in st.session_state:
        st.session_state.admin_seccion = "dashboard"
    
    # ============================================
    # MENÚ PRINCIPAL
    # ============================================
    
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
        if st.button("⚙️ Sistema", use_container_width=True,
                     type="primary" if st.session_state.admin_seccion == "sistema" else "secondary"):
            st.session_state.admin_seccion = "sistema"
            st.rerun()
    
    st.divider()
    
    # ============================================
    # MOSTRAR SECCIÓN SELECCIONADA
    # ============================================
    
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

# ============================================
# DASHBOARD
# ============================================
def mostrar_dashboard():
    st.subheader("📊 Dashboard General")
    
    headers = get_headers()
    
    response_est = requests.get(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers)
    total_alumnos = len(response_est.json()) if response_est.status_code == 200 else 0
    
    response_doc = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
    if response_doc.status_code == 200:
        datos = response_doc.json()
        total_docentes = len(datos)
    else:
        total_docentes = 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👨‍🎓 Alumnos", total_alumnos)
    col2.metric("👨‍🏫 Docentes", total_docentes)
    col3.metric("📚 Cursos", "7")
    col4.metric("👥 Usuarios", "Por definir")
    
    st.info("🔐 Panel de control del Administrador")

# ============================================
# ALUMNOS
# ============================================
def mostrar_alumnos():
    st.subheader("👨‍🎓 Gestión de Alumnos")
    
    tab1, tab2 = st.tabs(["📋 Lista de Alumnos", "➕ Nuevo Alumno"])
    
    with tab1:
        headers = get_headers()
        response = requests.get(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers)
        
        if response.status_code == 200:
            alumnos = response.json()
            if alumnos:
                df = pd.DataFrame(alumnos)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No hay alumnos registrados")
    
    with tab2:
        st.write("**Registrar nuevo alumno**")
        
        with st.form("nuevo_alumno"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre")
                apellidos = st.text_input("Apellidos")
                documento = st.text_input("Documento")
                curso = st.selectbox("Curso", ["901", "902", "903", "1001", "1002", "1003", "1101"])
            with col2:
                nombre_acudiente = st.text_input("Nombre del acudiente")
                documento_acudiente = st.text_input("Documento del acudiente")
                telefono = st.text_input("Teléfono del acudiente")
            
            if st.form_submit_button("💾 Guardar"):
                st.success(f"✅ Alumno {nombre} registrado")

# ============================================
# ACUDIENTES
# ============================================
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

# ============================================
# DOCENTES
# ============================================
def mostrar_docentes():
    st.subheader("👨‍🏫 Gestión de Docentes")
    
    tab1, tab2 = st.tabs(["📋 Lista de Docentes", "➕ Nuevo Docente"])
    
    with tab1:
        headers = get_headers()
        response = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
        
        if response.status_code == 200:
            docentes = response.json()
            if docentes:
                df = pd.DataFrame(docentes)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No hay docentes registrados")
    
    with tab2:
        st.write("**Registrar nuevo docente**")
        
        with st.form("nuevo_docente"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre")
                apellidos = st.text_input("Apellidos")
                documento = st.text_input("Documento")
            with col2:
                telefono = st.text_input("Teléfono")
                email = st.text_input("Email")
            
            if st.form_submit_button("💾 Guardar"):
                st.success(f"✅ Docente {nombre} registrado")

# ============================================
# ASIGNACIÓN ACADÉMICA
# ============================================
def mostrar_asignacion():
    st.subheader("📚 Asignación Académica")
    
    # ============================================
    # SECCIÓN 1: DIRECTORES DE CURSO
    # ============================================
    st.markdown("### 🎓 Directores de Curso")
    st.info("Asigna un docente como director para cada curso")
    
    headers = get_headers()
    
    # Obtener docentes
    response_docentes = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
    docentes_lista = ["-- Sin asignar --"]
    docentes_dict = {}
    
    if response_docentes.status_code == 200:
        for d in response_docentes.json():
            nombre = f"{d.get('nombre_docente', '')} {d.get('apellidos_docente', '')}".strip()
            if nombre and nombre != " ":
                docentes_lista.append(nombre)
                docentes_dict[nombre] = d.get('documento_docente')
    
    if len(docentes_lista) == 1:
        st.warning("⚠️ No hay docentes registrados. Por favor, carga docentes primero.")
        return
    
    cursos = ["901", "902", "903", "1001", "1002", "1003", "1101"]
    
    # Obtener directores actuales
    response_directores = requests.get(f"{SUPABASE_URL}/rest/v1/asignacion_academica?asignatura=eq.Dirección de Curso", headers=headers)
    directores_actuales = {}
    
    if response_directores.status_code == 200:
        for d in response_directores.json():
            directores_actuales[d.get('curso')] = d.get('documento_docente')
    
    with st.form("directores_form"):
        directores_asignados = {}
        for curso in cursos:
            col1, col2 = st.columns([1, 2])
            with col1:
                st.write(f"**Curso {curso}**")
            with col2:
                current_doc = directores_actuales.get(curso)
                current_nombre = "-- Sin asignar --"
                for nombre, doc in docentes_dict.items():
                    if doc == current_doc:
                        current_nombre = nombre
                        break
                
                index = docentes_lista.index(current_nombre) if current_nombre in docentes_lista else 0
                director = st.selectbox(
                    "Director",
                    docentes_lista,
                    index=index,
                    key=f"director_{curso}",
                    label_visibility="collapsed"
                )
                directores_asignados[curso] = director if director != "-- Sin asignar --" else None
        
        if st.form_submit_button("💾 Guardar Directores de Curso", type="primary"):
            guardar_directores(directores_asignados, docentes_dict, headers, cursos)
    
    st.divider()
    
    # ============================================
    # SECCIÓN 2: ASIGNACIÓN DE MATERIAS
    # ============================================
    st.markdown("### 📖 Asignación de Materias")
    st.info("Asigna docentes a cada materia por curso")
    
    curso = st.selectbox("Seleccionar curso", cursos, key="curso_asignacion")
    
    asignaturas_por_curso = {
        "901": ["Matemáticas", "Sociales", "Español", "Inglés", "Biología", "Artes", "Educación Física", "Ética", "Administración"],
        "902": ["Matemáticas", "Sociales", "Español", "Inglés", "Biología", "Artes", "Educación Física", "Ética", "Administración"],
        "903": ["Matemáticas", "Sociales", "Español", "Inglés", "Biología", "Artes", "Educación Física", "Ética", "Administración"],
        "1001": ["Trigonometría", "Sociales", "Español", "Inglés", "Química", "Física", "Educación Física", "Artes", "Filosofía", "Ética", "Administración", "Proyecto"],
        "1002": ["Trigonometría", "Sociales", "Español", "Inglés", "Química", "Física", "Educación Física", "Artes", "Filosofía", "Ética", "Administración", "Proyecto"],
        "1003": ["Trigonometría", "Sociales", "Español", "Inglés", "Química", "Física", "Educación Física", "Artes", "Filosofía", "Ética", "Administración", "Proyecto"],
        "1101": ["Cálculo", "Sociales", "Español", "Inglés", "Química", "Física", "Educación Física", "Artes", "Filosofía", "Ética", "Administración", "Proyecto"]
    }
    
    asignaturas = asignaturas_por_curso.get(curso, [])
    
    response_asig = requests.get(f"{SUPABASE_URL}/rest/v1/asignacion_academica?curso=eq.{curso}&asignatura=neq.Dirección de Curso", headers=headers)
    asignaciones_existentes = {}
    
    if response_asig.status_code == 200:
        for a in response_asig.json():
            asignaciones_existentes[a.get('asignatura')] = a.get('documento_docente')
    
    with st.form("materias_form"):
        materias_asignadas = {}
        for asignatura in asignaturas:
            col1, col2 = st.columns([2, 3])
            with col1:
                st.write(f"**{asignatura}**")
            with col2:
                current_doc = asignaciones_existentes.get(asignatura)
                current_nombre = "-- Sin asignar --"
                for nombre, doc in docentes_dict.items():
                    if doc == current_doc:
                        current_nombre = nombre
                        break
                
                index = docentes_lista.index(current_nombre) if current_nombre in docentes_lista else 0
                docente = st.selectbox(
                    "Docente",
                    docentes_lista,
                    index=index,
                    key=f"materia_{curso}_{asignatura}",
                    label_visibility="collapsed"
                )
                materias_asignadas[asignatura] = docente if docente != "-- Sin asignar --" else None
        
        if st.form_submit_button("💾 Guardar Asignación de Materias", type="primary"):
            guardar_materias(curso, materias_asignadas, docentes_dict, headers)
    
    st.divider()
    mostrar_resumen_asignaciones(curso, headers, docentes_dict)

# ============================================
# SISTEMA
# ============================================
def mostrar_sistema():
    st.subheader("⚙️ Configuración del Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        nombre_colegio = st.text_input("Nombre del colegio", "Mi Colegio")
        año_lectivo = st.number_input("Año lectivo", min_value=2000, max_value=2100, value=2024)
        
        if st.button("💾 Guardar Configuración"):
            st.success("Configuración guardada")
    
    with col2:
        if st.button("📀 Crear Respaldo"):
            st.success("Respaldo creado")
