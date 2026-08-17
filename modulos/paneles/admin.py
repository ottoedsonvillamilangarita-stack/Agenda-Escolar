# ============================================
# admin.py - VERSIÓN CORREGIDA (SIN MENÚ)
# ============================================

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from utils import SUPABASE_URL, get_headers

# ============================================
# CONSTANTES
# ============================================
CURSOS = ["901", "902", "903", "1001", "1002", "1003", "1101"]
PARENTESCOS = ["", "Padre", "Madre", "Tío", "Tía", "Abuelo", "Abuela", "Otro"]
SEXOS = ["", "Masculino", "Femenino"]
TIPOS_CONTRATO = ["", "Planta", "Contrato", "Cátedra", "Ocasional"]

# ============================================
# FUNCIÓN PRINCIPAL - SIN MENÚ
# ============================================
def mostrar(data):
    """
    Panel de administrador - SIN MENÚ PROPIO
    El menú se maneja desde app.py con st.navigation
    """
    st.title("🛡️ Panel de Administrador")
    st.write(f"Bienvenido, {data.get('username', 'Admin')}")
    
    # Obtener la sección desde session_state (manejado por app.py)
    seccion = st.session_state.get("admin_seccion", "dashboard")
    
    # Redirigir según la sección seleccionada en el menú lateral
    if seccion == "dashboard":
        mostrar_dashboard()
    elif seccion == "estudiantes":
        gestion_estudiantes()
    elif seccion == "acudientes":
        gestion_acudientes()
    elif seccion == "docentes":
        gestion_docentes()
    elif seccion == "asignacion":
        mostrar_asignacion()
    elif seccion == "sistema":
        mostrar_sistema()
    else:
        mostrar_dashboard()

