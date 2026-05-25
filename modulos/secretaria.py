import streamlit as st
import requests
import pandas as pd
from utils import SUPABASE_URL, get_headers
from modulos.features.horarios import mostrar_horario_tabla

def mostrar(data):
    st.title("📋 Panel de Secretaria")
    st.write(f"Bienvenida, {data.get('username', 'Secretaria')}")
    
    headers = get_headers()
    
    st.divider()
    st.subheader("📌 Funciones disponibles")
    
    opcion = st.selectbox(
        "Seleccionar función",
        [
            "📊 Dashboard",
            "👨‍🎓 Gestión de Estudiantes",
            "👨‍🏫 Gestión de Docentes",
            "📚 Gestión de Cursos",
            "📅 Consultar Horarios",
            "📄 Certificados",
            "📊 Reportes"
        ]
    )
    
    st.divider()
    
    if opcion == "📊 Dashboard":
        mostrar_dashboard()
    elif opcion == "👨‍🎓 Gestión de Estudiantes":
        gestion_estudiantes()
    elif opcion == "👨‍🏫 Gestión de Docentes":
        gestion_docentes()
    elif opcion == "📚 Gestión de Cursos":
        gestion_cursos()
    elif opcion == "📅 Consultar Horarios":
        consultar_horarios()
    elif opcion == "📄 Certificados":
        st.info("🚧 Módulo en desarrollo")
    elif opcion == "📊 Reportes":
        st.info("🚧 Módulo en desarrollo")


def mostrar_dashboard():
    st.subheader("📊 Dashboard Secretaria")
    
    headers = get_headers()
    
    response_est = requests.get(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers)
    total_estudiantes = len(response_est.json()) if response_est.status_code == 200 else 0
    
    response_doc = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
    total_docentes = len(response_doc.json()) if response_doc.status_code == 200 else 0
    
    estudiantes = response_est.json() if response_est.status_code == 200 else []
    activos = len([e for e in estudiantes if e.get('activo', True) != False])
    inactivos = total_estudiantes - activos
    
    # Docentes activos (por ahora todos activos)
    docentes_activos = total_docentes
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("👨‍🎓 Total Estudiantes", total_estudiantes)
    col2.metric("✅ Estudiantes Activos", activos)
    col3.metric("❌ Estudiantes Inactivos", inactivos)
    col4.metric("👨‍🏫 Total Docentes", total_docentes)
    col5.metric("✅ Docentes Activos", docentes_activos)
    
    st.info("📌 Panel de gestión administrativa")


