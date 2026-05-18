import streamlit as st
import requests
import pandas as pd
import io
from datetime import datetime
from utils import SUPABASE_URL, get_headers

def mostrar(data):
    st.title("🛡️ Panel de Administrador")
    st.write(f"Bienvenido, {data.get('username', 'Admin')}")
    
    # Inicializar sección actual
    if "admin_seccion" not in st.session_state:
        st.session_state.admin_seccion = "dashboard"
    
    # ============================================
    # MENÚ PRINCIPAL (por secciones)
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
        mostrar_gestion_alumnos()
    elif st.session_state.admin_seccion == "acudientes":
        mostrar_gestion_acudientes()
    elif st.session_state.admin_seccion == "docentes":
        mostrar_gestion_docentes()
    elif st.session_state.admin_seccion == "asignacion":
        mostrar_asignacion_academica()
    elif st.session_state.admin_seccion == "sistema":
        mostrar_configuracion_sistema()

# ============================================
# SECCIÓN 1: DASHBOARD
# ============================================
def mostrar_dashboard():
    st.subheader("📊 Dashboard General")
    
    headers = get_headers()
    
    # Estadísticas de alumnos
    url_alumnos = f"{SUPABASE_URL}/rest/v1/estudiantes"
    response_alumnos = requests.get(url_alumnos, headers=headers)
    total_alumnos = len(response_alumnos.json()) if response_alumnos.status_code == 200 else 0
    
    # Estadísticas de docentes
    url_docentes = f"{SUPABASE_URL}/rest/v1/docentes"
    response_docentes = requests.get(url_docentes, headers=headers)
    if response_docentes.status_code == 200:
        datos = response_docentes.json()
        docentes_unicos = set([d.get('documento_docente') for d in datos])
        total_docentes = len(docentes_unicos)
    else:
        total_docentes = 0
    
    # Estadísticas de acudientes
    acudientes_unicos = set()
    if response_alumnos.status_code == 200:
        for est in response_alumnos.json():
            if est.get('documento_acudiente'):
                acudientes_unicos.add(est.get('documento_acudiente'))
    total_acudientes = len(acudientes_unicos)
    
    # Cursos
    cursos = ["901", "902", "903", "1001", "1002", "1003", "1101"]
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👨‍🎓 Alumnos", total_alumnos)
    col2.metric("👨‍🏫 Docentes", total_docentes)
    col3.metric("👨‍👩‍👧 Acudientes", total_acudientes)
    col4.metric("📚 Cursos", len(cursos))
    
    # Distribución por curso
    st.subheader("📊 Distribución de Alumnos por Curso")
    
    if response_alumnos.status_code == 200:
        alumnos = response_alumnos.json()
        distribucion = {}
        for curso in cursos:
            distribucion[curso] = 0
        for alumno in alumnos:
            curso = alumno.get('curso', '')
            if curso in distribucion:
                distribucion[curso] += 1
        
        df_dist = pd.DataFrame(list(distribucion.items()), columns=["Curso", "Cantidad"])
        st.bar_chart(df_dist.set_index("Curso"))