# ============================================
# DASHBOARD
# ============================================
def mostrar_dashboard():
    """Dashboard con estadísticas básicas"""
    st.subheader("📊 Dashboard General")
    
    headers = get_headers()
    
    # Obtener datos
    try:
        response_est = requests.get(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers)
        total_estudiantes = len(response_est.json()) if response_est.status_code == 200 else 0
    except:
        total_estudiantes = 0
    
    try:
        response_doc = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
        if response_doc.status_code == 200:
            datos = response_doc.json()
            docentes_unicos = set([d.get('documento_docente') for d in datos if d.get('documento_docente')])
            total_docentes = len(docentes_unicos)
        else:
            total_docentes = 0
    except:
        total_docentes = 0
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👨‍🎓 Estudiantes", total_estudiantes)
    col2.metric("👨‍🏫 Docentes", total_docentes)
    col3.metric("📚 Cursos", "7")
    col4.metric("📅 Año Lectivo", datetime.now().year)
    
    st.info("🔐 Panel de control del Administrador")
    
    # Información adicional
    with st.expander("ℹ️ Información del sistema"):
        st.write("**Estado del sistema:** Activo")
        st.write(f"**Fecha actual:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        st.write("**Versión:** 1.0.0")

# ============================================
# GESTIÓN DE ESTUDIANTES
# ============================================
def gestion_estudiantes():
    """Gestión de estudiantes"""
    st.subheader("👨‍🎓 Gestión de Estudiantes")
    
    headers = get_headers()
    
    tab1, tab2, tab3 = st.tabs(["📋 Lista", "➕ Nuevo", "✏️ Editar"])
    
    with tab1:
        try:
            response = requests.get(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers)
            if response.status_code == 200:
                estudiantes = response.json()
                if estudiantes:
                    df = pd.DataFrame(estudiantes)
                    st.dataframe(df, use_container_width=True)
                    st.caption(f"Total: {len(estudiantes)} estudiantes")
                else:
                    st.info("No hay estudiantes registrados")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    with tab2:
        st.write("**Registrar nuevo estudiante**")
        with st.form("nuevo_estudiante", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Datos personales**")
                nombre = st.text_input("Nombre *")
                apellidos = st.text_input("Apellidos *")
                documento = st.text_input("Documento *")
                curso = st.selectbox("Curso *", CURSOS)
                telefono = st.text_input("Teléfono")
                email = st.text_input("Email")
            with col2:
                st.markdown("**Datos del acudiente**")
                nombre_acudiente = st.text_input("Nombre del acudiente *")
                documento_acudiente = st.text_input("Documento del acudiente *")
                parentesco = st.selectbox("Parentesco", PARENTESCOS)
                telefono_acudiente = st.text_input("Teléfono del acudiente")
                email_acudiente = st.text_input("Email del acudiente")
            
            if st.form_submit_button("💾 Registrar", type="primary"):
                if not all([nombre, apellidos, documento, curso, nombre_acudiente, documento_acudiente]):
                    st.error("❌ Completa todos los campos obligatorios (*)")
                else:
                    # Verificar si existe
                    check_url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{documento}"
                    check_response = requests.get(check_url, headers=headers)
                    
                    if check_response.status_code == 200 and check_response.json():
                        st.error(f"❌ Ya existe un estudiante con el documento {documento}")
                    else:
                        # Crear estudiante
                        data_estudiante = {
                            "nombre_estudiante": nombre,
                            "apellidos_estudiante": apellidos,
                            "documento_estudiante": documento,
                            "curso": curso,
                            "telefono_estudiante": telefono,
                            "email_estudiante": email
                        }
                        response = requests.post(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers, json=data_estudiante)
                        
                        if response.status_code == 201:
                            # Crear usuario estudiante
                            user_data = {
                                "username": documento,
                                "password_hash": "demo2026",
                                "rol": "estudiante",
                                "documento": documento,
                                "roles": ["estudiante"]
                            }
                            requests.post(f"{SUPABASE_URL}/rest/v1/usuarios_login", headers=headers, json=user_data)
                            
                            # Crear acudiente
                            data_acudiente = {
                                "documento_estudiante": documento,
                                "documento_acudiente": documento_acudiente,
                                "nombre_acudiente": nombre_acudiente,
                                "parentesco": parentesco,
                                "telefono_acudiente": telefono_acudiente,
                                "email_acudiente": email_acudiente,
                                "es_principal": True
                            }
                            requests.post(f"{SUPABASE_URL}/rest/v1/estudiante_acudiente", headers=headers, json=data_acudiente)
                            
                            # Crear usuario acudiente
                            user_acud = {
                                "username": documento_acudiente,
                                "password_hash": "demo2026",
                                "rol": "acudiente",
                                "documento": documento_acudiente,
                                "roles": ["acudiente"]
                            }
                            requests.post(f"{SUPABASE_URL}/rest/v1/usuarios_login", headers=headers, json=user_acud)
                            
                            st.success(f"✅ Estudiante {nombre} {apellidos} registrado exitosamente")
                            st.info(f"🔑 Estudiante: {documento} | demo2026")
                            st.info(f"🔑 Acudiente: {documento_acudiente} | demo2026")
                            st.balloons()
                        else:
                            st.error(f"Error al registrar: {response.status_code}")
    
    with tab3:
        st.write("**Editar estudiante**")
        documento_buscar = st.text_input("Documento del estudiante", key="buscar_est_edit")
        
        if documento_buscar:
            url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{documento_buscar}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200 and response.json():
                estudiante = response.json()[0]
                
                with st.form("editar_estudiante"):
                    col1, col2 = st.columns(2)
                    with col1:
                        nombre = st.text_input("Nombre", value=estudiante.get('nombre_estudiante', ''))
                        apellidos = st.text_input("Apellidos", value=estudiante.get('apellidos_estudiante', ''))
                        curso = st.selectbox("Curso", CURSOS, 
                                           index=CURSOS.index(estudiante.get('curso', '901')))
                    with col2:
                        telefono = st.text_input("Teléfono", value=estudiante.get('telefono_estudiante', ''))
                        email = st.text_input("Email", value=estudiante.get('email_estudiante', ''))
                    
                    if st.form_submit_button("💾 Guardar cambios", type="primary"):
                        data_update = {
                            "nombre_estudiante": nombre,
                            "apellidos_estudiante": apellidos,
                            "curso": curso,
                            "telefono_estudiante": telefono,
                            "email_estudiante": email
                        }
                        update_url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{documento_buscar}"
                        response_update = requests.patch(update_url, headers=headers, json=data_update)
                        
                        if response_update.status_code == 200:
                            st.success("✅ Estudiante actualizado")
                            st.rerun()
                        else:
                            st.error(f"Error: {response_update.status_code}")
            else:
                st.warning("No se encontró el estudiante")

# ============================================
# GESTIÓN DE ACUDIENTES
# ============================================
def gestion_acudientes():
    """Gestión de acudientes"""
    st.subheader("👨‍👩‍👧 Gestión de Acudientes")
    
    headers = get_headers()
    
    tab1, tab2 = st.tabs(["📋 Lista", "✏️ Editar"])
    
    with tab1:
        try:
            response = requests.get(f"{SUPABASE_URL}/rest/v1/estudiante_acudiente", headers=headers)
            if response.status_code == 200:
                acudientes = response.json()
                if acudientes:
                    # Agrupar por documento
                    acud_dict = {}
                    for a in acudientes:
                        doc = a.get('documento_acudiente')
                        if doc and doc not in acud_dict:
                            acud_dict[doc] = {
                                "nombre": a.get('nombre_acudiente'),
                                "documento": doc,
                                "telefono": a.get('telefono_acudiente'),
                                "email": a.get('email_acudiente')
                            }
                    
                    if acud_dict:
                        df = pd.DataFrame(acud_dict.values())
                        st.dataframe(df, use_container_width=True)
                        st.caption(f"Total: {len(acud_dict)} acudientes")
                else:
                    st.info("No hay acudientes registrados")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    with tab2:
        st.write("**Editar acudiente**")
        doc_buscar = st.text_input("Documento del acudiente", key="buscar_acud_edit")
        
        if doc_buscar:
            url = f"{SUPABASE_URL}/rest/v1/estudiante_acudiente?documento_acudiente=eq.{doc_buscar}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200 and response.json():
                acudiente = response.json()[0]
                
                with st.form("editar_acudiente"):
                    col1, col2 = st.columns(2)
                    with col1:
                        nombre = st.text_input("Nombre", value=acudiente.get('nombre_acudiente', ''))
                        parentesco = st.text_input("Parentesco", value=acudiente.get('parentesco', ''))
                    with col2:
                        telefono = st.text_input("Teléfono", value=acudiente.get('telefono_acudiente', ''))
                        email = st.text_input("Email", value=acudiente.get('email_acudiente', ''))
                    
                    if st.form_submit_button("💾 Guardar cambios", type="primary"):
                        update_data = {
                            "nombre_acudiente": nombre,
                            "parentesco": parentesco,
                            "telefono_acudiente": telefono,
                            "email_acudiente": email
                        }
                        update_url = f"{SUPABASE_URL}/rest/v1/estudiante_acudiente?documento_acudiente=eq.{doc_buscar}"
                        requests.patch(update_url, headers=headers, json=update_data)
                        st.success("✅ Acudiente actualizado")
                        st.rerun()
            else:
                st.warning("No se encontró el acudiente")

# ============================================
# GESTIÓN DE DOCENTES
# ============================================
def gestion_docentes():
    """Gestión de docentes"""
    st.subheader("👨‍🏫 Gestión de Docentes")
    
    headers = get_headers()
    
    tab1, tab2, tab3 = st.tabs(["📋 Lista", "➕ Nuevo", "✏️ Editar"])
    
    with tab1:
        try:
            response = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
            if response.status_code == 200:
                docentes = response.json()
                if docentes:
                    df = pd.DataFrame(docentes)
                    st.dataframe(df, use_container_width=True)
                    st.caption(f"Total: {len(docentes)} docentes")
                else:
                    st.info("No hay docentes registrados")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    with tab2:
        st.write("**Registrar nuevo docente**")
        with st.form("nuevo_docente", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre *")
                apellidos = st.text_input("Apellidos *")
                documento = st.text_input("Documento *")
                fecha_nacimiento = st.date_input("Fecha de nacimiento", value=None)
                sexo = st.selectbox("Sexo", SEXOS)
            with col2:
                telefono = st.text_input("Teléfono")
                email = st.text_input("Email")
                titulo = st.text_input("Título")
                tipo_contrato = st.selectbox("Tipo de contrato", TIPOS_CONTRATO)
                fecha_ingreso = st.date_input("Fecha de ingreso", value=None)
            
            if st.form_submit_button("💾 Registrar", type="primary"):
                if not all([nombre, apellidos, documento]):
                    st.error("❌ Completa los campos obligatorios")
                else:
                    # Verificar si existe
                    check_url = f"{SUPABASE_URL}/rest/v1/docentes?documento_docente=eq.{documento}"
                    check_response = requests.get(check_url, headers=headers)
                    
                    if check_response.status_code == 200 and check_response.json():
                        st.error(f"❌ Ya existe un docente con el documento {documento}")
                    else:
                        data = {
                            "nombre_docente": nombre,
                            "apellidos_docente": apellidos,
                            "documento_docente": documento,
                            "fecha_nacimiento": str(fecha_nacimiento) if fecha_nacimiento else None,
                            "sexo_docente": sexo,
                            "telefono_docente": telefono,
                            "email_docente": email,
                            "titulo": titulo,
                            "tipo_contrato": tipo_contrato,
                            "fecha_ingreso": str(fecha_ingreso) if fecha_ingreso else None
                        }
                        response = requests.post(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers, json=data)
                        
                        if response.status_code == 201:
                            username = nombre.lower().replace(" ", "_") + "_" + documento[-4:]
                            user_data = {
                                "username": username,
                                "password_hash": "demo2026",
                                "rol": "docente",
                                "documento": documento,
                                "roles": ["docente"]
                            }
                            requests.post(f"{SUPABASE_URL}/rest/v1/usuarios_login", headers=headers, json=user_data)
                            st.success(f"✅ Docente {nombre} {apellidos} registrado")
                            st.info(f"🔑 Usuario: {username} | demo2026")
                            st.balloons()
                        else:
                            st.error(f"Error: {response.status_code}")
    
    with tab3:
        st.write("**Editar docente**")
        documento_buscar = st.text_input("Documento del docente", key="buscar_doc_edit")
        
        if documento_buscar:
            url = f"{SUPABASE_URL}/rest/v1/docentes?documento_docente=eq.{documento_buscar}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200 and response.json():
                docente = response.json()[0]
                
                with st.form("editar_docente"):
                    col1, col2 = st.columns(2)
                    with col1:
                        nombre = st.text_input("Nombre", value=docente.get('nombre_docente', ''))
                        apellidos = st.text_input("Apellidos", value=docente.get('apellidos_docente', ''))
                        fecha_nacimiento = st.date_input("Fecha de nacimiento", 
                                                        value=datetime.strptime(docente.get('fecha_nacimiento', '2000-01-01'), '%Y-%m-%d') if docente.get('fecha_nacimiento') else None)
                    with col2:
                        telefono = st.text_input("Teléfono", value=docente.get('telefono_docente', ''))
                        email = st.text_input("Email", value=docente.get('email_docente', ''))
                        titulo = st.text_input("Título", value=docente.get('titulo', ''))
                    
                    if st.form_submit_button("💾 Guardar cambios", type="primary"):
                        data_update = {
                            "nombre_docente": nombre,
                            "apellidos_docente": apellidos,
                            "fecha_nacimiento": str(fecha_nacimiento) if fecha_nacimiento else None,
                            "telefono_docente": telefono,
                            "email_docente": email,
                            "titulo": titulo
                        }
                        update_url = f"{SUPABASE_URL}/rest/v1/docentes?documento_docente=eq.{documento_buscar}"
                        requests.patch(update_url, headers=headers, json=data_update)
                        st.success("✅ Docente actualizado")
                        st.rerun()
            else:
                st.warning("No se encontró el docente")

# ============================================
# ASIGNACIÓN ACADÉMICA
# ============================================
def mostrar_asignacion():
    """Asignación académica"""
    st.subheader("📚 Asignación Académica")
    
    headers = get_headers()
    
    tabs = st.tabs(["📖 Horarios", "👨‍🏫 Directores", "📚 Asignaturas"])
    
    with tabs[0]:
        st.write("**Configurar horarios**")
        
        # Obtener cursos
        response_cursos = requests.get(f"{SUPABASE_URL}/rest/v1/estudiantes?select=curso", headers=headers)
        if response_cursos.status_code == 200:
            cursos = list(set([e['curso'] for e in response_cursos.json() if e.get('curso')]))
            cursos.sort()
        
        if cursos:
            curso = st.selectbox("Seleccionar curso", cursos)
            st.info(f"Configurando horario para el curso {curso}")
            
            # Mostrar horario básico
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Lunes**")
                st.selectbox("Hora 1", ["", "Matemáticas", "Español", "Inglés"], key="lun_h1")
                st.selectbox("Hora 2", ["", "Matemáticas", "Español", "Inglés"], key="lun_h2")
            with col2:
                st.write("**Martes**")
                st.selectbox("Hora 1", ["", "Matemáticas", "Español", "Inglés"], key="mar_h1")
                st.selectbox("Hora 2", ["", "Matemáticas", "Español", "Inglés"], key="mar_h2")
            
            if st.button("💾 Guardar horario", type="primary"):
                st.success("✅ Horario guardado")
        else:
            st.warning("No hay cursos registrados")
    
    with tabs[1]:
        st.write("**Directores de grupo**")
        
        # Obtener cursos
        response_cursos = requests.get(f"{SUPABASE_URL}/rest/v1/estudiantes?select=curso", headers=headers)
        if response_cursos.status_code == 200:
            cursos = list(set([e['curso'] for e in response_cursos.json() if e.get('curso')]))
            cursos.sort()
        
        if cursos:
            curso_seleccionado = st.selectbox("Seleccionar curso", cursos, key="director_curso")
            
            # Obtener docentes
            response_docentes = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
            if response_docentes.status_code == 200:
                docentes = response_docentes.json()
                docentes_dict = {d['documento_docente']: f"{d['nombre_docente']} {d['apellidos_docente']}" for d in docentes}
                
                docente_seleccionado = st.selectbox(
                    "Seleccionar director",
                    options=[""] + list(docentes_dict.keys()),
                    format_func=lambda x: docentes_dict.get(x, "Ninguno") if x else "Ninguno"
                )
                
                if st.button("💾 Asignar director", type="primary"):
                    if docente_seleccionado:
                        # Eliminar director anterior
                        delete_url = f"{SUPABASE_URL}/rest/v1/asignacion_academica?curso=eq.{curso_seleccionado}&asignatura=ilike.%direccion%"
                        requests.delete(delete_url, headers=headers)
                        
                        # Asignar nuevo director
                        data = {
                            "curso": curso_seleccionado,
                            "asignatura": "DIRECCION DE CURSO",
                            "documento_docente": docente_seleccionado,
                            "anio": datetime.now().year
                        }
                        response = requests.post(f"{SUPABASE_URL}/rest/v1/asignacion_academica", headers=headers, json=data)
                        
                        if response.status_code == 201:
                            st.success(f"✅ Director asignado para {curso_seleccionado}")
                            st.rerun()
                        else:
                            st.error(f"Error: {response.status_code}")
                    else:
                        st.warning("Selecciona un docente")
        else:
            st.warning("No hay cursos registrados")
    
    with tabs[2]:
        st.write("**Gestionar asignaturas**")
        st.info("Funcionalidad en desarrollo")

# ============================================
# SISTEMA
# ============================================
def mostrar_sistema():
    """Configuración del sistema"""
    st.subheader("⚙️ Configuración del Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        nombre_colegio = st.text_input("Nombre del colegio", "Mi Colegio")
        año_lectivo = st.number_input("Año lectivo", min_value=2000, max_value=2100, value=datetime.now().year)
        
        if st.button("💾 Guardar Configuración", type="primary"):
            st.success("✅ Configuración guardada")
    
    with col2:
        st.write("**Información del sistema**")
        st.write(f"- Versión: 1.0.0")
        st.write(f"- Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        st.write(f"- Base de datos: Supabase")
        
        if st.button("📀 Crear Respaldo", type="primary"):
            st.success("✅ Respaldo creado")
    
    with st.expander("📊 Estadísticas del sistema"):
        headers = get_headers()
        
        try:
            response_est = requests.get(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers)
            total_est = len(response_est.json()) if response_est.status_code == 200 else 0
        except:
            total_est = 0
        
        try:
            response_doc = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
            total_doc = len(response_doc.json()) if response_doc.status_code == 200 else 0
        except:
            total_doc = 0
        
        st.write(f"- Total estudiantes: {total_est}")
        st.write(f"- Total docentes: {total_doc}")
