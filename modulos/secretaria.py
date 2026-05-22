import streamlit as st
import requests
import pandas as pd
from utils import SUPABASE_URL, get_headers
from modulos.features.horarios import mostrar_horario_semanal_detallado

def mostrar(data):
    st.title("📋 Panel de Secretaria")
    st.write(f"Bienvenida, {data.get('username', 'Secretaria')}")
    
    # Inicializar función actual
    if "secretaria_funcion" not in st.session_state:
        st.session_state.secretaria_funcion = "dashboard"
    
    # ============================================
    # MENÚ DE SECRETARIA (FUNCIONES EXCLUSIVAS)
    # ============================================
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Dashboard", use_container_width=True,
                     type="primary" if st.session_state.secretaria_funcion == "dashboard" else "secondary"):
            st.session_state.secretaria_funcion = "dashboard"
            st.rerun()
    
    with col2:
        if st.button("👨‍🎓 Estudiantes", use_container_width=True,
                     type="primary" if st.session_state.secretaria_funcion == "estudiantes" else "secondary"):
            st.session_state.secretaria_funcion = "estudiantes"
            st.rerun()
    
    with col3:
        if st.button("📚 Matrículas", use_container_width=True,
                     type="primary" if st.session_state.secretaria_funcion == "matriculas" else "secondary"):
            st.session_state.secretaria_funcion = "matriculas"
            st.rerun()
    
    with col4:
        if st.button("📄 Certificados", use_container_width=True,
                     type="primary" if st.session_state.secretaria_funcion == "certificados" else "secondary"):
            st.session_state.secretaria_funcion = "certificados"
            st.rerun()
    
    col5, col6, col7 = st.columns(3)
    
    with col5:
        if st.button("📊 Reportes", use_container_width=True,
                     type="primary" if st.session_state.secretaria_funcion == "reportes" else "secondary"):
            st.session_state.secretaria_funcion = "reportes"
            st.rerun()
    
    with col6:
        if st.button("📁 Documentación", use_container_width=True,
                     type="primary" if st.session_state.secretaria_funcion == "documentacion" else "secondary"):
            st.session_state.secretaria_funcion = "documentacion"
            st.rerun()
    
    with col7:
        if st.button("📧 Comunicados", use_container_width=True,
                     type="primary" if st.session_state.secretaria_funcion == "comunicados" else "secondary"):
            st.session_state.secretaria_funcion = "comunicados"
            st.rerun()
    
    st.divider()
    
    # ============================================
    # MOSTRAR FUNCIÓN SELECCIONADA
    # ============================================
    
    if st.session_state.secretaria_funcion == "dashboard":
        mostrar_dashboard()
    elif st.session_state.secretaria_funcion == "estudiantes":
        gestion_estudiantes()
    elif st.session_state.secretaria_funcion == "matriculas":
        gestion_matriculas()
    elif st.session_state.secretaria_funcion == "certificados":
        gestion_certificados()
    elif st.session_state.secretaria_funcion == "reportes":
        gestion_reportes()
    elif st.session_state.secretaria_funcion == "documentacion":
        gestion_documentacion()
    elif st.session_state.secretaria_funcion == "comunicados":
        gestion_comunicados()
    elif opcion == "📅 Consultar Horarios":
    mostrar_consultar_horarios(data)
def mostrar_dashboard():
    st.subheader("📊 Dashboard Secretaria")
    
    headers = get_headers()
    
    url_est = f"{SUPABASE_URL}/rest/v1/estudiantes"
    response_est = requests.get(url_est, headers=headers)
    total_estudiantes = len(response_est.json()) if response_est.status_code == 200 else 0
    
    url_doc = f"{SUPABASE_URL}/rest/v1/docentes"
    response_doc = requests.get(url_doc, headers=headers)
    total_docentes = len(response_doc.json()) if response_doc.status_code == 200 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👨‍🎓 Estudiantes", total_estudiantes)
    col2.metric("👨‍🏫 Docentes", total_docentes)
    col3.metric("📚 Cursos", "7")
    col4.metric("📄 Certificados", "0 emitidos")
    
    st.info("📋 Panel de gestión administrativa")

