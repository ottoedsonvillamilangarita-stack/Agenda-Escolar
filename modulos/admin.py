import streamlit as st
import requests
import pandas as pd
from datetime import datetime, time
from utils import SUPABASE_URL, get_headers

# ============================================
# FUNCIÓN PRINCIPAL mostrar()
# ============================================
def mostrar(data):
    st.title("🛡️ Panel de Administrador")
    st.write(f"Bienvenido, {data.get('username', 'Admin')}")
    
    if "admin_seccion" not in st.session_state:
        st.session_state.admin_seccion = "dashboard"
    
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
                documento = st.text_input("Documento de identidad *")
                curso = st.selectbox("Curso *", ["901", "902", "903", "1001", "1002", "1003", "1101"])
                telefono = st.text_input("Teléfono")
                email = st.text_input("Email")
                direccion = st.text_input("Dirección")
            with col2:
                st.markdown("**Datos del acudiente**")
                nombre_acudiente = st.text_input("Nombre del acudiente *")
                documento_acudiente = st.text_input("Documento del acudiente *")
                parentesco = st.selectbox("Parentesco", ["", "Padre", "Madre", "Tío", "Tía", "Abuelo", "Abuela", "Otro"])
                telefono_acudiente = st.text_input("Teléfono del acudiente")
                email_acudiente = st.text_input("Email del acudiente")
                direccion_acudiente = st.text_input("Dirección del acudiente")
            
            if st.form_submit_button("💾 Registrar Estudiante", type="primary"):
                if not all([nombre, apellidos, documento, curso, nombre_acudiente, documento_acudiente]):
                    st.error("❌ Completa todos los campos obligatorios (*)")
                else:
                    check_url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{documento}"
                    check_response = requests.get(check_url, headers=headers)
                    if check_response.status_code == 200 and check_response.json():
                        st.error(f"❌ Ya existe un estudiante con el documento {documento}")
                    else:
                        data_estudiante = {
                            "nombre_estudiante": nombre,
                            "apellidos_estudiante": apellidos,
                            "documento_estudiante": documento,
                            "curso": curso,
                            "telefono_estudiante": telefono,
                            "email_estudiante": email,
                            "direccion_estudiante": direccion
                        }
                        response = requests.post(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers, json=data_estudiante)
                        if response.status_code == 201:
                            user_data = {
                                "username": documento,
                                "password_hash": "demo2026",
                                "rol": "estudiante",
                                "documento": documento,
                                "roles": ["estudiante"]
                            }
                            requests.post(f"{SUPABASE_URL}/rest/v1/usuarios_login", headers=headers, json=user_data)
                            data_acudiente = {
                                "documento_estudiante": documento,
                                "documento_acudiente": documento_acudiente,
                                "nombre_acudiente": nombre_acudiente,
                                "parentesco": parentesco,
                                "telefono_acudiente": telefono_acudiente,
                                "email_acudiente": email_acudiente,
                                "direccion_acudiente": direccion_acudiente,
                                "es_principal": True
                            }
                            requests.post(f"{SUPABASE_URL}/rest/v1/estudiante_acudiente", headers=headers, json=data_acudiente)
                            user_acud = {
                                "username": documento_acudiente,
                                "password_hash": "demo2026",
                                "rol": "acudiente",
                                "documento": documento_acudiente,
                                "roles": ["acudiente"]
                            }
                            requests.post(f"{SUPABASE_URL}/rest/v1/usuarios_login", headers=headers, json=user_acud)
                            st.success(f"✅ Estudiante {nombre} {apellidos} registrado exitosamente")
                            st.info(f"🔑 Usuario estudiante: {documento} | Contraseña: demo2026")
                            st.info(f"🔑 Usuario acudiente: {documento_acudiente} | Contraseña: demo2026")
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
                    response_acud = requests.get(f"{SUPABASE_URL}/rest/v1/estudiante_acudiente?documento_estudiante=eq.{documento_buscar}", headers=headers)
                    acudientes = response_acud.json() if response_acud.status_code == 200 else []
                    with st.form("editar_estudiante_completo"):
                        st.success(f"Editando: {estudiante.get('nombre_estudiante', '')} {estudiante.get('apellidos_estudiante', '')}")
                        st.markdown("### Datos personales")
                        col1, col2 = st.columns(2)
                        with col1:
                            nombre = st.text_input("Nombre", value=estudiante.get('nombre_estudiante', ''))
                            apellidos = st.text_input("Apellidos", value=estudiante.get('apellidos_estudiante', ''))
                            documento_edit = st.text_input("Documento", value=estudiante.get('documento_estudiante', ''), disabled=True)
                            curso = st.selectbox("Curso", ["901", "902", "903", "1001", "1002", "1003", "1101"], 
                                                index=["901","902","903","1001","1002","1003","1101"].index(estudiante.get('curso', '901')))
                        with col2:
                            telefono = st.text_input("Teléfono", value=estudiante.get('telefono_estudiante', ''))
                            email = st.text_input("Email", value=estudiante.get('email_estudiante', ''))
                            direccion = st.text_input("Dirección", value=estudiante.get('direccion_estudiante', ''))
                        st.divider()
                        st.markdown("### Acudientes")
                        for idx, acud in enumerate(acudientes):
                            with st.container():
                                st.markdown(f"**Acudiente {idx + 1}**")
                                col1, col2 = st.columns(2)
                                with col1:
                                    nombre_acud = st.text_input("Nombre", value=acud.get('nombre_acudiente', ''), key=f"acud_nombre_{idx}")
                                    doc_acud = st.text_input("Documento", value=acud.get('documento_acudiente', ''), key=f"acud_doc_{idx}")
                                    parentesco_acud = st.selectbox("Parentesco", ["", "Padre", "Madre", "Tío", "Tía", "Abuelo", "Abuela", "Otro"],
                                                                  index=["", "Padre", "Madre", "Tío", "Tía", "Abuelo", "Abuela", "Otro"].index(acud.get('parentesco', '')),
                                                                  key=f"acud_parentesco_{idx}")
                                with col2:
                                    telefono_acud = st.text_input("Teléfono", value=acud.get('telefono_acudiente', ''), key=f"acud_telefono_{idx}")
                                    email_acud = st.text_input("Email", value=acud.get('email_acudiente', ''), key=f"acud_email_{idx}")
                                    direccion_acud = st.text_input("Dirección", value=acud.get('direccion_acudiente', ''), key=f"acud_direccion_{idx}")
                                    es_principal = st.checkbox("Acudiente principal", value=acud.get('es_principal', False), key=f"acud_principal_{idx}")
                                if st.button(f"🗑️ Eliminar acudiente {idx + 1}", key=f"eliminar_acud_{idx}"):
                                    requests.delete(f"{SUPABASE_URL}/rest/v1/estudiante_acudiente?id=eq.{acud['id']}", headers=headers)
                                    st.success("Acudiente eliminado")
                                    st.rerun()
                                st.divider()
                        with st.expander("➕ Agregar otro acudiente"):
                            col1, col2 = st.columns(2)
                            with col1:
                                nuevo_nombre = st.text_input("Nombre", key="nuevo_acud_nombre")
                                nuevo_doc = st.text_input("Documento", key="nuevo_acud_doc")
                                nuevo_parentesco = st.selectbox("Parentesco", ["", "Padre", "Madre", "Tío", "Tía", "Abuelo", "Abuela", "Otro"], key="nuevo_acud_parentesco")
                            with col2:
                                nuevo_telefono = st.text_input("Teléfono", key="nuevo_acud_telefono")
                                nuevo_email = st.text_input("Email", key="nuevo_acud_email")
                                nuevo_direccion = st.text_input("Dirección", key="nuevo_acud_direccion")
                            if st.button("Agregar acudiente", key="btn_agregar_acud"):
                                if nuevo_nombre and nuevo_doc:
                                    new_acud_data = {
                                        "documento_estudiante": documento_buscar,
                                        "documento_acudiente": nuevo_doc,
                                        "nombre_acudiente": nuevo_nombre,
                                        "parentesco": nuevo_parentesco,
                                        "telefono_acudiente": nuevo_telefono,
                                        "email_acudiente": nuevo_email,
                                        "direccion_acudiente": nuevo_direccion,
                                        "es_principal": False
                                    }
                                    requests.post(f"{SUPABASE_URL}/rest/v1/estudiante_acudiente", headers=headers, json=new_acud_data)
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
                                    st.rerun()
                        if st.form_submit_button("💾 Guardar todos los cambios", type="primary"):
                            data_update = {
                                "nombre_estudiante": nombre,
                                "apellidos_estudiante": apellidos,
                                "curso": curso,
                                "telefono_estudiante": telefono,
                                "email_estudiante": email,
                                "direccion_estudiante": direccion
                            }
                            update_url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{documento_buscar}"
                            requests.patch(update_url, headers=headers, json=data_update)
                            for idx, acud in enumerate(acudientes):
                                nombre_acud = st.session_state.get(f"acud_nombre_{idx}", acud.get('nombre_acudiente', ''))
                                doc_acud = st.session_state.get(f"acud_doc_{idx}", acud.get('documento_acudiente', ''))
                                parentesco_acud = st.session_state.get(f"acud_parentesco_{idx}", acud.get('parentesco', ''))
                                telefono_acud = st.session_state.get(f"acud_telefono_{idx}", acud.get('telefono_acudiente', ''))
                                email_acud = st.session_state.get(f"acud_email_{idx}", acud.get('email_acudiente', ''))
                                direccion_acud = st.session_state.get(f"acud_direccion_{idx}", acud.get('direccion_acudiente', ''))
                                es_principal = st.session_state.get(f"acud_principal_{idx}", acud.get('es_principal', False))
                                if nombre_acud and doc_acud:
                                    update_acud_url = f"{SUPABASE_URL}/rest/v1/estudiante_acudiente?id=eq.{acud['id']}"
                                    acud_data = {
                                        "nombre_acudiente": nombre_acud,
                                        "documento_acudiente": doc_acud,
                                        "parentesco": parentesco_acud,
                                        "telefono_acudiente": telefono_acud,
                                        "email_acudiente": email_acud,
                                        "direccion_acudiente": direccion_acud,
                                        "es_principal": es_principal
                                    }
                                    requests.patch(update_acud_url, headers=headers, json=acud_data)
                            st.success("✅ Estudiante actualizado exitosamente")
                            st.balloons()
                            st.rerun()
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
                            "direccion": rel.get('direccion_acudiente'),
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
                        "Dirección": v.get("direccion", ""),
                        "Hijos": ", ".join(v["hijos"])
                    } for v in acudientes_dict.values()])
                    st.dataframe(df, use_container_width=True)
                    st.caption(f"Total: {len(acudientes_dict)} acudientes")
                else:
                    st.info("No hay acudientes registrados")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    with tab2:
        st.write("**Buscar acudiente por documento**")
        doc_buscar = st.text_input("Documento del acudiente", key="buscar_acudiente")
        if doc_buscar:
            url = f"{SUPABASE_URL}/rest/v1/estudiante_acudiente?documento_acudiente=eq.{doc_buscar}"
            response = requests.get(url, headers=headers)
            if response.status_code == 200 and response.json():
                acudientes = response.json()
                acudiente = acudientes[0]
                with st.form("editar_acudiente"):
                    st.success(f"Editando acudiente: {acudiente.get('nombre_acudiente', '')}")
                    col1, col2 = st.columns(2)
                    with col1:
                        nombre = st.text_input("Nombre", value=acudiente.get('nombre_acudiente', ''))
                        documento = st.text_input("Documento", value=acudiente.get('documento_acudiente', ''), disabled=True)
                        parentesco = st.text_input("Parentesco", value=acudiente.get('parentesco', ''))
                    with col2:
                        telefono = st.text_input("Teléfono", value=acudiente.get('telefono_acudiente', ''))
                        email = st.text_input("Email", value=acudiente.get('email_acudiente', ''))
                        direccion = st.text_input("Dirección", value=acudiente.get('direccion_acudiente', ''))
                    st.write("**Hijos asociados:**")
                    for acud in acudientes:
                        hijo_url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{acud.get('documento_estudiante')}"
                        hijo_resp = requests.get(hijo_url, headers=headers)
                        if hijo_resp.status_code == 200 and hijo_resp.json():
                            hijo = hijo_resp.json()[0]
                            st.write(f"- {hijo.get('nombre_estudiante')} ({hijo.get('curso')})")
                    if st.form_submit_button("💾 Guardar Cambios", type="primary"):
                        for acud in acudientes:
                            update_data = {
                                "nombre_acudiente": nombre,
                                "parentesco": parentesco,
                                "telefono_acudiente": telefono,
                                "email_acudiente": email,
                                "direccion_acudiente": direccion
                            }
                            update_url = f"{SUPABASE_URL}/rest/v1/estudiante_acudiente?id=eq.{acud['id']}"
                            requests.patch(update_url, headers=headers, json=update_data)
                        st.success("✅ Acudiente actualizado exitosamente")
                        st.rerun()
            else:
                st.warning("No se encontró un acudiente con ese documento")


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
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    with tab2:
        st.write("**Registrar nuevo docente**")
        with st.form("nuevo_docente", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Datos personales**")
                nombre = st.text_input("Nombre *")
                apellidos = st.text_input("Apellidos *")
                documento = st.text_input("Documento de identidad *")
                fecha_nacimiento = st.date_input("Fecha de nacimiento", value=None)
                sexo = st.selectbox("Sexo", ["", "Masculino", "Femenino"])
                direccion = st.text_input("Dirección")
            with col2:
                st.markdown("**Datos profesionales**")
                telefono = st.text_input("Teléfono")
                email = st.text_input("Email")
                titulo = st.text_input("Título profesional")
                especializacion = st.text_input("Especialización")
                tipo_contrato = st.selectbox("Tipo de contrato", ["", "Planta", "Contrato", "Cátedra", "Ocasional"])
                fecha_ingreso = st.date_input("Fecha de ingreso", value=None)
                observaciones = st.text_area("Observaciones", height=68)
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
                            "fecha_nacimiento": str(fecha_nacimiento) if fecha_nacimiento else None,
                            "sexo_docente": sexo,
                            "direccion_docente": direccion,
                            "telefono_docente": telefono,
                            "email_docente": email,
                            "titulo": titulo,
                            "especializacion": especializacion,
                            "tipo_contrato": tipo_contrato,
                            "fecha_ingreso": str(fecha_ingreso) if fecha_ingreso else None,
                            "observaciones": observaciones
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
                            st.success(f"✅ Docente {nombre} {apellidos} registrado exitosamente")
                            st.info(f"🔑 Usuario: {username} | Contraseña: demo2026")
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
                with st.form("editar_docente_completo"):
                    st.success(f"Editando: {docente.get('nombre_docente', '')} {docente.get('apellidos_docente', '')}")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Datos personales**")
                        nombre = st.text_input("Nombre", value=docente.get('nombre_docente', ''))
                        apellidos = st.text_input("Apellidos", value=docente.get('apellidos_docente', ''))
                        st.text_input("Documento", value=docente.get('documento_docente', ''), disabled=True)
                        fecha_nacimiento = st.date_input("Fecha de nacimiento", 
                                                        value=datetime.strptime(docente.get('fecha_nacimiento', '2000-01-01'), '%Y-%m-%d') if docente.get('fecha_nacimiento') else None)
                        sexo = st.selectbox("Sexo", ["", "Masculino", "Femenino"],
                                           index=["", "Masculino", "Femenino"].index(docente.get('sexo_docente', '')) if docente.get('sexo_docente') in ["", "Masculino", "Femenino"] else 0)
                        direccion = st.text_input("Dirección", value=docente.get('direccion_docente', ''))
                    with col2:
                        st.markdown("**Datos profesionales**")
                        telefono = st.text_input("Teléfono", value=docente.get('telefono_docente', ''))
                        email = st.text_input("Email", value=docente.get('email_docente', ''))
                        titulo = st.text_input("Título", value=docente.get('titulo', ''))
                        especializacion = st.text_input("Especialización", value=docente.get('especializacion', ''))
                        tipo_contrato = st.selectbox("Tipo de contrato", ["", "Planta", "Contrato", "Cátedra", "Ocasional"],
                                                    index=["", "Planta", "Contrato", "Cátedra", "Ocasional"].index(docente.get('tipo_contrato', '')) if docente.get('tipo_contrato') in ["", "Planta", "Contrato", "Cátedra", "Ocasional"] else 0)
                        fecha_ingreso = st.date_input("Fecha de ingreso", 
                                                     value=datetime.strptime(docente.get('fecha_ingreso', '2024-01-01'), '%Y-%m-%d') if docente.get('fecha_ingreso') else None)
                        observaciones = st.text_area("Observaciones", value=docente.get('observaciones', ''), height=68)
                    if st.form_submit_button("💾 Guardar Cambios", type="primary"):
                        data_update = {
                            "nombre_docente": nombre,
                            "apellidos_docente": apellidos,
                            "fecha_nacimiento": str(fecha_nacimiento) if fecha_nacimiento else None,
                            "sexo_docente": sexo,
                            "direccion_docente": direccion,
                            "telefono_docente": telefono,
                            "email_docente": email,
                            "titulo": titulo,
                            "especializacion": especializacion,
                            "tipo_contrato": tipo_contrato,
                            "fecha_ingreso": str(fecha_ingreso) if fecha_ingreso else None,
                            "observaciones": observaciones
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
# FUNCIONES DE CONFIGURACIÓN DE HORARIOS
# ============================================
def configurar_niveles(headers):
    st.write("**📚 Niveles Educativos**")
    
    response = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    
    if response.status_code == 200:
        niveles = response.json()
        if niveles:
            st.write("**Niveles existentes:**")
            for n in niveles:
                st.write(f"- {n['nombre']}")
    
    with st.expander("➕ Agregar nivel"):
        nuevo_nivel = st.text_input("Nombre del nivel", key="nuevo_nivel_input")
        if st.button("Agregar nivel", key="agregar_nivel_btn"):
            if nuevo_nivel:
                data = {"nombre": nuevo_nivel, "orden": len(niveles) + 1 if niveles else 1}
                r = requests.post(f"{SUPABASE_URL}/rest/v1/niveles", headers=headers, json=data)
                if r.status_code == 201:
                    st.success(f"✅ Nivel '{nuevo_nivel}' agregado")
                    st.rerun()


def configurar_horas_nivel(headers):
    st.write("**⏰ Configurar Horas por Nivel**")
    st.info("Define las franjas horarias para cada nivel.")
    
    response_niveles = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    
    if response_niveles.status_code != 200:
        st.error(f"Error al cargar niveles: {response_niveles.status_code}")
        return
    
    niveles = response_niveles.json()
    
    if not niveles:
        st.warning("No hay niveles configurados")
        return
    
    nivel_nombres = [n['nombre'] for n in niveles]
    nivel_seleccionado = st.selectbox("Seleccionar nivel", nivel_nombres, key="horas_nivel_select")
    nivel_id = next(n['id'] for n in niveles if n['nombre'] == nivel_seleccionado)
    
    url_horas = f"{SUPABASE_URL}/rest/v1/horas_nivel?nivel_id=eq.{nivel_id}&order=orden.asc"
    response_horas = requests.get(url_horas, headers=headers)
    horas = response_horas.json() if response_horas.status_code == 200 else []
    
    st.write(f"**Horas configuradas para {nivel_seleccionado}:**")
    
    if horas:
        for h in horas:
            st.write(f"- Hora {h['orden']}: {h['hora_inicio'][:5]} - {h['hora_fin'][:5]}")
    else:
        st.info("No hay horas configuradas para este nivel.")



# ============================================
# FUNCIÓN 9: CONFIGURAR JORNADA POR NIVEL
# ============================================
def configurar_jornada_nivel(headers):
    st.write("**📅 Configurar Días Laborales por Nivel**")
    
    response_niveles = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    
    if response_niveles.status_code != 200:
        st.error("Error al cargar niveles")
        return
    
    niveles = response_niveles.json()
    
    if not niveles:
        st.warning("No hay niveles configurados")
        return
    
    nivel_nombres = [n['nombre'] for n in niveles]
    nivel_seleccionado = st.selectbox("Seleccionar nivel", nivel_nombres, key="jornada_nivel_select")
    
    st.info(f"Configuración para {nivel_seleccionado}")
    st.write("(Funcionalidad en desarrollo)")


# ============================================
# FUNCIÓN 10: GESTIONAR ASIGNATURAS
# ============================================
def gestionar_asignaturas(headers):
    st.subheader("📚 Gestionar Asignaturas")
    st.caption("Marca/Desmarca los niveles para cada materia. Los cambios se guardan con un solo botón.")
    
    # Obtener niveles
    response_niveles = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    if response_niveles.status_code != 200:
        st.error("Error al cargar niveles")
        return
    
    niveles = response_niveles.json()
    nivel_nombres = [n['nombre'] for n in niveles]
    niveles_dict = {n['nombre']: n['id'] for n in niveles}
    
    # Obtener materias
    response_materias = requests.get(f"{SUPABASE_URL}/rest/v1/materias?order=nombre.asc", headers=headers)
    if response_materias.status_code != 200:
        st.error("Error al cargar materias")
        return
    
    materias = response_materias.json()
    
    # Obtener relaciones
    response_relaciones = requests.get(f"{SUPABASE_URL}/rest/v1/materias_niveles", headers=headers)
    relaciones = response_relaciones.json() if response_relaciones.status_code == 200 else []
    
    # Crear diccionario de niveles por materia
    niveles_por_materia = {}
    for r in relaciones:
        materia_id = r['materia_id']
        nivel_id = r['nivel_id']
        if materia_id not in niveles_por_materia:
            niveles_por_materia[materia_id] = []
        niveles_por_materia[materia_id].append(nivel_id)
    
    # =============================================
    # CREAR DATAFRAME EDITABLE
    # =============================================
    import pandas as pd
    
    data = []
    for m in materias:
        niveles_ids = niveles_por_materia.get(m['id'], [])
        row = {
            "id": m['id'],
            "nombre": m['nombre'],
            "codigo": m.get('codigo', '') if m.get('codigo') is not None else ''
        }
        for nivel in nivel_nombres:
            nivel_id = niveles_dict.get(nivel)
            row[nivel] = nivel_id in niveles_ids if nivel_id else False
        data.append(row)
    
    df = pd.DataFrame(data)
    
    # =============================================
    # MOSTRAR TABLA EDITABLE
    # =============================================
    st.write("### 📋 Asignaturas y niveles")
    
    column_config = {
        "id": st.column_config.NumberColumn("ID", width="small", disabled=True),
        "nombre": st.column_config.TextColumn("Materia", width="medium", disabled=True),
        "codigo": st.column_config.TextColumn("Código", width="small")
    }
    
    for nivel in nivel_nombres:
        column_config[nivel] = st.column_config.CheckboxColumn(nivel, width="small")
    
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        hide_index=True,
        key="materias_editor",
        column_config=column_config
    )
    
    # =============================================
    # BOTÓN PARA GUARDAR TODOS LOS CAMBIOS
    # =============================================
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("💾 Guardar todos los cambios", type="primary", use_container_width=True):
            with st.spinner("Guardando cambios..."):
                guardados = 0
                errores = 0
                
                for idx, row in edited_df.iterrows():
                    materia_id = row['id']
                    materia_nombre = row['nombre']
                    nuevo_codigo = row['codigo']
                    
                    try:
                        # Actualizar código
                        materia_original = next((m for m in materias if m['id'] == materia_id), None)
                        if materia_original:
                            codigo_actual = materia_original.get('codigo', '') or ''
                            codigo_nuevo = nuevo_codigo if nuevo_codigo and not pd.isna(nuevo_codigo) else ''
                            if isinstance(codigo_nuevo, float):
                                codigo_nuevo = str(codigo_nuevo) if not pd.isna(codigo_nuevo) else ''
                            codigo_nuevo = codigo_nuevo.strip().upper() if codigo_nuevo else None
                            codigo_actual = codigo_actual.strip().upper() if codigo_actual else ''
                            
                            if codigo_nuevo != codigo_actual:
                                update_data = {"codigo": codigo_nuevo}
                                requests.patch(
                                    f"{SUPABASE_URL}/rest/v1/materias?id=eq.{materia_id}",
                                    headers=headers,
                                    json=update_data
                                )
                        
                        # Obtener niveles seleccionados
                        niveles_seleccionados = []
                        for nivel in nivel_nombres:
                            if row.get(nivel, False):
                                niveles_seleccionados.append(nivel)
                        
                        # Eliminar relaciones actuales
                        requests.delete(
                            f"{SUPABASE_URL}/rest/v1/materias_niveles?materia_id=eq.{materia_id}",
                            headers=headers
                        )
                        
                        # Insertar nuevas relaciones
                        for nivel_nombre in niveles_seleccionados:
                            nivel_id = niveles_dict.get(nivel_nombre)
                            if nivel_id:
                                rel_data = {"materia_id": materia_id, "nivel_id": nivel_id}
                                requests.post(
                                    f"{SUPABASE_URL}/rest/v1/materias_niveles",
                                    headers=headers,
                                    json=rel_data
                                )
                        
                        guardados += 1
                        
                    except Exception as e:
                        errores += 1
                
                if errores == 0:
                    st.success(f"✅ {guardados} materias actualizadas correctamente")
                    st.rerun()
                else:
                    st.warning(f"⚠️ {guardados} actualizadas, {errores} errores")
    
    st.divider()
    
    # =============================================
    # AGREGAR NUEVA MATERIA
    # =============================================
    st.write("### ➕ Agregar nueva asignatura")
    
    with st.form("nueva_materia_form"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre de la asignatura *")
            codigo = st.text_input("Código (opcional)")
        with col2:
            st.write("**Niveles donde se dicta:**")
            niveles_nueva = []
            for nivel in nivel_nombres:
                checked = st.checkbox(nivel, key=f"nueva_nivel_{nivel}")
                if checked:
                    niveles_nueva.append(nivel)
        
        submitted = st.form_submit_button("💾 Crear asignatura", type="primary")
        
        if submitted:
            if not nombre:
                st.error("❌ El nombre es obligatorio")
            elif not niveles_nueva:
                st.error("❌ Selecciona al menos un nivel")
            else:
                nombre_upper = nombre.upper().strip()
                codigo_upper = codigo.upper().strip() if codigo else None
                
                check_url = f"{SUPABASE_URL}/rest/v1/materias?nombre=eq.{nombre_upper}"
                check_resp = requests.get(check_url, headers=headers)
                
                if check_resp.status_code == 200 and check_resp.json():
                    st.error(f"❌ La asignatura '{nombre_upper}' ya existe")
                else:
                    data = {"nombre": nombre_upper, "codigo": codigo_upper}
                    r = requests.post(f"{SUPABASE_URL}/rest/v1/materias", headers=headers, json=data)
                    
                    if r.status_code == 201:
                        materia_id = r.json()[0]['id']
                        
                        for nivel_nombre in niveles_nueva:
                            nivel_id = niveles_dict.get(nivel_nombre)
                            if nivel_id:
                                rel_data = {"materia_id": materia_id, "nivel_id": nivel_id}
                                requests.post(
                                    f"{SUPABASE_URL}/rest/v1/materias_niveles",
                                    headers=headers,
                                    json=rel_data
                                )
                        
                        st.success(f"✅ Asignatura '{nombre_upper}' creada correctamente")
                        st.rerun()
                    else:
                        st.error(f"❌ Error al crear: {r.status_code}")
                        st.code(r.text)
    
    # =============================================
    # ELIMINAR MATERIA
    # =============================================
    if materias:
        st.divider()
        st.write("### 🗑️ Eliminar asignatura")
        st.caption("⚠️ Solo se puede eliminar si no está asignada a ningún horario.")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            materia_eliminar = st.selectbox(
                "Seleccionar materia para eliminar",
                options=[f"{m['id']} - {m['nombre']}" for m in materias],
                key="eliminar_materia_select"
            )
        with col2:
            if st.button("🗑️ Eliminar", type="secondary", use_container_width=True):
                if materia_eliminar:
                    materia_id = int(materia_eliminar.split(' - ')[0])
                    materia_nombre = materia_eliminar.split(' - ')[1]
                    
                    check_url = f"{SUPABASE_URL}/rest/v1/horario_base?asignatura=eq.{materia_nombre}&limit=1"
                    check_resp = requests.get(check_url, headers=headers)
                    
                    if check_resp.status_code == 200 and check_resp.json():
                        st.error(f"❌ No se puede eliminar '{materia_nombre}' porque está en uso en horarios")
                    else:
                        requests.delete(
                            f"{SUPABASE_URL}/rest/v1/materias_niveles?materia_id=eq.{materia_id}",
                            headers=headers
                        )
                        r = requests.delete(
                            f"{SUPABASE_URL}/rest/v1/materias?id=eq.{materia_id}",
                            headers=headers
                        )
                        if r.status_code == 204:
                            st.success(f"✅ Materia '{materia_nombre}' eliminada")
                            st.rerun()
                        else:
                            st.error(f"❌ Error al eliminar: {r.status_code}")

# ============================================
# FUNCIÓN 11: GESTIONAR FESTIVOS
# ============================================
def gestion_festivos(headers):
    st.write("**📆 Festivos**")
    
    year = st.selectbox("Año", [2024, 2025, 2026], key="festivos_year")
    
    url_festivos = f"{SUPABASE_URL}/rest/v1/festivos?year=eq.{year}&order=fecha.asc"
    response_festivos = requests.get(url_festivos, headers=headers)
    
    if response_festivos.status_code == 200:
        festivos = response_festivos.json()
        if festivos:
            st.write("**Festivos registrados:**")
            for f in festivos:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"{f['fecha']} - {f.get('descripcion', 'Sin descripción')}")
                with col2:
                    if st.button("🗑️", key=f"del_festivo_{f['id']}"):
                        requests.delete(f"{SUPABASE_URL}/rest/v1/festivos?id=eq.{f['id']}", headers=headers)
                        st.rerun()
        else:
            st.info("No hay festivos registrados")
    else:
        st.warning("No se pudieron cargar los festivos")
    
    with st.expander("➕ Agregar festivo"):
        col1, col2 = st.columns(2)
        with col1:
            fecha = st.date_input("Fecha", key="festivo_fecha")
        with col2:
            descripcion = st.text_input("Descripción", key="festivo_desc")
        
        if st.button("Agregar", key="agregar_festivo_btn"):
            data = {"fecha": str(fecha), "descripcion": descripcion, "year": fecha.year}
            requests.post(f"{SUPABASE_URL}/rest/v1/festivos", headers=headers, json=data)
            st.success("✅ Festivo agregado")
            st.rerun()


# ============================================
# FUNCIÓN 12: GESTIONAR DIRECTORES DE GRUPO
# ============================================
def gestion_directores_grupo(headers):
    st.subheader("👨‍🏫 Directores de Grupo")
    st.caption("Asigna o cambia el director de grupo para cada curso.")
    
    # 1. Obtener cursos
    response_cursos = requests.get(f"{SUPABASE_URL}/rest/v1/estudiantes?select=curso", headers=headers)
    if response_cursos.status_code != 200:
        st.error("❌ Error al cargar los cursos")
        return
    
    cursos = list(set([e['curso'] for e in response_cursos.json() if e.get('curso')]))
    cursos.sort()
    
    if not cursos:
        st.warning("⚠️ No hay cursos registrados")
        return
    
    # 2. Obtener docentes
    response_docentes = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
    if response_docentes.status_code != 200:
        st.error("❌ Error al cargar docentes")
        return
    
    docentes = response_docentes.json()
    docentes_dict = {d['documento_docente']: f"{d['nombre_docente']} {d['apellidos_docente']}" for d in docentes}
    opciones_docentes = [""] + list(docentes_dict.keys())
    
    # 3. Obtener directores desde asignacion_academica
    response_asignaciones = requests.get(f"{SUPABASE_URL}/rest/v1/asignacion_academica", headers=headers)
    
    directores_por_curso = {}
    if response_asignaciones.status_code == 200:
        asignaciones = response_asignaciones.json()
        for a in asignaciones:
            if a.get('asignatura') == 'Dirección de Curso':
                curso = a.get('curso')
                docente_documento = a.get('documento_docente')
                if curso and docente_documento:
                    directores_por_curso[curso] = docente_documento
    
    # 4. Mostrar tabla
    st.write("### 📋 Directores por curso")
    
    data = []
    for curso in cursos:
        docente_documento = directores_por_curso.get(curso)
        data.append({
            "Curso": curso,
            "Director": docentes_dict.get(docente_documento, "Sin asignar") if docente_documento else "Sin asignar"
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    total_directores = len([d for d in directores_por_curso.values() if d])
    st.caption(f"📌 {total_directores} de {len(cursos)} cursos tienen director asignado")
    
    st.divider()
    
    # 5. Asignar director
    st.write("### ✏️ Asignar director de grupo")
    
    col1, col2 = st.columns(2)
    with col1:
        curso_seleccionado = st.selectbox("Seleccionar curso", cursos, key="director_curso_edit")
    
    documento_actual = directores_por_curso.get(curso_seleccionado)
    nombre_actual = docentes_dict.get(documento_actual, "Sin asignar") if documento_actual else "Sin asignar"
    st.info(f"📌 Director actual: **{nombre_actual}**")
    
    with col2:
        default_index = 0
        if documento_actual and documento_actual in opciones_docentes:
            default_index = opciones_docentes.index(documento_actual)
        
        docente_seleccionado = st.selectbox(
            "Seleccionar docente",
            options=opciones_docentes,
            index=default_index,
            format_func=lambda x: docentes_dict.get(x, "Seleccionar") if x else "Ninguno",
            key="director_docente_edit"
        )
    
    if st.button("💾 Asignar director", type="primary", key="btn_asignar_director"):
        if not docente_seleccionado:
            st.error("❌ Selecciona un docente")
        else:
            data_director = {
                "curso": curso_seleccionado,
                "asignatura": "Dirección de Curso",
                "documento_docente": docente_seleccionado,
                "anio": 2025
            }
            
            check_url = f"{SUPABASE_URL}/rest/v1/asignacion_academica?curso=eq.{curso_seleccionado}&asignatura=eq.Dirección de Curso"
            check_resp = requests.get(check_url, headers=headers)
            
            if check_resp.status_code == 200 and check_resp.json():
                dir_id = check_resp.json()[0]['id']
                requests.patch(
                    f"{SUPABASE_URL}/rest/v1/asignacion_academica?id=eq.{dir_id}",
                    headers=headers,
                    json=data_director
                )
            else:
                requests.post(
                    f"{SUPABASE_URL}/rest/v1/asignacion_academica",
                    headers=headers,
                    json=data_director
                )
            
            # =============================================
            # ACTUALIZAR user_roles
            # =============================================
            # Obtener el username del docente seleccionado
            username = None
            for d in docentes:
                if d['documento_docente'] == docente_seleccionado:
                    # Buscar el username en usuarios_login
                    user_resp = requests.get(
                        f"{SUPABASE_URL}/rest/v1/usuarios_login?documento=eq.{docente_seleccionado}",
                        headers=headers
                    )
                    if user_resp.status_code == 200 and user_resp.json():
                        username = user_resp.json()[0].get('username')
                    break
            
            if username:
                # Verificar si ya tiene el rol director_grupo
                check_rol_url = f"{SUPABASE_URL}/rest/v1/user_roles?username=eq.{username}&rol=eq.director_grupo"
                check_rol_resp = requests.get(check_rol_url, headers=headers)
                
                if check_rol_resp.status_code == 200 and not check_rol_resp.json():
                    # Agregar el rol
                    requests.post(
                        f"{SUPABASE_URL}/rest/v1/user_roles",
                        headers=headers,
                        json={"username": username, "rol": "director_grupo"}
                    )
            
            st.success(f"✅ Director asignado para {curso_seleccionado}")
            st.rerun()
    
    # 6. Eliminar director
    if st.button("🗑️ Eliminar director", type="secondary", key="btn_eliminar_director"):
        check_url = f"{SUPABASE_URL}/rest/v1/asignacion_academica?curso=eq.{curso_seleccionado}&asignatura=eq.Dirección de Curso"
        check_resp = requests.get(check_url, headers=headers)
        
        if check_resp.status_code == 200 and check_resp.json():
            dir_id = check_resp.json()[0]['id']
            requests.delete(
                f"{SUPABASE_URL}/rest/v1/asignacion_academica?id=eq.{dir_id}",
                headers=headers
            )
            
            # =============================================
            # ELIMINAR DE user_roles
            # =============================================
            # Obtener el username del docente que era director
            username = None
            for d in docentes:
                if d['documento_docente'] == documento_actual:
                    user_resp = requests.get(
                        f"{SUPABASE_URL}/rest/v1/usuarios_login?documento=eq.{documento_actual}",
                        headers=headers
                    )
                    if user_resp.status_code == 200 and user_resp.json():
                        username = user_resp.json()[0].get('username')
                    break
            
            if username:
                # Eliminar el rol director_grupo
                check_rol_url = f"{SUPABASE_URL}/rest/v1/user_roles?username=eq.{username}&rol=eq.director_grupo"
                check_rol_resp = requests.get(check_rol_url, headers=headers)
                
                if check_rol_resp.status_code == 200 and check_rol_resp.json():
                    rol_id = check_rol_resp.json()[0]['id']
                    requests.delete(
                        f"{SUPABASE_URL}/rest/v1/user_roles?id=eq.{rol_id}",
                        headers=headers
                    )
            
            st.success(f"✅ Director eliminado para {curso_seleccionado}")
            st.rerun()
        else:
            st.warning("⚠️ No hay director asignado para este curso")
            
# ============================================
# FUNCIÓN 13: MOSTRAR ASIGNACIÓN
# ============================================
def mostrar_asignacion():
    st.subheader("📚 Asignación Académica")
    headers = get_headers()
    
    if "asignacion_seccion" not in st.session_state:
        st.session_state.asignacion_seccion = "horarios"
    
    # 8 botones
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
    
    with col1:
        if st.button("📖 Horarios", use_container_width=True,
                     type="primary" if st.session_state.asignacion_seccion == "horarios" else "secondary"):
            st.session_state.asignacion_seccion = "horarios"
            st.rerun()
    
    with col2:
        if st.button("👨‍🏫 Directores", use_container_width=True,
                     type="primary" if st.session_state.asignacion_seccion == "directores" else "secondary"):
            st.session_state.asignacion_seccion = "directores"
            st.rerun()
    
    with col3:
        if st.button("⏰ Horas", use_container_width=True,
                     type="primary" if st.session_state.asignacion_seccion == "horas" else "secondary"):
            st.session_state.asignacion_seccion = "horas"
            st.rerun()
    
    with col4:
        if st.button("📅 Días", use_container_width=True,
                     type="primary" if st.session_state.asignacion_seccion == "dias" else "secondary"):
            st.session_state.asignacion_seccion = "dias"
            st.rerun()
    
    with col5:
        if st.button("📚 Niveles", use_container_width=True,
                     type="primary" if st.session_state.asignacion_seccion == "niveles" else "secondary"):
            st.session_state.asignacion_seccion = "niveles"
            st.rerun()
    
    with col6:
        if st.button("📚 Materias", use_container_width=True,
                     type="primary" if st.session_state.asignacion_seccion == "materias" else "secondary"):
            st.session_state.asignacion_seccion = "materias"
            st.rerun()
    
    with col7:
        if st.button("📚 Cursos", use_container_width=True,
                     type="primary" if st.session_state.asignacion_seccion == "grados" else "secondary"):
            st.session_state.asignacion_seccion = "grados"
            st.rerun()
    
    with col8:
        if st.button("📆 Festivos", use_container_width=True,
                     type="primary" if st.session_state.asignacion_seccion == "festivos" else "secondary"):
            st.session_state.asignacion_seccion = "festivos"
            st.rerun()
    
    st.divider()
    
    if st.session_state.asignacion_seccion == "horarios":
        configurar_horario_curso(headers)
    elif st.session_state.asignacion_seccion == "directores":
        gestion_directores_grupo(headers)
    elif st.session_state.asignacion_seccion == "horas":
        configurar_horas_nivel(headers)
    elif st.session_state.asignacion_seccion == "dias":
        configurar_jornada_nivel(headers)
    elif st.session_state.asignacion_seccion == "niveles":
        configurar_niveles(headers)
    elif st.session_state.asignacion_seccion == "materias":
        gestionar_asignaturas(headers)
    elif st.session_state.asignacion_seccion == "grados":
        gestionar_grados(headers)
    elif st.session_state.asignacion_seccion == "festivos":
        gestion_festivos(headers)

def configurar_horario_curso(headers):
    st.write("**📖 Asignar Materias por Curso**")
    
    # 1. Obtener niveles
    response_niveles = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    niveles = response_niveles.json() if response_niveles.status_code == 200 else []
    
    if not niveles:
        st.warning("No hay niveles configurados.")
        return
    
    niveles_dict = {n['nombre']: n['id'] for n in niveles}
    
    # =============================================
    # OBTENER TODOS LOS CURSOS (SIN FILTRAR)
    # =============================================
    response_grados = requests.get(f"{SUPABASE_URL}/rest/v1/grados?order=curso.asc", headers=headers)
    
    if response_grados.status_code != 200:
        st.error(f"Error al consultar grados: {response_grados.status_code}")
        st.code(response_grados.text)
        return
    
    grados = response_grados.json()
    
    # =============================================
    # MOSTRAR TODOS LOS CURSOS (para depuración)
    # =============================================
    st.write("### 🔍 Cursos encontrados en la tabla 'grados'")
    
    if not grados:
        st.warning("⚠️ La tabla 'grados' está vacía")
        return
    
    # Mostrar tabla de cursos
    data = []
    for g in grados:
        data.append({
            "Curso": g.get('curso', '?'),
            "nivel_id": g.get('nivel_id', 'NULL'),
            "Nivel": next((n['nombre'] for n in niveles if n['id'] == g.get('nivel_id')), "Sin nivel")
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption(f"Total: {len(grados)} cursos")
    
    # =============================================
    # CREAR LISTA DE CURSOS DISPONIBLES (TODOS)
    # =============================================
    cursos_disponibles = []
    for g in grados:
        curso_nombre = g.get('curso')
        if curso_nombre:
            cursos_disponibles.append(curso_nombre)
    
    if not cursos_disponibles:
        st.warning("⚠️ No se encontraron cursos con la columna 'curso'")
        return
    
    cursos_disponibles.sort()
    
    st.write(f"**Cursos disponibles:** {cursos_disponibles}")
    st.divider()
    
    # 3. Selector de curso
    col1, col2 = st.columns([2, 1])
    with col1:
        curso = st.selectbox("Seleccionar curso", cursos_disponibles, key="curso_select_asignacion")
    
    # 4. Obtener nivel del curso
    nivel_curso_nombre = "Sin nivel"
    nivel_id = None
    
    for g in grados:
        if g.get('curso') == curso:
            nivel_id = g.get('nivel_id')
            if nivel_id:
                for n in niveles:
                    if n['id'] == nivel_id:
                        nivel_curso_nombre = n['nombre']
                        break
            break
    
    with col2:
        if nivel_id:
            st.info(f"📌 Nivel: **{nivel_curso_nombre}**")
        else:
            st.error(f"❌ El curso '{curso}' no tiene nivel asignado.")
            return
    
    if not nivel_id:
        st.error(f"❌ El curso '{curso}' no tiene nivel asignado.")
        return
    
    # 5. Obtener horas del nivel
    url_horas = f"{SUPABASE_URL}/rest/v1/horas_nivel?nivel_id=eq.{nivel_id}&order=orden.asc"
    response_horas = requests.get(url_horas, headers=headers)
    horas = response_horas.json() if response_horas.status_code == 200 else []
    
    if not horas:
        st.warning(f"No hay horas configuradas para el nivel '{nivel_curso_nombre}'.")
        return
    
    # 6. Obtener horario actual del curso
    url_horario = f"{SUPABASE_URL}/rest/v1/horario_base?curso=eq.{curso}&order=dia_semana.asc,orden_clase.asc"
    response_horario = requests.get(url_horario, headers=headers)
    horarios = response_horario.json() if response_horario.status_code == 200 else []
    
    # 7. Obtener docentes
    response_docentes = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
    docentes = response_docentes.json() if response_docentes.status_code == 200 else []
    docentes_dict = {d['documento_docente']: f"{d['nombre_docente']} {d['apellidos_docente']}" for d in docentes}
    lista_docentes = list(docentes_dict.keys())
    
    # 8. Obtener materias del nivel
    url_relaciones = f"{SUPABASE_URL}/rest/v1/materias_niveles?nivel_id=eq.{nivel_id}&select=materia_id"
    response_relaciones = requests.get(url_relaciones, headers=headers)
    
    materias = []
    if response_relaciones.status_code == 200:
        relaciones = response_relaciones.json()
        materia_ids = [r['materia_id'] for r in relaciones if r.get('materia_id')]
        if materia_ids:
            ids_str = ','.join([str(id) for id in materia_ids])
            url_materias = f"{SUPABASE_URL}/rest/v1/materias?id=in.({ids_str})&order=nombre.asc"
            response_materias = requests.get(url_materias, headers=headers)
            if response_materias.status_code == 200:
                materias = response_materias.json()
    
    opciones_materias = [""] + [m['nombre'] for m in materias]
    
    if not materias:
        st.warning("⚠️ No hay materias registradas para este nivel. Ve a 'Gestionar Asignaturas'.")
        return
    
    # Días
    dias = {1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves", 5: "Viernes", 6: "Sábado"}
    
    st.info(f"📊 {len(horas)} horas | {len(materias)} materias | {len(docentes)} docentes")
    
    # =============================================
    # TABLA CON DROPDOWNS
    # =============================================
    st.write("### ✏️ Asignar materias y docentes")
    
    with st.form(key=f"horario_form_{curso}"):
        for hora in horas:
            st.write(f"**{hora['orden']}. {str(hora['hora_inicio'])[:5]} - {str(hora['hora_fin'])[:5]}**")
            
            cols = st.columns(len(dias))
            for idx, (dia_num, dia_nombre) in enumerate(dias.items()):
                with cols[idx]:
                    st.write(f"📅 {dia_nombre}")
                    
                    existente = next((h for h in horarios if h['dia_semana'] == dia_num and h['orden_clase'] == hora['orden']), None)
                    key_base = f"{curso}_{dia_num}_{hora['orden']}_{idx}"
                    
                    # Materia
                    default_asignatura = existente.get('asignatura', '') if existente else ''
                    default_idx = 0
                    if default_asignatura in opciones_materias:
                        default_idx = opciones_materias.index(default_asignatura)
                    
                    asignatura = st.selectbox(
                        "Materia",
                        options=opciones_materias,
                        index=default_idx,
                        key=f"mat_{key_base}",
                        label_visibility="collapsed"
                    )
                    
                    # Docente
                    default_docente = existente.get('documento_docente', '') if existente else ''
                    default_idx_doc = 0
                    if default_docente and default_docente in lista_docentes:
                        default_idx_doc = lista_docentes.index(default_docente) + 1
                    
                    opciones_docentes = [""] + lista_docentes
                    docente = st.selectbox(
                        "Docente",
                        options=opciones_docentes,
                        index=default_idx_doc,
                        format_func=lambda x: docentes_dict.get(x, "Ninguno") if x else "Ninguno",
                        key=f"doc_{key_base}",
                        label_visibility="collapsed"
                    )
                    
                    # Salón
                    default_salon = existente.get('salon', '') if existente else ''
                    salon = st.text_input(
                        "Salón",
                        value=default_salon,
                        key=f"salon_{key_base}",
                        label_visibility="collapsed",
                        placeholder="Salón"
                    )
            
            st.divider()
        
        # Botón guardar
        submitted = st.form_submit_button("💾 Guardar horario", type="primary", use_container_width=True)
    
    # =============================================
    # PROCESAR GUARDADO
    # =============================================
    if submitted:
        with st.spinner("Guardando horario..."):
            guardados = 0
            eliminados = 0
            errores = 0
            
            for hora in horas:
                for dia_num, dia_nombre in dias.items():
                    key_base = f"{curso}_{dia_num}_{hora['orden']}_{list(dias.keys()).index(dia_num)}"
                    
                    asignatura = st.session_state.get(f"mat_{key_base}", "")
                    docente = st.session_state.get(f"doc_{key_base}", "")
                    salon = st.session_state.get(f"salon_{key_base}", "")
                    
                    existente = next((h for h in horarios if h['dia_semana'] == dia_num and h['orden_clase'] == hora['orden']), None)
                    
                    if asignatura and asignatura.strip():
                        data_horario = {
                            "curso": curso,
                            "nivel_id": nivel_id,
                            "dia_semana": dia_num,
                            "orden_clase": hora['orden'],
                            "hora_inicio": str(hora['hora_inicio']),
                            "hora_fin": str(hora['hora_fin']),
                            "asignatura": asignatura.strip(),
                            "documento_docente": docente if docente else None,
                            "salon": salon
                        }
                        try:
                            if existente:
                                requests.patch(
                                    f"{SUPABASE_URL}/rest/v1/horario_base?id=eq.{existente['id']}", 
                                    headers=headers,
                                    json=data_horario
                                )
                            else:
                                requests.post(
                                    f"{SUPABASE_URL}/rest/v1/horario_base",
                                    headers=headers,
                                    json=data_horario
                                )
                            guardados += 1
                        except Exception as e:
                            errores += 1
                    elif existente:
                        try:
                            requests.delete(
                                f"{SUPABASE_URL}/rest/v1/horario_base?id=eq.{existente['id']}",
                                headers=headers
                            )
                            eliminados += 1
                        except Exception as e:
                            errores += 1
            
            if errores > 0:
                st.warning(f"⚠️ {guardados} guardadas, {eliminados} eliminadas, {errores} errores.")
            else:
                st.success(f"✅ Horario guardado: {guardados} clases, {eliminados} eliminadas.")
                st.rerun()

def gestionar_grados(headers):
    st.subheader("📚 Gestionar Cursos (Grados)")
    st.caption("Crea, edita o elimina cursos y asígnales un nivel educativo.")
    
    # Obtener niveles
    response_niveles = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    if response_niveles.status_code != 200:
        st.error("Error al cargar niveles")
        return
    
    niveles = response_niveles.json()
    niveles_dict = {n['nombre']: n['id'] for n in niveles}
    nivel_nombres = [n['nombre'] for n in niveles]
    
    # Obtener grados
    response_grados = requests.get(f"{SUPABASE_URL}/rest/v1/grados?order=curso.asc", headers=headers)
    if response_grados.status_code != 200:
        st.error(f"Error al cargar grados: {response_grados.status_code}")
        st.code(response_grados.text)
        return
    
    grados = response_grados.json()
    
    # =============================================
    # MOSTRAR TABLA DE GRADOS
    # =============================================
    st.write("### 📋 Lista de cursos")
    
    if grados:
        data = []
        for g in grados:
            nivel_nombre = next((n['nombre'] for n in niveles if n['id'] == g['nivel_id']), "Sin nivel")
            data.append({
                "ID": g['id_grado'],
                "Curso": g['curso'],
                "Nivel": nivel_nombre
            })
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"Total: {len(grados)} cursos")
    else:
        st.info("No hay cursos registrados")
    
    st.divider()
    
    # =============================================
    # AGREGAR NUEVO GRADO
    # =============================================
    st.write("### ➕ Agregar nuevo curso")
    
    with st.form("nuevo_grado_form"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre del curso *")
        with col2:
            nivel_seleccionado = st.selectbox("Nivel *", nivel_nombres)
        
        submitted = st.form_submit_button("💾 Crear curso", type="primary")
        
        if submitted:
            if not nombre:
                st.error("❌ El nombre es obligatorio")
            else:
                nombre_upper = nombre.upper().strip()
                nivel_id = niveles_dict.get(nivel_seleccionado)
                
                if not nivel_id:
                    st.error("❌ Nivel no válido")
                else:
                    check_url = f"{SUPABASE_URL}/rest/v1/grados?curso=eq.{nombre_upper}"
                    check_resp = requests.get(check_url, headers=headers)
                    
                    if check_resp.status_code == 200 and check_resp.json():
                        st.error(f"❌ El curso '{nombre_upper}' ya existe")
                    else:
                        data = {"curso": nombre_upper, "nivel_id": nivel_id}
                        r = requests.post(f"{SUPABASE_URL}/rest/v1/grados", headers=headers, json=data)
                        
                        if r.status_code == 201:
                            st.success(f"✅ Curso '{nombre_upper}' creado correctamente")
                            st.rerun()
                        else:
                            st.error(f"❌ Error al crear: {r.status_code}")
                            st.code(r.text)
    
    # =============================================
    # ELIMINAR GRADO
    # =============================================
    if grados:
        st.divider()
        st.write("### 🗑️ Eliminar curso")
        st.caption("⚠️ Solo se puede eliminar si no está en uso (sin estudiantes asignados)")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            grado_eliminar = st.selectbox(
                "Seleccionar curso para eliminar",
                options=[f"{g['id_grado']} - {g['curso']}" for g in grados],
                key="eliminar_grado_select"
            )
        with col2:
            if st.button("🗑️ Eliminar", type="secondary", use_container_width=True):
                if grado_eliminar:
                    grado_id = int(grado_eliminar.split(' - ')[0])
                    grado_nombre = grado_eliminar.split(' - ')[1]
                    
                    check_url = f"{SUPABASE_URL}/rest/v1/estudiantes?curso=eq.{grado_nombre}&limit=1"
                    check_resp = requests.get(check_url, headers=headers)
                    
                    if check_resp.status_code == 200 and check_resp.json():
                        st.error(f"❌ No se puede eliminar '{grado_nombre}' porque tiene estudiantes asignados")
                    else:
                        r = requests.delete(
                            f"{SUPABASE_URL}/rest/v1/grados?id_grado=eq.{grado_id}",
                            headers=headers
                        )
                        if r.status_code == 204:
                            st.success(f"✅ Curso '{grado_nombre}' eliminado")
                            st.rerun()
                        else:
                            st.error(f"❌ Error al eliminar: {r.status_code}")

# ============================================
# FUNCIÓN 14: MOSTRAR SISTEMA
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
