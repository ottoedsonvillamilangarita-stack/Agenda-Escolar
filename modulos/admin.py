import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from utils import SUPABASE_URL, get_headers

def mostrar(data):
    st.title("🛡️ Panel de Administrador")
    st.write(f"Bienvenido, {data.get('username', 'Admin')}")
    
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
        if st.button("👨‍🎓 Estudiantes", use_container_width=True,
                     type="primary" if st.session_state.admin_seccion == "estudiantes" else "secondary"):
            st.session_state.admin_seccion = "estudiantes"
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
    elif st.session_state.admin_seccion == "estudiantes":
        gestion_estudiantes()
    elif st.session_state.admin_seccion == "acudientes":
        gestion_acudientes()
    elif st.session_state.admin_seccion == "docentes":
        gestion_docentes()
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
    
    try:
        response_est = requests.get(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers)
        total_estudiantes = len(response_est.json()) if response_est.status_code == 200 else 0
    except:
        total_estudiantes = 0
    
    try:
        response_doc = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
        if response_doc.status_code == 200:
            datos = response_doc.json()
            docentes_unicos = set([d.get('documento_docente') for d in datos])
            total_docentes = len(docentes_unicos)
        else:
            total_docentes = 0
    except:
        total_docentes = 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👨‍🎓 Estudiantes", total_estudiantes)
    col2.metric("👨‍🏫 Docentes", total_docentes)
    col3.metric("📚 Cursos", "7")
    col4.metric("📅 Año Lectivo", "2024")
    
    st.info("🔐 Panel de control del Administrador")


# ============================================
# GESTIÓN DE ESTUDIANTES
# ============================================

