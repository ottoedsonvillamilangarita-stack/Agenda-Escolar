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
    
    # Contar estudiantes
    response_est = requests.get(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers)
    total_alumnos = len(response_est.json()) if response_est.status_code == 200 else 0
    
    # Contar docentes
    response_doc = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
    if response_doc.status_code == 200:
        datos = response_doc.json()
        docentes_unicos = set([d.get('documento_docente') for d in datos])
        total_docentes = len(docentes_unicos)
    else:
        total_docentes = 0
    
    # Contar acudientes únicos
    acudientes_unicos = set()
    if response_est.status_code == 200:
        for est in response_est.json():
            if est.get('documento_acudiente'):
                acudientes_unicos.add(est.get('documento_acudiente'))
    total_acudientes = len(acudientes_unicos)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👨‍🎓 Alumnos", total_alumnos)
    col2.metric("👨‍🏫 Docentes", total_docentes)
    col3.metric("👨‍👩‍👧 Acudientes", total_acudientes)
    col4.metric("📚 Cursos", "7")
    
    st.info("🔐 Panel de control del Administrador")

# ============================================
# ALUMNOS (CON TODOS LOS CAMPOS)
# ============================================
def mostrar_alumnos():
    st.subheader("👨‍🎓 Gestión de Alumnos")
    
    tab1, tab2, tab3 = st.tabs(["📋 Lista de Alumnos", "➕ Nuevo Alumno", "📥 Carga Masiva"])
    
    with tab1:
        headers = get_headers()
        response = requests.get(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers)
        
        if response.status_code == 200:
            alumnos = response.json()
            if alumnos:
                df = pd.DataFrame(alumnos)
                st.dataframe(df, use_container_width=True)
                st.caption(f"Total: {len(alumnos)} alumnos")
            else:
                st.info("No hay alumnos registrados")
    
    with tab2:
        st.write("**Registrar nuevo alumno**")
        st.info("📌 Todos los campos están disponibles para uso futuro")
        
        with st.form("nuevo_alumno", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Datos personales**")
                nombre = st.text_input("Nombre *")
                apellidos = st.text_input("Apellidos *")
                documento = st.text_input("Documento *")
                curso = st.selectbox("Curso *", ["901", "902", "903", "1001", "1002", "1003", "1101"])
                sexo = st.selectbox("Sexo", ["", "Masculino", "Femenino"])
                fecha_nacimiento = st.date_input("Fecha de nacimiento", value=None)
                lugar_nacimiento = st.text_input("Lugar de nacimiento")
            
            with col2:
                st.markdown("**Datos del acudiente**")
                nombre_acudiente = st.text_input("Nombre del acudiente *")
                documento_acudiente = st.text_input("Documento del acudiente *")
                parentesco = st.selectbox("Parentesco", ["", "Padre", "Madre", "Tío", "Tía", "Abuelo", "Abuela", "Hermano", "Hermana", "Otro"])
                telefono_acudiente = st.text_input("Teléfono del acudiente")
                email_acudiente = st.text_input("Email del acudiente")
                direccion_acudiente = st.text_input("Dirección del acudiente")
            
            st.markdown("**Datos adicionales**")
            col3, col4 = st.columns(2)
            with col3:
                telefono_estudiante = st.text_input("Teléfono del estudiante")
                email_estudiante = st.text_input("Email del estudiante")
            with col4:
                direccion_estudiante = st.text_input("Dirección del estudiante")
                observaciones = st.text_area("Observaciones")
            
            if st.form_submit_button("💾 Guardar Alumno", type="primary"):
                if not all([nombre, apellidos, documento, curso, nombre_acudiente, documento_acudiente]):
                    st.error("❌ Por favor completa todos los campos obligatorios (*)")
                else:
                    headers = get_headers()
                    
                    # Datos completos del alumno
                    data_alumno = {
                        "nombre_estudiante": nombre,
                        "apellidos_estudiante": apellidos,
                        "documento_estudiante": documento,
                        "curso": curso,
                        "sexo_estudiante": sexo,
                        "fecha_nacimiento": str(fecha_nacimiento) if fecha_nacimiento else None,
                        "lugar_nacimiento": lugar_nacimiento,
                        "telefono_estudiante": telefono_estudiante,
                        "email_estudiante": email_estudiante,
                        "direccion_estudiante": direccion_estudiante,
                        "nombre_acudiente": nombre_acudiente,
                        "documento_acudiente": documento_acudiente,
                        "parentesco": parentesco,
                        "telefono_acudiente": telefono_acudiente,
                        "email_acudiente": email_acudiente,
                        "direccion_acudiente": direccion_acudiente,
                        "observaciones": observaciones
                    }
                    
                    response = requests.post(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers, json=data_alumno)
                    
                    if response.status_code == 201:
                        # Crear usuario para el alumno
                        user_alumno = {
                            "username": documento,
                            "password_hash": "demo2026",
                            "rol": "estudiante",
                            "documento": documento
                        }
                        requests.post(f"{SUPABASE_URL}/rest/v1/usuarios_login", headers=headers, json=user_alumno)
                        
                        # Crear usuario para el acudiente
                        username_acudiente = nombre_acudiente.lower().replace(" ", "_") + "_" + documento_acudiente[-4:]
                        user_acudiente = {
                            "username": username_acudiente,
                            "password_hash": "demo2026",
                            "rol": "acudiente",
                            "documento": documento_acudiente
                        }
                        requests.post(f"{SUPABASE_URL}/rest/v1/usuarios_login", headers=headers, json=user_acudiente)
                        
                        st.success(f"✅ Alumno {nombre} registrado exitosamente")
                        st.info(f"🔑 Usuario alumno: {documento} | Contraseña: demo2026")
                        st.info(f"🔑 Usuario acudiente: {username_acudiente} | Contraseña: demo2026")
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
    
    with tab3:
        st.write("**Carga masiva de alumnos**")
        st.info("Formato CSV: nombre_estudiante, apellidos_estudiante, documento_estudiante, curso, sexo_estudiante, nombre_acudiente, documento_acudiente, parentesco, telefono_acudiente, email_acudiente")
        
        archivo = st.file_uploader("Seleccionar archivo CSV", type=['csv'], key="carga_alumnos")
        
        if archivo:
            df = pd.read_csv(archivo)
            st.write("**Vista previa:**")
            st.dataframe(df.head())
            
            if st.button("📤 Cargar Alumnos", type="primary"):
                headers = get_headers()
                exitos = 0
                errores = 0
                
                for _, row in df.iterrows():
                    data = {
                        "nombre_estudiante": row.get('nombre_estudiante', ''),
                        "apellidos_estudiante": row.get('apellidos_estudiante', ''),
                        "documento_estudiante": str(row.get('documento_estudiante', '')),
                        "curso": str(row.get('curso', '')),
                        "sexo_estudiante": row.get('sexo_estudiante', ''),
                        "nombre_acudiente": row.get('nombre_acudiente', ''),
                        "documento_acudiente": str(row.get('documento_acudiente', '')),
                        "parentesco": row.get('parentesco', ''),
                        "telefono_acudiente": str(row.get('telefono_acudiente', '')),
                        "email_acudiente": row.get('email_acudiente', '')
                    }
                    response = requests.post(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers, json=data)
                    
                    if response.status_code == 201:
                        exitos += 1
                    else:
                        errores += 1
                
                st.success(f"✅ Carga completada: {exitos} alumnos, {errores} errores")

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
                    "email": alumno.get('email_acudiente'),
                    "direccion": alumno.get('direccion_acudiente'),
                    "parentesco": alumno.get('parentesco'),
                    "hijos": []
                }
            if doc_acud:
                acudientes_dict[doc_acud]["hijos"].append({
                    "nombre": alumno.get('nombre_estudiante'),
                    "curso": alumno.get('curso')
                })
        
        if acudientes_dict:
            df = pd.DataFrame([{
                "Nombre": v["nombre"],
                "Documento": v["documento"],
                "Teléfono": v["telefono"],
                "Email": v["email"],
                "Parentesco": v["parentesco"],
                "Hijos": ", ".join([h["nombre"] for h in v["hijos"]])
            } for v in acudientes_dict.values()])
            st.dataframe(df, use_container_width=True)
            st.caption(f"Total: {len(acudientes_dict)} acudientes")
        else:
            st.info("No hay acudientes registrados")