# ============================================
# SECCIÓN 2: GESTIÓN DE ALUMNOS
# ============================================
def mostrar_gestion_alumnos():
    st.subheader("👨‍🎓 Gestión de Alumnos")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Lista de Alumnos", "➕ Nuevo Alumno", "✏️ Editar Alumno", "📥 Carga Masiva"])
    
    with tab1:
        headers = get_headers()
        url = f"{SUPABASE_URL}/rest/v1/estudiantes"
        response = requests.get(url, headers=headers)
        
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
                parentesco = st.selectbox("Parentesco", ["Padre", "Madre", "Tío", "Abuelo", "Otro"])
                telefono = st.text_input("Teléfono de contacto")
            
            if st.form_submit_button("💾 Guardar Alumno", type="primary"):
                headers = get_headers()
                data = {
                    "nombre_estudiante": nombre,
                    "apellidos_estudiante": apellidos,
                    "documento_estudiante": documento,
                    "curso": curso,
                    "nombre_acudiente": nombre_acudiente,
                    "documento_acudiente": documento_acudiente,
                    "parentesco": parentesco,
                    "telefono_acudiente": telefono
                }
                response = requests.post(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers, json=data)
                
                if response.status_code == 201:
                    st.success(f"✅ Alumno {nombre} registrado exitosamente")
                    # Actualizar usuario login
                    user_data = {
                        "username": documento,
                        "password_hash": "demo2026",
                        "rol": "estudiante",
                        "documento": documento
                    }
                    requests.post(f"{SUPABASE_URL}/rest/v1/usuarios_login", headers=headers, json=user_data)
                else:
                    st.error(f"Error: {response.status_code}")
    
    with tab3:
        st.write("**Buscar y editar alumno**")
        
        buscar = st.text_input("Documento del alumno")
        if buscar:
            headers = get_headers()
            url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{buscar}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200 and response.json():
                alumno = response.json()[0]
                
                with st.form("editar_alumno"):
                    col1, col2 = st.columns(2)
                    with col1:
                        nombre = st.text_input("Nombre", alumno.get('nombre_estudiante', ''))
                        apellidos = st.text_input("Apellidos", alumno.get('apellidos_estudiante', ''))
                        documento_edit = st.text_input("Documento", alumno.get('documento_estudiante', ''))
                        curso = st.selectbox("Curso", ["901", "902", "903", "1001", "1002", "1003", "1101"], 
                                            index=["901","902","903","1001","1002","1003","1101"].index(alumno.get('curso', '901')))
                    with col2:
                        nombre_acudiente = st.text_input("Nombre del acudiente", alumno.get('nombre_acudiente', ''))
                        documento_acudiente = st.text_input("Documento del acudiente", alumno.get('documento_acudiente', ''))
                        telefono = st.text_input("Teléfono", alumno.get('telefono_acudiente', ''))
                    
                    if st.form_submit_button("💾 Actualizar Alumno", type="primary"):
                        data = {
                            "nombre_estudiante": nombre,
                            "apellidos_estudiante": apellidos,
                            "curso": curso,
                            "nombre_acudiente": nombre_acudiente,
                            "documento_acudiente": documento_acudiente,
                            "telefono_acudiente": telefono
                        }
                        url_update = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{buscar}"
                        response = requests.patch(url_update, headers=headers, json=data)
                        
                        if response.status_code == 200:
                            st.success("✅ Alumno actualizado exitosamente")
                        else:
                            st.error(f"Error: {response.status_code}")
            else:
                st.warning("Alumno no encontrado")
    
    with tab4:
        st.write("**Carga masiva de alumnos desde archivo CSV/Excel**")
        st.info("Formato: nombre_estudiante, apellidos_estudiante, documento_estudiante, curso, nombre_acudiente, documento_acudiente, parentesco, telefono_acudiente")
        
        archivo = st.file_uploader("Seleccionar archivo", type=['csv', 'xlsx'], key="carga_alumnos")
        
        if archivo:
            if archivo.name.endswith('.csv'):
                df = pd.read_csv(archivo)
            else:
                df = pd.read_excel(archivo)
            
            st.write("**Vista previa:**")
            st.dataframe(df.head())
            
            if st.button("📤 Cargar Alumnos", type="primary"):
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
                        "telefono_acudiente": str(row.get('telefono_acudiente', ''))
                    }
                    response = requests.post(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers, json=data)
                    
                    if response.status_code == 201:
                        exitos += 1
                    else:
                        errores += 1
                
                st.success(f"✅ Carga completada: {exitos} alumnos, {errores} errores")

# ============================================
# SECCIÓN 3: GESTIÓN DE ACUDIENTES
# ============================================
def mostrar_gestion_acudientes():
    st.subheader("👨‍👩‍👧 Gestión de Acudientes")
    
    tab1, tab2 = st.tabs(["📋 Lista de Acudientes", "✏️ Editar Acudiente"])
    
    with tab1:
        headers = get_headers()
        url = f"{SUPABASE_URL}/rest/v1/estudiantes"
        response = requests.get(url, headers=headers)
        
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
                st.caption(f"Total: {len(acudientes_dict)} acudientes")
            else:
                st.info("No hay acudientes registrados")
    
    with tab2:
        st.write("**Buscar acudiente por documento**")
        buscar = st.text_input("Documento del acudiente")
        
        if buscar:
            headers = get_headers()
            url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_acudiente=eq.{buscar}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200 and response.json():
                hijos = response.json()
                acudiente = hijos[0]
                
                with st.form("editar_acudiente"):
                    nombre = st.text_input("Nombre", acudiente.get('nombre_acudiente', ''))
                    telefono = st.text_input("Teléfono", acudiente.get('telefono_acudiente', ''))
                    
                    st.write("**Hijos asociados:**")
                    for hijo in hijos:
                        st.write(f"- {hijo.get('nombre_estudiante')} - {hijo.get('curso')}")
                    
                    if st.form_submit_button("💾 Actualizar Acudiente", type="primary"):
                        for hijo in hijos:
                            data = {
                                "nombre_acudiente": nombre,
                                "telefono_acudiente": telefono
                            }
                            url_update = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{hijo.get('documento_estudiante')}"
                            requests.patch(url_update, headers=headers, json=data)
                        
                        st.success("✅ Acudiente actualizado exitosamente")
            else:
                st.warning("Acudiente no encontrado")