def gestion_estudiantes():
    st.subheader("👨‍🎓 Gestión de Estudiantes")
    
    headers = get_headers()
    
    tab1, tab2, tab3 = st.tabs(["📋 Lista de Estudiantes", "➕ Nuevo Estudiante", "✏️ Editar Estudiante"])
    
    with tab1:
        try:
            response = requests.get(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers)
            if response.status_code == 200:
                estudiantes = response.json()
                if estudiantes:
                    df = pd.DataFrame(estudiantes)
                    columnas = ['nombre_estudiante', 'apellidos_estudiante', 'documento_estudiante', 'curso']
                    columnas_existentes = [col for col in columnas if col in df.columns]
                    st.dataframe(df[columnas_existentes], use_container_width=True)
                    st.caption(f"Total: {len(estudiantes)} estudiantes")
                else:
                    st.info("No hay estudiantes registrados")
        except Exception as e:
            st.error(f"Error al cargar estudiantes: {str(e)}")
    
    with tab2:
        st.write("**Registrar nuevo estudiante**")
        
        with st.form("nuevo_estudiante", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                nombre = st.text_input("Nombre *")
                apellidos = st.text_input("Apellidos *")
                documento = st.text_input("Documento de identidad *")
                curso = st.selectbox("Curso *", ["901", "902", "903", "1001", "1002", "1003", "1101"])
                telefono = st.text_input("Teléfono")
                email = st.text_input("Email")
            
            with col2:
                nombre_acudiente = st.text_input("Nombre del acudiente *")
                documento_acudiente = st.text_input("Documento del acudiente *")
                parentesco = st.selectbox("Parentesco", ["", "Padre", "Madre", "Tío", "Tía", "Abuelo", "Abuela", "Otro"])
                telefono_acudiente = st.text_input("Teléfono del acudiente")
                email_acudiente = st.text_input("Email del acudiente")
            
            if st.form_submit_button("💾 Registrar Estudiante", type="primary"):
                if not all([nombre, apellidos, documento, curso, nombre_acudiente, documento_acudiente]):
                    st.error("❌ Completa todos los campos obligatorios (*)")
                else:
                    check_url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{documento}"
                    check_response = requests.get(check_url, headers=headers)
                    
                    if check_response.status_code == 200 and check_response.json():
                        st.error(f"❌ Ya existe un estudiante con el documento {documento}")
                    else:
                        data = {
                            "nombre_estudiante": nombre,
                            "apellidos_estudiante": apellidos,
                            "documento_estudiante": documento,
                            "curso": curso,
                            "telefono_estudiante": telefono,
                            "email_estudiante": email
                        }
                        response = requests.post(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers, json=data)
                        
                        if response.status_code == 201:
                            # Crear usuario para el estudiante
                            user_data = {
                                "username": documento,
                                "password_hash": "demo2026",
                                "rol": "estudiante",
                                "documento": documento,
                                "roles": ["estudiante"]
                            }
                            requests.post(f"{SUPABASE_URL}/rest/v1/usuarios_login", headers=headers, json=user_data)
                            
                            # Crear acudiente
                            acud_data = {
                                "documento_estudiante": documento,
                                "documento_acudiente": documento_acudiente,
                                "nombre_acudiente": nombre_acudiente,
                                "parentesco": parentesco,
                                "telefono_acudiente": telefono_acudiente,
                                "email_acudiente": email_acudiente,
                                "es_principal": True
                            }
                            requests.post(f"{SUPABASE_URL}/rest/v1/estudiante_acudiente", headers=headers, json=acud_data)
                            
                            # Crear usuario para el acudiente
                            user_acud = {
                                "username": documento_acudiente,
                                "password_hash": "demo2026",
                                "rol": "acudiente",
                                "documento": documento_acudiente,
                                "roles": ["acudiente"]
                            }
                            requests.post(f"{SUPABASE_URL}/rest/v1/usuarios_login", headers=headers, json=user_acud)
                            
                            st.success(f"✅ Estudiante {nombre} {apellidos} registrado")
                            st.balloons()
                        else:
                            st.error(f"Error al registrar: {response.status_code}")
    
    with tab3:
        st.write("**Editar estudiante existente**")
        
        documento_buscar = st.text_input("Documento de identidad del estudiante", key="buscar_estudiante_editar")
        
        if documento_buscar:
            with st.spinner("Buscando estudiante..."):
                url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{documento_buscar}"
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200 and response.json():
                    estudiante = response.json()[0]
                    
                    with st.form("editar_estudiante_form"):
                        st.success(f"Editando: {estudiante.get('nombre_estudiante', '')} {estudiante.get('apellidos_estudiante', '')}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            nombre = st.text_input("Nombre", value=estudiante.get('nombre_estudiante', ''))
                            apellidos = st.text_input("Apellidos", value=estudiante.get('apellidos_estudiante', ''))
                            curso = st.selectbox("Curso", ["901", "902", "903", "1001", "1002", "1003", "1101"], 
                                                index=["901","902","903","1001","1002","1003","1101"].index(estudiante.get('curso', '901')))
                        with col2:
                            telefono = st.text_input("Teléfono", value=estudiante.get('telefono_estudiante', ''))
                            email = st.text_input("Email", value=estudiante.get('email_estudiante', ''))
                        
                        if st.form_submit_button("💾 Guardar Cambios", type="primary"):
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
                                st.success("✅ Estudiante actualizado exitosamente")
                                st.rerun()
                            else:
                                st.error(f"Error al actualizar: {response_update.status_code}")
                elif response.status_code == 200:
                    st.warning("No se encontró un estudiante con ese documento")


# ============================================
# GESTIÓN DE ACUDIENTES
# ============================================

def gestion_acudientes():
    st.subheader("👨‍👩‍👧 Gestión de Acudientes")
    
    headers = get_headers()
    
    tab1, tab2 = st.tabs(["📋 Lista de Acudientes", "✏️ Editar Acudiente"])
    
    with tab1:
        try:
            response = requests.get(f"{SUPABASE_URL}/rest/v1/estudiante_acudiente", headers=headers)
            if response.status_code == 200:
                acudientes_rel = response.json()
                acudientes_dict = {}
                
                for rel in acudientes_rel:
                    doc_acud = rel.get('documento_acudiente')
                    if doc_acud and doc_acud not in acudientes_dict:
                        acudientes_dict[doc_acud] = {
                            "nombre": rel.get('nombre_acudiente'),
                            "documento": doc_acud,
                            "telefono": rel.get('telefono_acudiente'),
                            "email": rel.get('email_acudiente'),
                            "hijos": []
                        }
                    if doc_acud:
                        hijo_url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{rel.get('documento_estudiante')}"
                        hijo_resp = requests.get(hijo_url, headers=headers)
                        if hijo_resp.status_code == 200 and hijo_resp.json():
                            nombre_hijo = hijo_resp.json()[0].get('nombre_estudiante')
                            acudientes_dict[doc_acud]["hijos"].append(nombre_hijo)
                
                if acudientes_dict:
                    df = pd.DataFrame([{
                        "Nombre": v["nombre"],
                        "Documento": v["documento"],
                        "Teléfono": v["telefono"],
                        "Email": v["email"],
                        "Hijos": ", ".join(v["hijos"])
                    } for v in acudientes_dict.values()])
                    st.dataframe(df, use_container_width=True)
                    st.caption(f"Total: {len(acudientes_dict)} acudientes")
                else:
                    st.info("No hay acudientes registrados")
        except Exception as e:
            st.error(f"Error al cargar acudientes: {str(e)}")
    
    with tab2:
        st.write("**Editar acudiente**")
        st.info("Para editar un acudiente, busca al estudiante asociado y edita desde la sección de Estudiantes")


# ============================================
# GESTIÓN DE DOCENTES
# ============================================

def gestion_docentes():
    st.subheader("👨‍🏫 Gestión de Docentes")
    
    headers = get_headers()
    
    tab1, tab2, tab3 = st.tabs(["📋 Lista de Docentes", "➕ Nuevo Docente", "✏️ Editar Docente"])
    
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
        except:
            st.error("Error al cargar docentes")
    
    with tab2:
        st.write("**Registrar nuevo docente**")
        
        with st.form("nuevo_docente", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                nombre = st.text_input("Nombre *")
                apellidos = st.text_input("Apellidos *")
                documento = st.text_input("Documento de identidad *")
                telefono = st.text_input("Teléfono")
                email = st.text_input("Email")
            
            with col2:
                titulo = st.text_input("Título profesional")
                especializacion = st.text_input("Especialización")
                tipo_contrato = st.selectbox("Tipo de contrato", ["", "Planta", "Contrato", "Cátedra"])
                fecha_ingreso = st.date_input("Fecha de ingreso", value=None)
            
            if st.form_submit_button("💾 Registrar Docente", type="primary"):
                if not all([nombre, apellidos, documento]):
                    st.error("❌ Completa todos los campos obligatorios (*)")
                else:
                    check_url = f"{SUPABASE_URL}/rest/v1/docentes?documento_docente=eq.{documento}"
                    check_response = requests.get(check_url, headers=headers)
                    
                    if check_response.status_code == 200 and check_response.json():
                        st.error(f"❌ Ya existe un docente con el documento {documento}")
                    else:
                        data = {
                            "nombre_docente": nombre,
                            "apellidos_docente": apellidos,
                            "documento_docente": documento,
                            "telefono_docente": telefono,
                            "email_docente": email,
                            "titulo": titulo,
                            "especializacion": especializacion,
                            "tipo_contrato": tipo_contrato,
                            "fecha_ingreso": str(fecha_ingreso) if fecha_ingreso else None
                        }
                        response = requests.post(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers, json=data)
                        
                        if response.status_code == 201:
                            username = nombre.lower().replace(" ", "_")
                            user_data = {
                                "username": username,
                                "password_hash": "demo2026",
                                "rol": "docente",
                                "documento": documento,
                                "roles": ["docente"]
                            }
                            requests.post(f"{SUPABASE_URL}/rest/v1/usuarios_login", headers=headers, json=user_data)
                            
                            st.success(f"✅ Docente {nombre} {apellidos} registrado")
                            st.balloons()
                        else:
                            st.error(f"Error al registrar: {response.status_code}")
    
    with tab3:
        st.write("**Editar docente existente**")
        
        documento_buscar = st.text_input("Documento de identidad del docente", key="buscar_docente_editar")
        
        if documento_buscar:
            url = f"{SUPABASE_URL}/rest/v1/docentes?documento_docente=eq.{documento_buscar}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200 and response.json():
                docente = response.json()[0]
                
                with st.form("editar_docente", clear_on_submit=False):
                    st.success(f"Editando: {docente.get('nombre_docente', '')} {docente.get('apellidos_docente', '')}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        nombre = st.text_input("Nombre", value=docente.get('nombre_docente', ''))
                        apellidos = st.text_input("Apellidos", value=docente.get('apellidos_docente', ''))
                        st.text_input("Documento", value=docente.get('documento_docente', ''), disabled=True)
                        telefono = st.text_input("Teléfono", value=docente.get('telefono_docente', ''))
                        email = st.text_input("Email", value=docente.get('email_docente', ''))
                    
                    with col2:
                        titulo = st.text_input("Título", value=docente.get('titulo', ''))
                        especializacion = st.text_input("Especialización", value=docente.get('especializacion', ''))
                        tipo_contrato = st.selectbox("Tipo de contrato", ["", "Planta", "Contrato", "Cátedra"],
                                                    index=["", "Planta", "Contrato", "Cátedra"].index(docente.get('tipo_contrato', '')))
                        fecha_ingreso = st.date_input("Fecha de ingreso", value=datetime.strptime(docente.get('fecha_ingreso', '2024-01-01'), '%Y-%m-%d') if docente.get('fecha_ingreso') else None)
                    
                    if st.form_submit_button("💾 Guardar Cambios", type="primary"):
                        data_update = {
                            "nombre_docente": nombre,
                            "apellidos_docente": apellidos,
                            "telefono_docente": telefono,
                            "email_docente": email,
                            "titulo": titulo,
                            "especializacion": especializacion,
                            "tipo_contrato": tipo_contrato,
                            "fecha_ingreso": str(fecha_ingreso) if fecha_ingreso else None
                        }
                        
                        update_url = f"{SUPABASE_URL}/rest/v1/docentes?documento_docente=eq.{documento_buscar}"
                        response_update = requests.patch(update_url, headers=headers, json=data_update)
                        
                        if response_update.status_code == 200:
                            st.success("✅ Docente actualizado exitosamente")
                            st.rerun()
                        else:
                            st.error(f"Error al actualizar: {response_update.status_code}")
            elif response.status_code == 200:
                st.warning("No se encontró un docente con ese documento")


# ============================================
# ASIGNACIÓN ACADÉMICA
# ============================================

def mostrar_asignacion():
    st.subheader("📚 Asignación Académica")
    st.info("🚧 Módulo en construcción - Próximamente")


# ============================================
# SISTEMA
# ============================================

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
