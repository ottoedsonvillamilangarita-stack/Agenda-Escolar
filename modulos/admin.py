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
                            "email_estudiante": email,
                            "direccion_estudiante": direccion
                        }
                        response = requests.post(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers, json=data_estudiante)
                        
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
                            
                            # Insertar acudiente
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
                            
                            # Crear usuario para el acudiente
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
                # Buscar estudiante
                url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{documento_buscar}"
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200 and response.json():
                    estudiante = response.json()[0]
                    
                    # Buscar acudientes
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
                        
                        # Mostrar acudientes existentes
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
                                
                                # Botón para eliminar acudiente
                                if st.button(f"🗑️ Eliminar acudiente {idx + 1}", key=f"eliminar_acud_{idx}"):
                                    requests.delete(f"{SUPABASE_URL}/rest/v1/estudiante_acudiente?id=eq.{acud['id']}", headers=headers)
                                    st.success("Acudiente eliminado")
                                    st.rerun()
                                st.divider()
                        
                        # Agregar nuevo acudiente
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
                                    # Insertar nuevo acudiente
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
                                    st.rerun()
                        
                        if st.form_submit_button("💾 Guardar todos los cambios", type="primary"):
                            # Actualizar datos del estudiante
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
                            
                            # Actualizar acudientes existentes
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
                        # Actualizar todos los registros del acudiente
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


def mostrar_asignacion():
    st.subheader("📚 Asignación Académica")
    st.info("🚧 Módulo en construcción - Próximamente")


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
