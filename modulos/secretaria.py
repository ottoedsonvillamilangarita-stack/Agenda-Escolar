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
            "➕ Matricular Estudiante",
            "✏️ Editar Estudiante",
            "🚫 Dar de Baja",
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
    elif opcion == "➕ Matricular Estudiante":
        matricular_estudiante()
    elif opcion == "✏️ Editar Estudiante":
        editar_estudiante()
    elif opcion == "🚫 Dar de Baja":
        dar_baja_estudiante()
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
    
    # Contar estudiantes activos e inactivos
    estudiantes = response_est.json() if response_est.status_code == 200 else []
    activos = len([e for e in estudiantes if e.get('activo', True) != False])
    inactivos = total_estudiantes - activos
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👨‍🎓 Total Estudiantes", total_estudiantes)
    col2.metric("✅ Activos", activos)
    col3.metric("❌ Inactivos", inactivos)
    col4.metric("👨‍🏫 Docentes", total_docentes)
    
    st.info("📌 Panel de gestión administrativa")


def gestion_estudiantes():
    st.subheader("👨‍🎓 Lista de Estudiantes")
    
    headers = get_headers()
    response = requests.get(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers)
    
    if response.status_code == 200:
        estudiantes = response.json()
        if estudiantes:
            df = pd.DataFrame(estudiantes)
            # Mostrar solo columnas relevantes
            columnas = ['nombre_estudiante', 'apellidos_estudiante', 'documento_estudiante', 'curso', 'nombre_acudiente']
            columnas_existentes = [col for col in columnas if col in df.columns]
            st.dataframe(df[columnas_existentes], use_container_width=True)
            st.caption(f"Total: {len(estudiantes)} estudiantes")
        else:
            st.info("No hay estudiantes registrados")


def matricular_estudiante():
    st.subheader("➕ Matricular Nuevo Estudiante")
    st.info("Completa todos los campos obligatorios (*)")
    
    headers = get_headers()
    
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
                        # Crear usuario para login
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


def editar_estudiante():
    st.subheader("✏️ Editar Estudiante")
    
    headers = get_headers()
    
    # Buscar estudiante
    documento_buscar = st.text_input("Documento de identidad del estudiante")
    
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
                    documento_edit = st.text_input("Documento", value=estudiante.get('documento_estudiante', ''), disabled=True)
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


def dar_baja_estudiante():
    st.subheader("🚫 Dar de Baja Estudiante")
    
    headers = get_headers()
    
    documento = st.text_input("Documento de identidad del estudiante")
    
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
    response = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
    
    if response.status_code == 200:
        docentes = response.json()
        if docentes:
            df = pd.DataFrame(docentes)
            st.dataframe(df, use_container_width=True)
            st.caption(f"Total: {len(docentes)} docentes")
        else:
            st.info("No hay docentes registrados")


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
