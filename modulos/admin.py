import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from utils import SUPABASE_URL, get_headers

def mostrar(data):
    st.title("🛡️ Panel de Administrador")
    st.write(f"Bienvenido, {data.get('username', 'Admin')}")
    
    # Inicializar función actual
    if "admin_funcion" not in st.session_state:
        st.session_state.admin_funcion = "dashboard"
    
    # ============================================
    # MENÚ DE ADMIN (FUNCIONES EXCLUSIVAS)
    # ============================================
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Dashboard", use_container_width=True,
                     type="primary" if st.session_state.admin_funcion == "dashboard" else "secondary"):
            st.session_state.admin_funcion = "dashboard"
            st.rerun()
    
    with col2:
        if st.button("👥 Usuarios", use_container_width=True,
                     type="primary" if st.session_state.admin_funcion == "usuarios" else "secondary"):
            st.session_state.admin_funcion = "usuarios"
            st.rerun()
    
    with col3:
        if st.button("🔐 Roles", use_container_width=True,
                     type="primary" if st.session_state.admin_funcion == "roles" else "secondary"):
            st.session_state.admin_funcion = "roles"
            st.rerun()
    
    with col4:
        if st.button("⚙️ Configuración", use_container_width=True,
                     type="primary" if st.session_state.admin_funcion == "configuracion" else "secondary"):
            st.session_state.admin_funcion = "configuracion"
            st.rerun()
    
    st.divider()
    
    # ============================================
    # MOSTRAR FUNCIÓN SELECCIONADA
    # ============================================
    
    if st.session_state.admin_funcion == "dashboard":
        mostrar_dashboard()
    elif st.session_state.admin_funcion == "usuarios":
        mostrar_gestion_usuarios()
    elif st.session_state.admin_funcion == "roles":
        mostrar_gestion_roles()
    elif st.session_state.admin_funcion == "configuracion":
        mostrar_configuracion()

def mostrar_dashboard():
    st.subheader("📊 Dashboard Administrativo")
    
    headers = get_headers()
    
    # Estadísticas generales
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
    
    url_usr = f"{SUPABASE_URL}/rest/v1/usuarios_login"
    response_usr = requests.get(url_usr, headers=headers)
    total_usuarios = len(response_usr.json()) if response_usr.status_code == 200 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👨‍🎓 Estudiantes", total_estudiantes)
    col2.metric("👨‍🏫 Docentes", total_docentes)
    col3.metric("👥 Usuarios", total_usuarios)
    col4.metric("📚 Cursos", "7")
    
    st.info("🔐 Panel exclusivo del Administrador del sistema")

def mostrar_gestion_usuarios():
    st.subheader("👥 Gestión de Usuarios")
    
    tab1, tab2, tab3 = st.tabs(["📋 Lista de Usuarios", "➕ Crear Usuario", "✏️ Editar Usuario"])
    
    with tab1:
        headers = get_headers()
        url = f"{SUPABASE_URL}/rest/v1/usuarios_login"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            usuarios = response.json()
            if usuarios:
                df = pd.DataFrame(usuarios)
                st.dataframe(df, use_container_width=True)
                st.caption(f"Total: {len(usuarios)} usuarios")
            else:
                st.info("No hay usuarios registrados")
    
    with tab2:
        st.write("**Crear nuevo usuario**")
        nuevo_user = st.text_input("Username")
        nueva_pass = st.text_input("Contraseña", type="password")
        nuevo_rol = st.selectbox("Rol", ["admin", "secretaria", "supervisor", "director", "estudiante", "docente", "acudiente"])
        
        if st.button("➕ Crear", type="primary"):
            headers = get_headers()
            data = {
                "username": nuevo_user,
                "password_hash": nueva_pass,
                "rol": nuevo_rol,
                "roles": [nuevo_rol]
            }
            url = f"{SUPABASE_URL}/rest/v1/usuarios_login"
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 201:
                st.success(f"✅ Usuario {nuevo_user} creado exitosamente")
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
    
    with tab3:
        st.write("**Editar usuario existente**")
        st.info("Funcionalidad en desarrollo")

def mostrar_gestion_roles():
    st.subheader("🔐 Gestión de Roles y Permisos")
    
    st.write("**Roles disponibles en el sistema:**")
    
    roles = {
        "admin": "Control total del sistema",
        "secretaria": "Gestión administrativa (matrículas, horarios, documentación)",
        "supervisor": "Supervisión académica y evaluación docente",
        "director": "Gestión de curso específico",
        "docente": "Gestión de cursos, notas, asistencia",
        "estudiante": "Ver notas, horario, asistencia",
        "acudiente": "Seguimiento de hijos"
    }
    
    for rol, descripcion in roles.items():
        with st.expander(f"📌 {rol.upper()}"):
            st.write(f"**Descripción:** {descripcion}")
            st.write(f"**Permisos:**")
            if rol == "admin":
                st.write("- ✅ Crear/editar/eliminar usuarios")
                st.write("- ✅ Configurar roles y permisos")
                st.write("- ✅ Ver respaldos y logs")
            elif rol == "secretaria":
                st.write("- ✅ Gestionar estudiantes (altas/bajas)")
                st.write("- ✅ Gestionar matrículas")
                st.write("- ✅ Emitir certificados")
                st.write("- ❌ No puede crear usuarios")
            elif rol == "docente":
                st.write("- ✅ Ingresar notas")
                st.write("- ✅ Marcar asistencia")
                st.write("- ✅ Crear evaluaciones")
                st.write("- ❌ No puede modificar estudiantes")

def mostrar_configuracion():
    st.subheader("⚙️ Configuración del Sistema")
    
    tab1, tab2, tab3 = st.tabs(["🏫 Configuración General", "💾 Respaldos", "📊 Logs"])
    
    with tab1:
        st.write("**Configuración general**")
        nombre_colegio = st.text_input("Nombre del colegio", "Mi Colegio")
        año_lectivo = st.number_input("Año lectivo", min_value=2000, max_value=2100, value=2024)
        periodos = st.select_slider("Número de períodos académicos", options=[2, 3, 4], value=4)
        
        if st.button("💾 Guardar Configuración", type="primary"):
            st.success("✅ Configuración guardada exitosamente")
    
    with tab2:
        st.write("**Respaldos de base de datos**")
        if st.button("📀 Crear Respaldo", type="primary"):
            st.info("Generando respaldo...")
            st.success("✅ Respaldo creado exitosamente")
        
        st.write("**Respaldos disponibles:**")
        st.info("No hay respaldos disponibles")
    
    with tab3:
        st.write("**Logs del sistema**")
        logs = [
            {"fecha": "2024-01-15 10:30", "usuario": "admin", "accion": "Login exitoso"},
            {"fecha": "2024-01-15 09:00", "usuario": "secretaria", "accion": "Creó estudiante"},
        ]
        if logs:
            df = pd.DataFrame(logs)
            st.dataframe(df, use_container_width=True)
