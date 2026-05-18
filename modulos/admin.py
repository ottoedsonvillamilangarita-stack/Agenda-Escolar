import streamlit as st
import requests
import pandas as pd
from utils import SUPABASE_URL, get_headers

def mostrar(data):
    st.title("🛡️ Panel de Administrador")
    st.write(f"Bienvenido, {data.get('username', 'Admin')}")
    
    # Menú lateral
    opcion = st.sidebar.selectbox(
        "Seleccionar función",
        ["📊 Dashboard", "👥 Usuarios", "📚 Cursos", "📈 Reportes", "⚙️ Configuración"]
    )
    
    if opcion == "📊 Dashboard":
        mostrar_dashboard()
    elif opcion == "👥 Usuarios":
        mostrar_usuarios()
    elif opcion == "📚 Cursos":
        mostrar_cursos()
    elif opcion == "📈 Reportes":
        mostrar_reportes()
    elif opcion == "⚙️ Configuración":
        mostrar_configuracion()

def mostrar_dashboard():
    st.subheader("📊 Dashboard")
    
    headers = get_headers()
    
    # Contar estudiantes
    url_estudiantes = f"{SUPABASE_URL}/rest/v1/estudiantes"
    response_est = requests.get(url_estudiantes, headers=headers)
    total_estudiantes = len(response_est.json()) if response_est.status_code == 200 else 0
    
    # Contar docentes (distintos)
    url_docentes = f"{SUPABASE_URL}/rest/v1/docentes"
    response_doc = requests.get(url_docentes, headers=headers)
    if response_doc.status_code == 200:
        datos = response_doc.json()
        # Contar docentes únicos por documento
        docentes_unicos = set([d.get('documento_docente') for d in datos])
        total_docentes = len(docentes_unicos)
    else:
        total_docentes = 0
    
    # Contar usuarios
    url_usuarios = f"{SUPABASE_URL}/rest/v1/usuarios_login"
    response_usr = requests.get(url_usuarios, headers=headers)
    total_usuarios = len(response_usr.json()) if response_usr.status_code == 200 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👨‍🎓 Estudiantes", total_estudiantes)
    col2.metric("👨‍🏫 Docentes", total_docentes)
    col3.metric("👥 Usuarios", total_usuarios)
    col4.metric("📚 Cursos", "7")
    
    st.info("📌 Módulo en desarrollo - Próximamente más estadísticas")

def mostrar_usuarios():
    st.subheader("👥 Gestión de Usuarios")
    
    headers = get_headers()
    url = f"{SUPABASE_URL}/rest/v1/usuarios_login"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        datos = response.json()
        if datos:
            df = pd.DataFrame(datos)
            st.dataframe(df, use_container_width=True)
            st.caption(f"Total: {len(datos)} usuarios")
        else:
            st.info("No hay usuarios registrados")
    else:
        st.error(f"Error {response.status_code}: No se pudieron cargar los usuarios")

def mostrar_cursos():
    st.subheader("📚 Gestión de Cursos")
    
    cursos = ["901", "902", "903", "1001", "1002", "1003", "1101"]
    
    for curso in cursos:
        with st.expander(f"Curso {curso}"):
            st.write(f"**Materias asignadas para {curso}:**")
            # Aquí puedes agregar la consulta a la tabla asignacion_academica cuando la tengas
            st.write("Próximamente: Lista de materias y docentes")

def mostrar_reportes():
    st.subheader("📈 Reportes")
    st.write("📊 Reportes disponibles:")
    st.write("- Reporte de estudiantes por curso")
    st.write("- Reporte de docentes por asignatura")
    st.write("- Reporte de notas (próximamente)")
    st.write("- Reporte de asistencia (próximamente)")

def mostrar_configuracion():
    st.subheader("⚙️ Configuración")
    st.write("Configuración del sistema:")
    st.write("- Gestión de períodos académicos (próximamente)")
    st.write("- Configuración de notas (próximamente)")
    st.write("- Respaldo de datos (próximamente)")