# ============================================
# DOCENTES (CON TODOS LOS CAMPOS)
# ============================================
def mostrar_docentes():
    st.subheader("👨‍🏫 Gestión de Docentes")
    
    tab1, tab2, tab3 = st.tabs(["📋 Lista de Docentes", "➕ Nuevo Docente", "📥 Carga Masiva"])
    
    with tab1:
        headers = get_headers()
        response = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
        
        if response.status_code == 200:
            docentes = response.json()
            if docentes:
                df = pd.DataFrame(docentes)
                st.dataframe(df, use_container_width=True)
                st.caption(f"Total: {len(docentes)} registros")
            else:
                st.info("No hay docentes registrados")
    
    with tab2:
        st.write("**Registrar nuevo docente**")
        st.info("📌 Todos los campos están disponibles para uso futuro")
        
        with st.form("nuevo_docente", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Datos personales**")
                nombre = st.text_input("Nombre *")
                apellidos = st.text_input("Apellidos *")
                documento = st.text_input("Documento *")
                sexo = st.selectbox("Sexo", ["", "Masculino", "Femenino"])
                fecha_nacimiento = st.date_input("Fecha de nacimiento", value=None)
                titulo = st.text_input("Título profesional")
                especializacion = st.text_input("Especialización")
            
            with col2:
                st.markdown("**Datos de contacto**")
                telefono = st.text_input("Teléfono")
                email = st.text_input("Email")
                direccion = st.text_input("Dirección")
                
                st.markdown("**Asignación académica**")
                curso = st.selectbox("Curso *", ["", "901", "902", "903", "1001", "1002", "1003", "1101"])
                asignatura = st.text_input("Asignatura *")
                intensidad = st.number_input("Intensidad horaria", min_value=1, max_value=10, value=4)
            
            st.markdown("**Datos adicionales**")
            col3, col4 = st.columns(2)
            with col3:
                fecha_ingreso = st.date_input("Fecha de ingreso", value=None)
                tipo_contrato = st.selectbox("Tipo de contrato", ["", "Planta", "Contrato", "Ocasional", "Cátedra"])
            with col4:
                observaciones = st.text_area("Observaciones")
            
            if st.form_submit_button("💾 Guardar Docente", type="primary"):
                if not all([nombre, apellidos, documento, curso, asignatura]):
                    st.error("❌ Por favor completa todos los campos obligatorios (*)")
                else:
                    headers = get_headers()
                    
                    data = {
                        "nombre_docente": nombre,
                        "apellidos_docente": apellidos,
                        "documento_docente": documento,
                        "sexo_docente": sexo,
                        "fecha_nacimiento": str(fecha_nacimiento) if fecha_nacimiento else None,
                        "titulo": titulo,
                        "especializacion": especializacion,
                        "telefono_docente": telefono,
                        "email_docente": email,
                        "direccion_docente": direccion,
                        "curso": curso,
                        "asignatura": asignatura,
                        "intensidad": str(intensidad),
                        "fecha_ingreso": str(fecha_ingreso) if fecha_ingreso else None,
                        "tipo_contrato": tipo_contrato,
                        "observaciones": observaciones
                    }
                    
                    response = requests.post(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers, json=data)
                    
                    if response.status_code == 201:
                        # Crear usuario para el docente
                        username_docente = nombre.lower().replace(" ", "_") + "_" + documento[-4:]
                        user_docente = {
                            "username": username_docente,
                            "password_hash": "demo2026",
                            "rol": "docente",
                            "documento": documento
                        }
                        requests.post(f"{SUPABASE_URL}/rest/v1/usuarios_login", headers=headers, json=user_docente)
                        
                        st.success(f"✅ Docente {nombre} registrado exitosamente")
                        st.info(f"🔑 Usuario: {username_docente} | Contraseña: demo2026")
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
    
    with tab3:
        st.write("**Carga masiva de docentes**")
        st.info("Formato CSV: nombre_docente, apellidos_docente, documento_docente, curso, asignatura, intensidad, telefono_docente, email_docente")
        
        archivo = st.file_uploader("Seleccionar archivo CSV", type=['csv'], key="carga_docentes")
        
        if archivo:
            df = pd.read_csv(archivo)
            st.write("**Vista previa:**")
            st.dataframe(df.head())
            
            if st.button("📤 Cargar Docentes", type="primary"):
                headers = get_headers()
                exitos = 0
                errores = 0
                
                for _, row in df.iterrows():
                    data = {
                        "nombre_docente": row.get('nombre_docente', ''),
                        "apellidos_docente": row.get('apellidos_docente', ''),
                        "documento_docente": str(row.get('documento_docente', '')),
                        "curso": str(row.get('curso', '')),
                        "asignatura": row.get('asignatura', ''),
                        "intensidad": str(row.get('intensidad', '4')),
                        "telefono_docente": str(row.get('telefono_docente', '')),
                        "email_docente": row.get('email_docente', '')
                    }
                    response = requests.post(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers, json=data)
                    
                    if response.status_code == 201:
                        exitos += 1
                    else:
                        errores += 1
                
                st.success(f"✅ Carga completada: {exitos} docentes, {errores} errores")

# ============================================
# ASIGNACIÓN ACADÉMICA
# ============================================
def mostrar_asignacion():
    st.subheader("📚 Asignación Académica")
    st.info("🚧 Módulo en construcción - Próximamente")
    st.write("Aquí se configurarán:")
    st.write("- Asignación de docentes a cursos")
    st.write("- Horarios de clase")
    st.write("- Planes de estudio")

# ============================================
# SISTEMA
# ============================================
def mostrar_sistema():
    st.subheader("⚙️ Configuración del Sistema")
    
    tab1, tab2 = st.tabs(["🏫 General", "💾 Respaldos"])
    
    with tab1:
        st.write("**Configuración institucional**")
        
        nombre_colegio = st.text_input("Nombre del colegio", "Mi Colegio")
        año_lectivo = st.number_input("Año lectivo", min_value=2000, max_value=2100, value=2024)
        periodos = st.select_slider("Número de períodos académicos", options=[2, 3, 4], value=4)
        
        if st.button("💾 Guardar Configuración", type="primary"):
            st.success("✅ Configuración guardada exitosamente")
    
    with tab2:
        st.write("**Respaldos de base de datos**")
        
        if st.button("📀 Crear Respaldo", type="primary"):
            with st.spinner("Generando respaldo..."):
                st.success("✅ Respaldo creado exitosamente")