def gestion_estudiantes():
    st.subheader("👨‍🎓 Gestión de Estudiantes")
    
    tab1, tab2, tab3 = st.tabs(["📋 Lista", "➕ Nuevo Estudiante", "✏️ Editar/Bajas"])
    
    with tab1:
        headers = get_headers()
        url = f"{SUPABASE_URL}/rest/v1/estudiantes"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            estudiantes = response.json()
            if estudiantes:
                df = pd.DataFrame(estudiantes)
                st.dataframe(df, use_container_width=True)
                st.caption(f"Total: {len(estudiantes)} estudiantes")
            else:
                st.info("No hay estudiantes registrados")
    
    with tab2:
        st.write("**Registrar nuevo estudiante**")
        with st.form("nuevo_estudiante"):
            nombre = st.text_input("Nombre")
            apellidos = st.text_input("Apellidos")
            documento = st.text_input("Documento")
            curso = st.selectbox("Curso", ["901", "902", "903", "1001", "1002", "1003", "1101"])
            acudiente = st.text_input("Nombre del acudiente")
            telefono = st.text_input("Teléfono de contacto")
            
            if st.form_submit_button("💾 Guardar"):
                st.success(f"✅ Estudiante {nombre} registrado exitosamente")
    
    with tab3:
        st.write("**Buscar estudiante para editar o dar de baja**")
        buscar = st.text_input("Documento o nombre")
        if buscar:
            st.info(f"Mostrando resultados para: {buscar}")

def gestion_matriculas():
    st.subheader("📚 Gestión de Matrículas")
    
    periodo = st.selectbox("Período académico", ["2024", "2025"])
    
    st.write(f"**Matrículas - Período {periodo}**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Matrículas activas", "251")
        st.metric("Pendientes", "0")
    
    with col2:
        st.metric("Canceladas", "0")
        st.metric("Traslados", "0")
    
    if st.button("📊 Generar Reporte de Matrículas", type="primary"):
        st.info("Generando reporte...")

def gestion_certificados():
    st.subheader("📄 Emisión de Certificados")
    
    estudiante = st.selectbox("Seleccionar estudiante", ["Buscar estudiante..."])
    tipo = st.selectbox("Tipo de certificado", 
                        ["Estudio", "Conducta", "Notas", "Terminación de estudios"])
    
    if st.button("📄 Generar Certificado", type="primary"):
        st.success("✅ Certificado generado exitosamente")
        st.download_button(
            label="📥 Descargar Certificado",
            data="Certificado.pdf",
            file_name="certificado.pdf"
        )

def gestion_reportes():
    st.subheader("📊 Reportes Administrativos")
    
    tipo = st.selectbox("Tipo de reporte", 
                        ["Listado de estudiantes", "Listado de docentes", "Distribución por curso", "Estadísticas generales"])
    
    if st.button("📄 Generar", type="primary"):
        st.success(f"✅ Reporte {tipo} generado")

def gestion_documentacion():
    st.subheader("📁 Documentación Administrativa")
    
    st.write("**Documentos disponibles:**")
    
    docs = ["Manual de convivencia", "Calendario académico", "Formatos de inscripción", "Reglamento interno"]
    
    for doc in docs:
        if st.button(f"📄 {doc}", key=doc):
            st.info(f"Descargando {doc}...")

def gestion_comunicados():
    st.subheader("📧 Comunicados y Circulares")
    
    opcion = st.radio("", ["📝 Nuevo comunicado", "📋 Ver comunicados anteriores"])
    
    if opcion == "📝 Nuevo comunicado":
        titulo = st.text_input("Título")
        destinatarios = st.multiselect("Dirigido a", 
                                       ["Estudiantes", "Padres", "Docentes", "Administrativos"])
        contenido = st.text_area("Contenido")
        
        if st.button("📨 Enviar", type="primary"):
            st.success("✅ Comunicado enviado exitosamente")
    
    else:
        st.write("**Comunicados anteriores**")
        st.info("No hay comunicados guardados")