def gestion_estudiantes():
    st.subheader("👨‍🎓 Gestión de Estudiantes")
    
    headers = get_headers()
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Lista de Estudiantes", "➕ Matricular", "✏️ Editar", "🚫 Dar de Baja"])
    
    with tab1:
        response = requests.get(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers)
        
        if response.status_code == 200:
            estudiantes = response.json()
            if estudiantes:
                df = pd.DataFrame(estudiantes)
                columnas = ['nombre_estudiante', 'apellidos_estudiante', 'documento_estudiante', 'curso', 'nombre_acudiente']
                columnas_existentes = [col for col in columnas if col in df.columns]
                st.dataframe(df[columnas_existentes], use_container_width=True)
                st.caption(f"Total: {len(estudiantes)} estudiantes")
            else:
                st.info("No hay estudiantes registrados")
    
    with tab2:
        st.info("Completa todos los campos obligatorios (*)")
        
        with st.form("form_matricula", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Datos personales**")
                nombre = st.text_input("Nombre *")
                apellidos = st.text_input("Apellidos *")
                documento = st.text_input("Documento de identidad *")
                fecha_nacimiento = st.date_input("Fecha de nacimiento", value=None)
                curso = st.selectbox("Curso *", ["901", "902", "903", "1001", "1002", "1003", "1101"])
                direccion = st.text_input("Dirección")
                telefono = st.text_input("Teléfono")
                email = st.text_input("Email")
            
            with col2:
                st.markdown("**Datos del acudiente**")
                nombre_acudiente = st.text_input("Nombre del acudiente *")
                documento_acudiente = st.text_input("Documento del acudiente *")
                parentesco = st.selectbox("Parentesco", ["", "Padre", "Madre", "Tío", "Tía", "Abuelo", "Abuela", "Hermano", "Hermana", "Otro"])
                telefono_acudiente = st.text_input("Teléfono del acudiente")
                email_acudiente = st.text_input("Email del acudiente")
                direccion_acudiente = st.text_input("Dirección del acudiente")
            
            st.markdown("**Datos de matrícula**")
            col3, col4 = st.columns(2)
            with col3:
                fecha_matricula = st.date_input("Fecha de matrícula")
            with col4:
                observaciones = st.text_area("Observaciones", height=68)
            
            submitted = st.form_submit_button("💾 Registrar Estudiante", type="primary")
            
            if submitted:
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
                            "fecha_nacimiento": str(fecha_nacimiento) if fecha_nacimiento else None,
                            "curso": curso,
                            "direccion_estudiante": direccion,
                            "telefono_estudiante": telefono,
                            "email_estudiante": email,
                            "nombre_acudiente": nombre_acudiente,
                            "documento_acudiente": documento_acudiente,
                            "parentesco": parentesco,
                            "telefono_acudiente": telefono_acudiente,
                            "email_acudiente": email_acudiente,
                            "direccion_acudiente": direccion_acudiente,
                            "fecha_matricula": str(fecha_matricula),
                            "observaciones": observaciones,
                            "activo": True
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
                            
                            st.success(f"✅ Estudiante {nombre} {apellidos} matriculado exitosamente")
                            st.info(f"🔑 Usuario: {documento} | Contraseña: demo2026")
                            st.balloons()
                        else:
                            st.error(f"Error al registrar: {response.status_code}")
    
    with tab3:
        documento_buscar = st.text_input("Documento de identidad del estudiante", key="buscar_editar")
        
        if documento_buscar:
            url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{documento_buscar}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200 and response.json():
                estudiante = response.json()[0]
                
                with st.form("form_editar", clear_on_submit=False):
                    st.success(f"Editando: {estudiante.get('nombre_estudiante')} {estudiante.get('apellidos_estudiante')}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Datos personales**")
                        nombre = st.text_input("Nombre", value=estudiante.get('nombre_estudiante', ''))
                        apellidos = st.text_input("Apellidos", value=estudiante.get('apellidos_estudiante', ''))
                        st.text_input("Documento", value=estudiante.get('documento_estudiante', ''), disabled=True)
                        curso = st.selectbox("Curso", ["901", "902", "903", "1001", "1002", "1003", "1101"], 
                                            index=["901","902","903","1001","1002","1003","1101"].index(estudiante.get('curso', '901')))
                        telefono = st.text_input("Teléfono", value=estudiante.get('telefono_estudiante', ''))
                        email = st.text_input("Email", value=estudiante.get('email_estudiante', ''))
                    
                    with col2:
                        st.markdown("**Datos del acudiente**")
                        nombre_acudiente = st.text_input("Nombre del acudiente", value=estudiante.get('nombre_acudiente', ''))
                        documento_acudiente = st.text_input("Documento del acudiente", value=estudiante.get('documento_acudiente', ''))
                        parentesco = st.selectbox("Parentesco", ["", "Padre", "Madre", "Tío", "Tía", "Abuelo", "Abuela", "Otro"],
                                                 index=["", "Padre", "Madre", "Tío", "Tía", "Abuelo", "Abuela", "Otro"].index(estudiante.get('parentesco', '')))
                        telefono_acudiente = st.text_input("Teléfono del acudiente", value=estudiante.get('telefono_acudiente', ''))
                        email_acudiente = st.text_input("Email del acudiente", value=estudiante.get('email_acudiente', ''))
                    
                    activo = st.checkbox("Activo", value=estudiante.get('activo', True))
                    
                    submitted = st.form_submit_button("💾 Guardar Cambios", type="primary")
                    
                    if submitted:
                        data_update = {
                            "nombre_estudiante": nombre,
                            "apellidos_estudiante": apellidos,
                            "curso": curso,
                            "telefono_estudiante": telefono,
                            "email_estudiante": email,
                            "nombre_acudiente": nombre_acudiente,
                            "documento_acudiente": documento_acudiente,
                            "parentesco": parentesco,
                            "telefono_acudiente": telefono_acudiente,
                            "email_acudiente": email_acudiente,
                            "activo": activo
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
    
    with tab4:
        documento = st.text_input("Documento de identidad del estudiante", key="buscar_baja")
        
        if documento:
            url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{documento}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200 and response.json():
                estudiante = response.json()[0]
                nombre = estudiante.get('nombre_estudiante')
                apellidos = estudiante.get('apellidos_estudiante')
                curso = estudiante.get('curso')
                
                st.warning(f"⚠️ Estás a punto de dar de baja a: **{nombre} {apellidos}** (Curso: {curso})")
                
                motivo = st.text_area("Motivo de la baja")
                fecha_baja = st.date_input("Fecha de baja")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Confirmar Baja", type="primary"):
                        data_update = {
                            "activo": False,
                            "fecha_baja": str(fecha_baja),
                            "motivo_baja": motivo
                        }
                        update_url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{documento}"
                        response_update = requests.patch(update_url, headers=headers, json=data_update)
                        
                        if response_update.status_code == 200:
                            st.success(f"✅ Estudiante {nombre} {apellidos} dado de baja")
                            st.rerun()
                        else:
                            st.error("Error al dar de baja")
                with col2:
                    if st.button("❌ Cancelar"):
                        st.rerun()
            elif response.status_code == 200:
                st.warning("No se encontró un estudiante con ese documento")


def gestion_docentes():
    st.subheader("👨‍🏫 Gestión de Docentes")
    
    headers = get_headers()
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Lista de Docentes", "➕ Contratar", "✏️ Editar", "🚫 Retirar"])
    
    with tab1:
        response = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
        
        if response.status_code == 200:
            docentes = response.json()
            if docentes:
                df = pd.DataFrame(docentes)
                st.dataframe(df, use_container_width=True)
                st.caption(f"Total: {len(docentes)} docentes")
            else:
                st.info("No hay docentes registrados")
    
    with tab2:
        st.info("Completa todos los campos obligatorios (*)")
        
        with st.form("form_contratar", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Datos personales**")
                nombre = st.text_input("Nombre *")
                apellidos = st.text_input("Apellidos *")
                documento = st.text_input("Documento de identidad *")
                fecha_nacimiento = st.date_input("Fecha de nacimiento", value=None)
                sexo = st.selectbox("Sexo", ["", "Masculino", "Femenino"])
                direccion = st.text_input("Dirección")
                telefono = st.text_input("Teléfono")
                email = st.text_input("Email")
            
            with col2:
                st.markdown("**Datos profesionales**")
                titulo = st.text_input("Título profesional")
                especializacion = st.text_input("Especialización")
                tipo_contrato = st.selectbox("Tipo de contrato", ["", "Planta", "Contrato", "Cátedra", "Ocasional"])
                fecha_ingreso = st.date_input("Fecha de ingreso")
                salario = st.number_input("Salario", min_value=0, step=100000)
                observaciones = st.text_area("Observaciones", height=68)
            
            submitted = st.form_submit_button("💾 Contratar Docente", type="primary")
            
            if submitted:
                if not all([nombre, apellidos, documento]):
                    st.error("❌ Completa todos los campos obligatorios (*)")
                else:
                    check_url = f"{SUPABASE_URL}/rest/v1/docentes?documento_docente=eq.{documento}"
                    check_response = requests.get(check_url, headers=headers)
                    
                    if check_response.status_code == 200 and check_response.json():
                        st.error(f"❌ Ya existe un docente con el documento {documento}")
                    else:
                        data_docente = {
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
                            "salario": salario if salario > 0 else None,
                            "observaciones": observaciones,
                            "activo": True
                        }
                        
                        response = requests.post(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers, json=data_docente)
                        
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
                            
                            st.success(f"✅ Docente {nombre} {apellidos} contratado exitosamente")
                            st.info(f"🔑 Usuario: {username} | Contraseña: demo2026")
                            st.balloons()
                        else:
                            st.error(f"Error al registrar: {response.status_code}")
    
    with tab3:
        documento_buscar = st.text_input("Documento de identidad del docente", key="buscar_editar_docente")
        
        if documento_buscar:
            url = f"{SUPABASE_URL}/rest/v1/docentes?documento_docente=eq.{documento_buscar}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200 and response.json():
                docente = response.json()[0]
                
                with st.form("form_editar_docente", clear_on_submit=False):
                    st.success(f"Editando: {docente.get('nombre_docente')} {docente.get('apellidos_docente')}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Datos personales**")
                        nombre = st.text_input("Nombre", value=docente.get('nombre_docente', ''))
                        apellidos = st.text_input("Apellidos", value=docente.get('apellidos_docente', ''))
                        st.text_input("Documento", value=docente.get('documento_docente', ''), disabled=True)
                        telefono = st.text_input("Teléfono", value=docente.get('telefono_docente', ''))
                        email = st.text_input("Email", value=docente.get('email_docente', ''))
                        direccion = st.text_input("Dirección", value=docente.get('direccion_docente', ''))
                    
                    with col2:
                        st.markdown("**Datos profesionales**")
                        titulo = st.text_input("Título", value=docente.get('titulo', ''))
                        especializacion = st.text_input("Especialización", value=docente.get('especializacion', ''))
                        tipo_contrato = st.selectbox("Tipo de contrato", ["", "Planta", "Contrato", "Cátedra", "Ocasional"],
                                                    index=["", "Planta", "Contrato", "Cátedra", "Ocasional"].index(docente.get('tipo_contrato', '')))
                    
                    activo = st.checkbox("Activo", value=docente.get('activo', True))
                    
                    submitted = st.form_submit_button("💾 Guardar Cambios", type="primary")
                    
                    if submitted:
                        data_update = {
                            "nombre_docente": nombre,
                            "apellidos_docente": apellidos,
                            "telefono_docente": telefono,
                            "email_docente": email,
                            "direccion_docente": direccion,
                            "titulo": titulo,
                            "especializacion": especializacion,
                            "tipo_contrato": tipo_contrato,
                            "activo": activo
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
    
    with tab4:
        documento = st.text_input("Documento de identidad del docente", key="buscar_retiro")
        
        if documento:
            url = f"{SUPABASE_URL}/rest/v1/docentes?documento_docente=eq.{documento}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200 and response.json():
                docente = response.json()[0]
                nombre = docente.get('nombre_docente')
                apellidos = docente.get('apellidos_docente')
                
                st.warning(f"⚠️ Estás a punto de retirar a: **{nombre} {apellidos}**")
                
                motivo = st.text_area("Motivo del retiro")
                fecha_retiro = st.date_input("Fecha de retiro")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Confirmar Retiro", type="primary"):
                        data_update = {
                            "activo": False,
                            "fecha_retiro": str(fecha_retiro),
                            "motivo_retiro": motivo
                        }
                        update_url = f"{SUPABASE_URL}/rest/v1/docentes?documento_docente=eq.{documento}"
                        response_update = requests.patch(update_url, headers=headers, json=data_update)
                        
                        if response_update.status_code == 200:
                            st.success(f"✅ Docente {nombre} {apellidos} retirado")
                            st.rerun()
                        else:
                            st.error("Error al retirar")
                with col2:
                    if st.button("❌ Cancelar"):
                        st.rerun()
            elif response.status_code == 200:
                st.warning("No se encontró un docente con ese documento")


def gestion_cursos():
    st.subheader("📚 Gestión de Cursos")
    
    cursos = ["901", "902", "903", "1001", "1002", "1003", "1101"]
    
    for curso in cursos:
        with st.expander(f"Curso {curso}"):
            st.write(f"**Asignaturas del curso {curso}:**")
            headers = get_headers()
            url = f"{SUPABASE_URL}/rest/v1/docentes?curso=eq.{curso}&select=asignatura,nombre_docente"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                materias = response.json()
                if materias:
                    for m in materias:
                        st.write(f"- {m.get('asignatura')}: {m.get('nombre_docente')}")
                else:
                    st.write("Sin asignaturas asignadas")


def consultar_horarios():
    st.subheader("📅 Consultar Horarios")
    
    headers = get_headers()
    
    tipo = st.radio("Ver horario de:", ["Curso", "Docente"], key="horario_tipo")
    
    if tipo == "Curso":
        cursos = ["901", "902", "903", "1001", "1002", "1003", "1101"]
        curso = st.selectbox("Seleccionar curso", cursos, key="horario_curso")
        
        if st.button("Ver horario", type="primary", key="ver_horario_curso"):
            mostrar_horario_tabla(curso, headers)
    
    else:
        url = f"{SUPABASE_URL}/rest/v1/docentes"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            docentes = response.json()
            docentes_opciones = [f"{d['nombre_docente']} {d['apellidos_docente']}" for d in docentes]
            docente_seleccionado = st.selectbox("Seleccionar docente", docentes_opciones, key="horario_docente")
            
            if st.button("Ver horario", type="primary", key="ver_horario_docente"):
                idx = docentes_opciones.index(docente_seleccionado)
                documento_docente = docentes[idx]['documento_docente']
                
                url_horario = f"{SUPABASE_URL}/rest/v1/horario_base?documento_docente=eq.{documento_docente}"
                response_horario = requests.get(url_horario, headers=headers)
                
                if response_horario.status_code == 200:
                    horarios = response_horario.json()
                    if horarios:
                        cursos_dict = {}
                        for h in horarios:
                            curso = h.get('curso')
                            if curso not in cursos_dict:
                                cursos_dict[curso] = []
                            cursos_dict[curso].append(h)
                        
                        for curso, clases in cursos_dict.items():
                            st.write(f"**Curso {curso}**")
                            mostrar_horario_tabla(curso, headers)
                    else:
                        st.info("Este docente no tiene horario asignado")
                else:
                    st.info("No se pudo cargar el horario del docente")