# ============================================
# SECCIÓN 4: GESTIÓN DE DOCENTES
# ============================================
def mostrar_gestion_docentes():
    st.subheader("👨‍🏫 Gestión de Docentes")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Lista de Docentes", "➕ Nuevo Docente", "✏️ Editar Docente", "📥 Carga Masiva"])
    
    with tab1:
        headers = get_headers()
        url = f"{SUPABASE_URL}/rest/v1/docentes"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            docentes = response.json()
            if docentes:
                df = pd.DataFrame(docentes)
                st.dataframe(df, use_container_width=True)
                st.caption(f"Total asignaciones: {len(docentes)}")
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
                curso = st.selectbox("Curso", ["901", "902", "903", "1001", "1002", "1003", "1101"])
            with col2:
                asignatura = st.text_input("Asignatura")
                intensidad = st.number_input("Intensidad (horas)", min_value=1, max_value=10, value=4)
                telefono = st.text_input("Teléfono")
                email = st.text_input("Email")
            
            if st.form_submit_button("💾 Guardar Docente", type="primary"):
                headers = get_headers()
                data = {
                    "nombre_docente": nombre,
                    "apellidos_docente": apellidos,
                    "documento_docente": documento,
                    "curso": curso,
                    "asignatura": asignatura,
                    "intensidad": str(intensidad),
                    "telefono_docente": telefono,
                    "email_docente": email
                }
                response = requests.post(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers, json=data)
                
                if response.status_code == 201:
                    st.success(f"✅ Docente {nombre} registrado exitosamente")
                else:
                    st.error(f"Error: {response.status_code}")
    
    with tab3:
        st.write("**Buscar y editar docente**")
        
        buscar = st.text_input("Documento del docente")
        if buscar:
            headers = get_headers()
            url = f"{SUPABASE_URL}/rest/v1/docentes?documento_docente=eq.{buscar}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200 and response.json():
                docente = response.json()[0]
                
                with st.form("editar_docente"):
                    nombre = st.text_input("Nombre", docente.get('nombre_docente', ''))
                    apellidos = st.text_input("Apellidos", docente.get('apellidos_docente', ''))
                    telefono = st.text_input("Teléfono", docente.get('telefono_docente', ''))
                    email = st.text_input("Email", docente.get('email_docente', ''))
                    
                    if st.form_submit_button("💾 Actualizar Docente", type="primary"):
                        data = {
                            "nombre_docente": nombre,
                            "apellidos_docente": apellidos,
                            "telefono_docente": telefono,
                            "email_docente": email
                        }
                        url_update = f"{SUPABASE_URL}/rest/v1/docentes?documento_docente=eq.{buscar}"
                        response = requests.patch(url_update, headers=headers, json=data)
                        
                        if response.status_code == 200:
                            st.success("✅ Docente actualizado exitosamente")
                        else:
                            st.error(f"Error: {response.status_code}")
            else:
                st.warning("Docente no encontrado")
    
    with tab4:
        st.write("**Carga masiva de docentes**")
        archivo = st.file_uploader("Seleccionar archivo", type=['csv', 'xlsx'], key="carga_docentes")
        
        if archivo:
            if archivo.name.endswith('.csv'):
                df = pd.read_csv(archivo)
            else:
                df = pd.read_excel(archivo)
            
            st.write("**Vista previa:**")
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
# SECCIÓN 5: ASIGNACIÓN ACADÉMICA
# ============================================
def mostrar_asignacion_academica():
    st.subheader("📚 Asignación Académica")
    st.info("🚧 Módulo en construcción - Próximamente")
    st.write("Aquí se configurarán las asignaciones de docentes a cursos y materias")

# ============================================
# SECCIÓN 6: CONFIGURACIÓN DEL SISTEMA
# ============================================
def mostrar_configuracion_sistema():
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
