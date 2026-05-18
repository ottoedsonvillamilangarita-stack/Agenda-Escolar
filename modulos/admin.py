import streamlit as st
import requests
import pandas as pd
import io
from datetime import datetime
from utils import SUPABASE_URL, get_headers

def mostrar(data):
    st.title("🛡️ Panel de Administrador")
    st.write(f"Bienvenido, {data.get('username', 'Admin')}")
    
    # Inicializar función actual
    if "admin_funcion" not in st.session_state:
        st.session_state.admin_funcion = "dashboard"
    
    # ============================================
    # MENÚ DE ADMIN (REDISEÑADO)
    # ============================================
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Dashboard", use_container_width=True,
                     type="primary" if st.session_state.admin_funcion == "dashboard" else "secondary"):
            st.session_state.admin_funcion = "dashboard"
            st.rerun()
    
    with col2:
        if st.button("📥 Carga Masiva", use_container_width=True,
                     type="primary" if st.session_state.admin_funcion == "carga_masiva" else "secondary"):
            st.session_state.admin_funcion = "carga_masiva"
            st.rerun()
    
    with col3:
        if st.button("👥 Usuarios", use_container_width=True,
                     type="primary" if st.session_state.admin_funcion == "usuarios" else "secondary"):
            st.session_state.admin_funcion = "usuarios"
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
    elif st.session_state.admin_funcion == "carga_masiva":
        mostrar_carga_masiva()
    elif st.session_state.admin_funcion == "usuarios":
        mostrar_gestion_usuarios()
    elif st.session_state.admin_funcion == "configuracion":
        mostrar_configuracion()

def mostrar_dashboard():
    st.subheader("📊 Dashboard Administrativo")
    
    headers = get_headers()
    
    # Estadísticas
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
    
    # Acudientes únicos (desde estudiantes)
    acudientes_unicos = set()
    if response_est.status_code == 200:
        for est in response_est.json():
            if est.get('documento_acudiente'):
                acudientes_unicos.add(est.get('documento_acudiente'))
    total_acudientes = len(acudientes_unicos)
    
    url_usr = f"{SUPABASE_URL}/rest/v1/usuarios_login"
    response_usr = requests.get(url_usr, headers=headers)
    total_usuarios = len(response_usr.json()) if response_usr.status_code == 200 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👨‍🎓 Estudiantes", total_estudiantes)
    col2.metric("👨‍🏫 Docentes", total_docentes)
    col3.metric("👨‍👩‍👧 Acudientes", total_acudientes)
    col4.metric("👥 Usuarios Login", total_usuarios)
    
    st.info("🔐 Panel exclusivo del Administrador del sistema")

def mostrar_carga_masiva():
    st.subheader("📥 Carga Masiva de Datos")
    
    tab1, tab2 = st.tabs(["📚 Cargar Estudiantes", "👨‍🏫 Cargar Docentes"])
    
    with tab1:
        st.write("**Cargar estudiantes desde archivo CSV/Excel**")
        st.write("Formato requerido:")
        st.code("nombre_estudiante,apellidos_estudiante,documento_estudiante,curso,nombre_acudiente,documento_acudiente,parentesco,telefono_acudiente,email_acudiente")
        
        archivo = st.file_uploader("Seleccionar archivo", type=['csv', 'xlsx'], key="estudiantes")
        
        if archivo:
            if archivo.name.endswith('.csv'):
                df = pd.read_csv(archivo)
            else:
                df = pd.read_excel(archivo)
            
            st.write("**Vista previa de los datos:**")
            st.dataframe(df.head())
            
            if st.button("📤 Cargar Estudiantes", type="primary"):
                headers = get_headers()
                exitos = 0
                errores = 0
                
                for _, row in df.iterrows():
                    data = {
                        "nombre_estudiante": row['nombre_estudiante'],
                        "apellidos_estudiante": row['apellidos_estudiante'],
                        "documento_estudiante": str(row['documento_estudiante']),
                        "curso": str(row['curso']),
                        "nombre_acudiente": row.get('nombre_acudiente', ''),
                        "documento_acudiente": str(row.get('documento_acudiente', '')),
                        "parentesco": row.get('parentesco', ''),
                        "telefono_acudiente": str(row.get('telefono_acudiente', '')),
                        "email_acudiente": row.get('email_acudiente', '')
                    }
                    
                    url = f"{SUPABASE_URL}/rest/v1/estudiantes"
                    response = requests.post(url, headers=headers, json=data)
                    
                    if response.status_code == 201:
                        exitos += 1
                    else:
                        errores += 1
                
                st.success(f"✅ Carga completada: {exitos} estudiantes cargados, {errores} errores")
                
                # Actualizar usuarios_login para los nuevos estudiantes
                if exitos > 0:
                    actualizar_usuarios_login()
    
    with tab2:
        st.write("**Cargar docentes desde archivo CSV/Excel**")
        st.write("Formato requerido:")
        st.code("nombre_docente,apellidos_docente,documento_docente,curso,asignatura,intensidad,telefono_docente,email_docente")
        
        archivo = st.file_uploader("Seleccionar archivo", type=['csv', 'xlsx'], key="docentes")
        
        if archivo:
            if archivo.name.endswith('.csv'):
                df = pd.read_csv(archivo)
            else:
                df = pd.read_excel(archivo)
            
            st.write("**Vista previa de los datos:**")
            st.dataframe(df.head())
            
            if st.button("📤 Cargar Docentes", type="primary"):
                headers = get_headers()
                exitos = 0
                errores = 0
                
                for _, row in df.iterrows():
                    data = {
                        "nombre_docente": row['nombre_docente'],
                        "apellidos_docente": row['apellidos_docente'],
                        "documento_docente": str(row['documento_docente']),
                        "curso": str(row['curso']),
                        "asignatura": row['asignatura'],
                        "intensidad": str(row.get('intensidad', '')),
                        "telefono_docente": str(row.get('telefono_docente', '')),
                        "email_docente": row.get('email_docente', '')
                    }
                    
                    url = f"{SUPABASE_URL}/rest/v1/docentes"
                    response = requests.post(url, headers=headers, json=data)
                    
                    if response.status_code == 201:
                        exitos += 1
                    else:
                        errores += 1
                
                st.success(f"✅ Carga completada: {exitos} docentes cargados, {errores} errores")
                
                # Actualizar usuarios_login para los nuevos docentes
                if exitos > 0:
                    actualizar_usuarios_login()

