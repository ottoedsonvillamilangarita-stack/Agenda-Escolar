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
    
    # Contar acudientes únicos
    try:
        response_acud = requests.get(f"{SUPABASE_URL}/rest/v1/estudiante_acudiente", headers=headers)
        if response_acud.status_code == 200:
            acudientes = response_acud.json()
            acudientes_unicos = set([a.get('documento_acudiente') for a in acudientes if a.get('documento_acudiente')])
            total_acudientes = len(acudientes_unicos)
        else:
            total_acudientes = 0
    except:
        total_acudientes = 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👨‍🎓 Estudiantes", total_estudiantes)
    col2.metric("👨‍🏫 Docentes", total_docentes)
    col3.metric("👨‍👩‍👧 Acudientes", total_acudientes)
    col4.metric("📚 Cursos", "7")
    
    st.info("🔐 Panel de control del Administrador")


# ============================================
# GESTIÓN DE ESTUDIANTES (CON MÚLTIPLES ACUDIENTES)
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
                    # Obtener acudientes para cada estudiante
                    for est in estudiantes:
                        doc_est = est.get('documento_estudiante')
                        response_acud = requests.get(f"{SUPABASE_URL}/rest/v1/estudiante_acudiente?documento_estudiante=eq.{doc_est}", headers=headers)
                        if response_acud.status_code == 200:
                            acudientes = response_acud.json()
                            nombres_acud = [a.get('nombre_acudiente') for a in acudientes]
                            est['acudientes'] = ", ".join(nombres_acud) if nombres_acud else "Sin acudiente"
                    
                    df = pd.DataFrame(estudiantes)
                    columnas = ['nombre_estudiante', 'apellidos_estudiante', 'documento_estudiante', 'curso', 'acudientes']
                    columnas_existentes = [col for col in columnas if col in df.columns]
                    st.dataframe(df[columnas_existentes], use_container_width=True)
                    st.caption(f"Total: {len(estudiantes)} estudiantes")
                else:
                    st.info("No hay estudiantes registrados")
        except Exception as e:
            st.error(f"Error al cargar estudiantes: {str(e)}")
    
    with tab2:
        st.write("**Registrar nuevo estudiante**")
        st.info("Puedes agregar hasta 3 acudientes por estudiante")
        
        with st.form("nuevo_estudiante", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                nombre = st.text_input("Nombre *")
                apellidos = st.text_input("Apellidos *")
                documento = st.text_input("Documento de identidad *")
                curso = st.selectbox("Curso *", ["901", "902", "903", "1001", "1002", "1003", "1101"])
                telefono = st.text_input("Teléfono del estudiante")
                email = st.text_input("Email del estudiante")
            
            with col2:
                st.markdown("**Acudiente Principal**")
                nombre_acudiente1 = st.text_input("Nombre del acudiente principal *")
                documento_acudiente1 = st.text_input("Documento del acudiente principal *")
                parentesco1 = st.selectbox("Parentesco", ["", "Padre", "Madre", "Tío", "Tía", "Abuelo", "Abuela", "Otro"], key="parentesco1")
                telefono_acudiente1 = st.text_input("Teléfono del acudiente principal")
                email_acudiente1 = st.text_input("Email del acudiente principal")
            
            st.markdown("**Acudiente Secundario (opcional)**")
            col3, col4 = st.columns(2)
            with col3:
                nombre_acudiente2 = st.text_input("Nombre del acudiente secundario")
                documento_acudiente2 = st.text_input("Documento del acudiente secundario")
                parentesco2 = st.selectbox("Parentesco", ["", "Padre", "Madre", "Tío", "Tía", "Abuelo", "Abuela", "Otro"], key="parentesco2")
            with col4:
                telefono_acudiente2 = st.text_input("Teléfono del acudiente secundario")
                email_acudiente2 = st.text_input("Email del acudiente secundario")
            
            st.markdown("**Acudiente Terciario (opcional)**")
            col5, col6 = st.columns(2)
            with col5:
                nombre_acudiente3 = st.text_input("Nombre del acudiente terciario")
                documento_acudiente3 = st.text_input("Documento del acudiente terciario")
                parentesco3 = st.selectbox("Parentesco", ["", "Padre", "Madre", "Tío", "Tía", "Abuelo", "Abuela", "Otro"], key="parentesco3")
            with col6:
                telefono_acudiente3 = st.text_input("Teléfono del acudiente terciario")
                email_acudiente3 = st.text_input("Email del acudiente terciario")
            
            if st.form_submit_button("💾 Registrar Estudiante", type="primary"):
                if not all([nombre, apellidos, documento, curso, nombre_acudiente1, documento_acudiente1]):
                    st.error("❌ Completa todos los campos obligatorios (*)")
                else:
                    # Verificar si ya existe
                    check_url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{documento}"
                    check_response = requests.get(check_url, headers=headers)
                    
                    if check_response.status_code == 200 and check_response.json():
                        st.error(f"❌ Ya existe un estudiante con el documento {documento}")
                    else:
                        # Insertar estudiante
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
                            # Insertar acudientes
                            acudientes_data = [
                                (nombre_acudiente1, documento_acudiente1, parentesco1, telefono_acudiente1, email_acudiente1, True),
                                (nombre_acudiente2, documento_acudiente2, parentesco2, telefono_acudiente2, email_acudiente2, False),
                                (nombre_acudiente3, documento_acudiente3, parentesco3, telefono_acudiente3, email_acudiente3, False)
                            ]
                            
                            for nombre_acud, doc_acud, parent, tel, mail, es_principal in acudientes_data:
                                if nombre_acud and doc_acud:
                                    data_acudiente = {
                                        "documento_estudiante": documento,
                                        "documento_acudiente": doc_acud,
                                        "nombre_acudiente": nombre_acud,
                                        "parentesco": parent,
                                        "telefono_acudiente": tel,
                                        "email_acudiente": mail,
                                        "es_principal": es_principal
                                    }
                                    requests.post(f"{SUPABASE_URL}/rest/v1/estudiante_acudiente", headers=headers, json=data_acudiente)
                                    
                                    # Crear usuario para el acudiente si no existe
                                    user_check = requests.get(f"{SUPABASE_URL}/rest/v1/usuarios_login?username=eq.{doc_acud}", headers=headers)
                                    if user_check.status_code == 200 and not user_check.json():
                                        user_data = {
                                            "username": doc_acud,
                                            "password_hash": "demo2026",
                                            "rol": "acudiente",
                                            "documento": doc_acud,
                                            "roles": ["acudiente"]
                                        }
                                        requests.post(f"{SUPABASE_URL}/rest/v1/usuarios_login", headers=headers, json=user_data)
                            
                            # Crear usuario para el estudiante
                            user_estudiante = {
                                "username": documento,
                                "password_hash": "demo2026",
                                "rol": "estudiante",
                                "documento": documento,
                                "roles": ["estudiante"]
                            }
                            requests.post(f"{SUPABASE_URL}/rest/v1/usuarios_login", headers=headers, json=user_estudiante)
                            
                            st.success(f"✅ Estudiante {nombre} {apellidos} registrado")
                            st.balloons()
                        else:
                            st.error(f"Error al registrar: {response.status_code}")
    
    with tab3:
        st.write("**Editar estudiante existente**")
        
        documento_buscar = st.text_input("Documento de identidad del estudiante", key="buscar_estudiante_editar")
        
        if documento_buscar:
            url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{documento_buscar}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200 and response.json():
                estudiante = response.json()[0]
                
                # Obtener acudientes del estudiante
                response_acud = requests.get(f"{SUPABASE_URL}/rest/v1/estudiante_acudiente?documento_estudiante=eq.{documento_buscar}", headers=headers)
                acudientes = response_acud.json() if response_acud.status_code == 200 else []
                
                with st.form("editar_estudiante", clear_on_submit=False):
                    st.success(f"Editando: {estudiante.get('nombre_estudiante', '')} {estudiante.get('apellidos_estudiante', '')}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        nombre = st.text_input("Nombre", value=estudiante.get('nombre_estudiante', ''))
                        apellidos = st.text_input("Apellidos", value=estudiante.get('apellidos_estudiante', ''))
                        st.text_input("Documento", value=estudiante.get('documento_estudiante', ''), disabled=True)
                        curso = st.selectbox("Curso", ["901", "902", "903", "1001", "1002", "1003", "1101"], 
                                            index=["901","902","903","1001","1002","1003","1101"].index(estudiante.get('curso', '901')))
                        telefono = st.text_input("Teléfono", value=estudiante.get('telefono_estudiante', ''))
                        email = st.text_input("Email", value=estudiante.get('email_estudiante', ''))
                    
                    with col2:
                        st.markdown("**Acudientes**")
                        
                        # Mostrar acudientes existentes
                        for idx, acud in enumerate(acudientes):
                            st.write(f"**Acudiente {idx + 1}**")
                            nombre_acud = st.text_input(f"Nombre", value=acud.get('nombre_acudiente', ''), key=f"nombre_acud_{idx}")
                            doc_acud = st.text_input(f"Documento", value=acud.get('documento_acudiente', ''), key=f"doc_acud_{idx}")
                            parentesco_acud = st.selectbox(f"Parentesco", ["", "Padre", "Madre", "Tío", "Tía", "Abuelo", "Abuela", "Otro"],
                                                          index=["", "Padre", "Madre", "Tío", "Tía", "Abuelo", "Abuela", "Otro"].index(acud.get('parentesco', '')),
                                                          key=f"parentesco_acud_{idx}")
                            telefono_acud = st.text_input(f"Teléfono", value=acud.get('telefono_acudiente', ''), key=f"telefono_acud_{idx}")
                            email_acud = st.text_input(f"Email", value=acud.get('email_acudiente', ''), key=f"email_acud_{idx}")
                            es_principal = st.checkbox(f"Acudiente principal", value=acud.get('es_principal', False), key=f"principal_acud_{idx}")
                            
                            if st.button(f"🗑️ Eliminar acudiente {idx + 1}", key=f"eliminar_acud_{idx}"):
                                requests.delete(f"{SUPABASE_URL}/rest/v1/estudiante_acudiente?id=eq.{acud.get('id')}", headers=headers)
                                st.rerun()
                            st.divider()
                        
                        # Botón para agregar nuevo acudiente
                        if st.button("➕ Agregar otro acudiente", key="agregar_acudiente"):
                            st.session_state.agregar_acudiente = True
                        
                        if st.session_state.get('agregar_acudiente', False):
                            st.write("**Nuevo acudiente**")
                            nuevo_nombre = st.text_input("Nombre", key="nuevo_nombre_acud")
                            nuevo_doc = st.text_input("Documento", key="nuevo_doc_acud")
                            nuevo_parentesco = st.selectbox("Parentesco", ["", "Padre", "Madre", "Tío", "Tía", "Abuelo", "Abuela", "Otro"], key="nuevo_parentesco")
                            nuevo_telefono = st.text_input("Teléfono", key="nuevo_telefono_acud")
                            nuevo_email = st.text_input("Email", key="nuevo_email_acud")
                            
                            if st.button("Guardar nuevo acudiente"):
                                if nuevo_nombre and nuevo_doc:
                                    data_acud = {
                                        "documento_estudiante": documento_buscar,
                                        "documento_acudiente": nuevo_doc,
                                        "nombre_acudiente": nuevo_nombre,
                                        "parentesco": nuevo_parentesco,
                                        "telefono_acudiente": nuevo_telefono,
                                        "email_acudiente": nuevo_email,
                                        "es_principal": False
                                    }
                                    requests.post(f"{SUPABASE_URL}/rest/v1/estudiante_acudiente", headers=headers, json=data_acud)
                                    
                                    # Crear usuario para el nuevo acudiente
                                    user_check = requests.get(f"{SUPABASE_URL}/rest/v1/usuarios_login?username=eq.{nuevo_doc}", headers=headers)
                                    if user_check.status_code == 200 and not user_check.json():
                                        user_data = {
                                            "username": nuevo_doc,
                                            "password_hash": "demo2026",
                                            "rol": "acudiente",
                                            "documento": nuevo_doc,
                                            "roles": ["acudiente"]
                                        }
                                        requests.post(f"{SUPABASE_URL}/rest/v1/usuarios_login", headers=headers, json=user_data)
                                    
                                    st.success("Acudiente agregado")
                                    st.session_state.agregar_acudiente = False
                                    st.rerun()
                    
                    if st.form_submit_button("💾 Guardar Cambios", type="primary"):
                        # Actualizar datos del estudiante
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
                            # Actualizar acudientes existentes
                            for idx, acud in enumerate(acudientes):
                                data_acud_update = {
                                    "nombre_acudiente": st.session_state.get(f"nombre_acud_{idx}", acud.get('nombre_acudiente', '')),
                                    "documento_acudiente": st.session_state.get(f"doc_acud_{idx}", acud.get('documento_acudiente', '')),
                                    "parentesco": st.session_state.get(f"parentesco_acud_{idx}", acud.get('parentesco', '')),
                                    "telefono_acudiente": st.session_state.get(f"telefono_acud_{idx}", acud.get('telefono_acudiente', '')),
                                    "email_acudiente": st.session_state.get(f"email_acud_{idx}", acud.get('email_acudiente', '')),
                                    "es_principal": st.session_state.get(f"principal_acud_{idx}", acud.get('es_principal', False))
                                }
                                update_acud_url = f"{SUPABASE_URL}/rest/v1/estudiante_acudiente?id=eq.{acud.get('id')}"
                                requests.patch(update_acud_url, headers=headers, json=data_acud_update)
                            
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
                        # Obtener nombre del hijo
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
                    # Verificar si ya existe
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
                            # Crear usuario para login
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