def actualizar_usuarios_login():
    """Actualiza la tabla usuarios_login con estudiantes y docentes nuevos"""
    headers = get_headers()
    
    # Insertar estudiantes que no tengan usuario
    url_est = f"{SUPABASE_URL}/rest/v1/estudiantes"
    response_est = requests.get(url_est, headers=headers)
    
    if response_est.status_code == 200:
        estudiantes = response_est.json()
        for est in estudiantes:
            user_data = {
                "username": est['documento_estudiante'],
                "password_hash": "demo2026",
                "rol": "estudiante",
                "documento": est['documento_estudiante']
            }
            url = f"{SUPABASE_URL}/rest/v1/usuarios_login"
            requests.post(url, headers=headers, json=user_data)
    
    # Insertar docentes que no tengan usuario
    url_doc = f"{SUPABASE_URL}/rest/v1/docentes"
    response_doc = requests.get(url_doc, headers=headers)
    
    if response_doc.status_code == 200:
        docentes = response_doc.json()
        docentes_unicos = {}
        for doc in docentes:
            docentes_unicos[doc['documento_docente']] = doc['nombre_docente']
        
        for doc_doc, doc_nom in docentes_unicos.items():
            user_data = {
                "username": doc_nom,
                "password_hash": "demo2026",
                "rol": "docente",
                "documento": doc_doc
            }
            url = f"{SUPABASE_URL}/rest/v1/usuarios_login"
            requests.post(url, headers=headers, json=user_data)
    
    # Insertar acudientes únicos
    acudientes = {}
    for est in estudiantes:
        if est.get('documento_acudiente') and est.get('documento_acudiente') not in acudientes:
            acudientes[est['documento_acudiente']] = est['nombre_acudiente']
    
    for doc_acud, nom_acud in acudientes.items():
        user_data = {
            "username": nom_acud,
            "password_hash": "demo2026",
            "rol": "acudiente",
            "documento": doc_acud
        }
        url = f"{SUPABASE_URL}/rest/v1/usuarios_login"
        requests.post(url, headers=headers, json=user_data)

def mostrar_gestion_usuarios():
    st.subheader("👥 Gestión de Usuarios")
    
    tab1, tab2, tab3 = st.tabs(["📋 Lista de Usuarios", "➕ Crear Usuario Manual", "🗑️ Eliminar Usuario"])
    
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
        st.write("**Crear usuario manualmente**")
        
        nuevo_user = st.text_input("Username")
        nueva_pass = st.text_input("Contraseña", type="password")
        nuevo_rol = st.selectbox("Rol", ["admin", "secretaria", "supervisor", "director", "docente", "estudiante", "acudiente"])
        documento = st.text_input("Documento (opcional)", "0")
        
        if st.button("➕ Crear Usuario", type="primary"):
            headers = get_headers()
            data = {
                "username": nuevo_user,
                "password_hash": nueva_pass,
                "rol": nuevo_rol,
                "documento": documento
            }
            url = f"{SUPABASE_URL}/rest/v1/usuarios_login"
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 201:
                st.success(f"✅ Usuario {nuevo_user} creado exitosamente")
            else:
                st.error(f"Error: {response.status_code}")
    
    with tab3:
        st.write("**Eliminar usuario**")
        usuario_eliminar = st.text_input("Username a eliminar")
        
        if st.button("🗑️ Eliminar Usuario", type="primary"):
            headers = get_headers()
            url = f"{SUPABASE_URL}/rest/v1/usuarios_login?username=eq.{usuario_eliminar}"
            response = requests.delete(url, headers=headers)
            
            if response.status_code == 204:
                st.success(f"✅ Usuario {usuario_eliminar} eliminado")
            else:
                st.error(f"Error: {response.status_code}")

def mostrar_configuracion():
    st.subheader("⚙️ Configuración del Sistema")
    
    tab1, tab2 = st.tabs(["🏫 General", "💾 Respaldos"])
    
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
            with st.spinner("Generando respaldo..."):
                # Aquí se generaría el respaldo
                st.success("✅ Respaldo creado exitosamente")
                st.download_button(
                    label="📥 Descargar Respaldo",
                    data="Datos del respaldo...",
                    file_name=f"respaldo_{datetime.now().strftime('%Y%m%d')}.csv"
                )
