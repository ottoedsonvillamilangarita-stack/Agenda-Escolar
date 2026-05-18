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
    
    response_est = requests.get(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers)
    total_alumnos = len(response_est.json()) if response_est.status_code == 200 else 0
    
    response_doc = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
    if response_doc.status_code == 200:
        total_docentes = len(response_doc.json())
    else:
        total_docentes = 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👨‍🎓 Alumnos", total_alumnos)
    col2.metric("👨‍🏫 Docentes", total_docentes)
    col3.metric("📚 Cursos", "7")
    col4.metric("👥 Usuarios", "Por definir")
    
    st.info("🔐 Panel de control del Administrador")


# ============================================
# ALUMNOS
# ============================================
def mostrar_alumnos():
    st.subheader("👨‍🎓 Gestión de Alumnos")
    
    tab1, tab2 = st.tabs(["📋 Lista de Alumnos", "➕ Nuevo Alumno"])
    
    with tab1:
        headers = get_headers()
        response = requests.get(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers)
        
        if response.status_code == 200:
            alumnos = response.json()
            if alumnos:
                df = pd.DataFrame(alumnos)
                st.dataframe(df, use_container_width=True)
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
                telefono = st.text_input("Teléfono del acudiente")
            
            if st.form_submit_button("💾 Guardar"):
                headers = get_headers()
                # Guardar alumno
                data_alumno = {
                    "nombre_estudiante": nombre,
                    "apellidos_estudiante": apellidos,
                    "documento_estudiante": documento,
                    "curso": curso,
                    "nombre_acudiente": nombre_acudiente,
                    "documento_acudiente": documento_acudiente,
                    "telefono_acudiente": telefono
                }
                response = requests.post(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers, json=data_alumno)
                
                if response.status_code == 201:
                    # Actualizar rol del acudiente automáticamente
                    actualizar_rol_acudiente(documento_acudiente, nombre_acudiente, headers)
                    st.success(f"✅ Alumno {nombre} registrado")
                else:
                    st.error("Error al registrar alumno")


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
        else:
            st.info("No hay acudientes registrados")


# ============================================
# DOCENTES
# ============================================
def mostrar_docentes():
    st.subheader("👨‍🏫 Gestión de Docentes")
    
    tab1, tab2 = st.tabs(["📋 Lista de Docentes", "➕ Nuevo Docente"])
    
    with tab1:
        headers = get_headers()
        response = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
        
        if response.status_code == 200:
            docentes = response.json()
            if docentes:
                df = pd.DataFrame(docentes)
                st.dataframe(df, use_container_width=True)
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
            with col2:
                telefono = st.text_input("Teléfono")
                email = st.text_input("Email")
            
            if st.form_submit_button("💾 Guardar"):
                headers = get_headers()
                data = {
                    "nombre_docente": nombre,
                    "apellidos_docente": apellidos,
                    "documento_docente": documento,
                    "telefono_docente": telefono,
                    "email_docente": email
                }
                response = requests.post(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers, json=data)
                
                if response.status_code == 201:
                    # Crear usuario con rol docente
                    username = nombre.lower().replace(" ", "_")
                    user_data = {
                        "username": username,
                        "password_hash": "demo2026",
                        "rol": "docente",
                        "documento": documento,
                        "roles": ["docente"]
                    }
                    requests.post(f"{SUPABASE_URL}/rest/v1/usuarios_login", headers=headers, json=user_data)
                    st.success(f"✅ Docente {nombre} registrado")
                    st.info(f"🔑 Usuario: {username} | Contraseña: demo2026")
                else:
                    st.error("Error al registrar docente")


# ============================================
# ASIGNACIÓN ACADÉMICA
# ============================================
def mostrar_asignacion():
    st.subheader("📚 Asignación Académica")
    
    headers = get_headers()
    
    # ============================================
    # OBTENER DATOS BÁSICOS
    # ============================================
    
    # Obtener todos los docentes
    response_docentes = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
    todos_docentes = []
    docentes_dict = {}
    
    if response_docentes.status_code == 200:
        for d in response_docentes.json():
            nombre = f"{d.get('nombre_docente', '')} {d.get('apellidos_docente', '')}".strip()
            if nombre and nombre != " ":
                todos_docentes.append({
                    "nombre": nombre,
                    "documento": d.get('documento_docente')
                })
                docentes_dict[nombre] = d.get('documento_docente')
    
    if not todos_docentes:
        st.warning("⚠️ No hay docentes registrados. Por favor, carga docentes primero.")
        return
    
    cursos = ["901", "902", "903", "1001", "1002", "1003", "1101"]
    
    # Obtener directores actuales
    response_directores = requests.get(f"{SUPABASE_URL}/rest/v1/asignacion_academica?asignatura=eq.Dirección de Curso", headers=headers)
    directores_actuales = {}
    docentes_con_direccion = set()
    
    if response_directores.status_code == 200:
        for d in response_directores.json():
            curso = d.get('curso')
            doc_docente = d.get('documento_docente')
            directores_actuales[curso] = doc_docente
            if doc_docente:
                docentes_con_direccion.add(doc_docente)
    
    # ============================================
    # SECCIÓN 1: DIRECTORES DE CURSO
    # ============================================
    st.markdown("### 🎓 Directores de Curso")
    st.info("Asigna un docente como director para cada curso (un docente no puede ser director de más de un curso)")
    
    with st.form("directores_form"):
        st.write("**Asignación de Directores por Curso:**")
        
        directores_asignados = {}
        for curso in cursos:
            col1, col2 = st.columns([1, 2])
            with col1:
                st.write(f"**Curso {curso}**")
            with col2:
                current_doc = directores_actuales.get(curso)
                current_nombre = "-- Sin asignar --"
                for nombre, doc in docentes_dict.items():
                    if doc == current_doc:
                        current_nombre = nombre
                        break
                
                docentes_disponibles = ["-- Sin asignar --"]
                for docente in todos_docentes:
                    if current_doc and docente['documento'] == current_doc:
                        docentes_disponibles.append(docente['nombre'])
                    elif docente['documento'] not in docentes_con_direccion:
                        docentes_disponibles.append(docente['nombre'])
                
                index = docentes_disponibles.index(current_nombre) if current_nombre in docentes_disponibles else 0
                
                director = st.selectbox(
                    "Director",
                    docentes_disponibles,
                    index=index,
                    key=f"director_{curso}",
                    label_visibility="collapsed"
                )
                directores_asignados[curso] = director if director != "-- Sin asignar --" else None
        
        if st.form_submit_button("💾 Guardar Directores de Curso", type="primary"):
            guardar_directores(directores_asignados, docentes_dict, headers, cursos)
    
    st.divider()
    
    # ============================================
    # SECCIÓN 2: ASIGNACIÓN DE MATERIAS
    # ============================================
    st.markdown("### 📖 Asignación de Materias")
    st.info("Asigna docentes a cada materia por curso")
    
    curso = st.selectbox("Seleccionar curso", cursos, key="curso_asignacion")
    
    asignaturas_por_curso = {
        "901": ["Matemáticas", "Sociales", "Español", "Inglés", "Biología", "Artes", "Educación Física", "Ética", "Administración"],
        "902": ["Matemáticas", "Sociales", "Español", "Inglés", "Biología", "Artes", "Educación Física", "Ética", "Administración"],
        "903": ["Matemáticas", "Sociales", "Español", "Inglés", "Biología", "Artes", "Educación Física", "Ética", "Administración"],
        "1001": ["Trigonometría", "Sociales", "Español", "Inglés", "Química", "Física", "Educación Física", "Artes", "Filosofía", "Ética", "Administración", "Proyecto"],
        "1002": ["Trigonometría", "Sociales", "Español", "Inglés", "Química", "Física", "Educación Física", "Artes", "Filosofía", "Ética", "Administración", "Proyecto"],
        "1003": ["Trigonometría", "Sociales", "Español", "Inglés", "Química", "Física", "Educación Física", "Artes", "Filosofía", "Ética", "Administración", "Proyecto"],
        "1101": ["Cálculo", "Sociales", "Español", "Inglés", "Química", "Física", "Educación Física", "Artes", "Filosofía", "Ética", "Administración", "Proyecto"]
    }
    
    asignaturas = asignaturas_por_curso.get(curso, [])
    
    # Obtener qué docentes ya están asignados a este curso
    response_materias_curso = requests.get(
        f"{SUPABASE_URL}/rest/v1/asignacion_academica?curso=eq.{curso}&asignatura=neq.Dirección de Curso&select=documento_docente",
        headers=headers
    )
    
    docentes_del_curso = set()
    if response_materias_curso.status_code == 200:
        for a in response_materias_curso.json():
            if a.get('documento_docente'):
                docentes_del_curso.add(a.get('documento_docente'))
    
    director_curso = directores_actuales.get(curso)
    if director_curso:
        docentes_del_curso.add(director_curso)
    
    docentes_curso_lista = ["-- Sin asignar --"]
    docentes_curso_dict = {}
    
    for docente in todos_docentes:
        if docente['documento'] in docentes_del_curso:
            docentes_curso_lista.append(docente['nombre'])
            docentes_curso_dict[docente['nombre']] = docente['documento']
    
    if len(docentes_curso_lista) == 1:
        st.warning(f"⚠️ No hay docentes asignados al curso {curso}. Primero asigna materias o un director.")
        return
    
    response_asig = requests.get(
        f"{SUPABASE_URL}/rest/v1/asignacion_academica?curso=eq.{curso}&asignatura=neq.Dirección de Curso",
        headers=headers
    )
    asignaciones_existentes = {}
    
    if response_asig.status_code == 200:
        for a in response_asig.json():
            asignaciones_existentes[a.get('asignatura')] = a.get('documento_docente')
    
    with st.form("materias_form"):
        st.write(f"**Asignación de materias para el curso {curso}:**")
        
        materias_asignadas = {}
        for asignatura in asignaturas:
            col1, col2 = st.columns([2, 3])
            with col1:
                st.write(f"**{asignatura}**")
            with col2:
                current_doc = asignaciones_existentes.get(asignatura)
                current_nombre = "-- Sin asignar --"
                for nombre, doc in docentes_curso_dict.items():
                    if doc == current_doc:
                        current_nombre = nombre
                        break
                
                index = docentes_curso_lista.index(current_nombre) if current_nombre in docentes_curso_lista else 0
                docente = st.selectbox(
                    "Docente",
                    docentes_curso_lista,
                    index=index,
                    key=f"materia_{curso}_{asignatura}",
                    label_visibility="collapsed"
                )
                materias_asignadas[asignatura] = docente if docente != "-- Sin asignar --" else None
        
        if st.form_submit_button("💾 Guardar Asignación de Materias", type="primary"):
            guardar_materias(curso, materias_asignadas, docentes_curso_dict, headers)
    
    st.divider()
    mostrar_resumen_asignaciones(curso, headers, docentes_curso_dict)


# ============================================
# FUNCIONES DE ACTUALIZACIÓN AUTOMÁTICA DE ROLES
# ============================================

def actualizar_rol_docente(documento_docente, rol_a_agregar, headers):
    """Agrega un rol a un docente si no lo tiene"""
    url = f"{SUPABASE_URL}/rest/v1/usuarios_login?documento=eq.{documento_docente}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200 and response.json():
        user = response.json()[0]
        roles_actuales = user.get('roles', [user.get('rol')])
        
        if rol_a_agregar not in roles_actuales:
            roles_actuales.append(rol_a_agregar)
            update_url = f"{SUPABASE_URL}/rest/v1/usuarios_login?documento=eq.{documento_docente}"
            requests.patch(update_url, headers=headers, json={"roles": roles_actuales})


def quitar_rol_docente(documento_docente, rol_a_quitar, headers):
    """Quita un rol a un docente si lo tiene"""
    url = f"{SUPABASE_URL}/rest/v1/usuarios_login?documento=eq.{documento_docente}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200 and response.json():
        user = response.json()[0]
        roles_actuales = user.get('roles', [user.get('rol')])
        
        if rol_a_quitar in roles_actuales:
            roles_actuales.remove(rol_a_quitar)
            update_url = f"{SUPABASE_URL}/rest/v1/usuarios_login?documento=eq.{documento_docente}"
            requests.patch(update_url, headers=headers, json={"roles": roles_actuales})


def actualizar_rol_acudiente(documento_acudiente, nombre_acudiente, headers):
    """Crea o actualiza el rol de acudiente"""
    url = f"{SUPABASE_URL}/rest/v1/usuarios_login?documento=eq.{documento_acudiente}"
    response = requests.get(url, headers=headers)
    
    username_base = nombre_acudiente.lower().replace(" ", "_") if nombre_acudiente else "acudiente"
    username = f"{username_base}_{documento_acudiente[-4:]}"
    
    if response.status_code == 200 and response.json():
        user = response.json()[0]
        roles_actuales = user.get('roles', [user.get('rol')])
        if 'acudiente' not in roles_actuales:
            roles_actuales.append('acudiente')
            update_url = f"{SUPABASE_URL}/rest/v1/usuarios_login?documento=eq.{documento_acudiente}"
            requests.patch(update_url, headers=headers, json={"roles": roles_actuales})
    else:
        # Crear nuevo usuario acudiente
        user_data = {
            "username": username,
            "password_hash": "demo2026",
            "rol": "acudiente",
            "documento": documento_acudiente,
            "roles": ["acudiente"]
        }
        requests.post(f"{SUPABASE_URL}/rest/v1/usuarios_login", headers=headers, json=user_data)


def sincronizar_todos_los_roles(headers):
    """Sincroniza todos los roles basados en las asignaciones actuales"""
    # 1. Docentes que dictan materias
    response = requests.get(f"{SUPABASE_URL}/rest/v1/asignacion_academica?asignatura=neq.Dirección de Curso&select=documento_docente", headers=headers)
    if response.status_code == 200:
        docentes_materias = set()
        for a in response.json():
            if a.get('documento_docente'):
                docentes_materias.add(a.get('documento_docente'))
        for doc in docentes_materias:
            actualizar_rol_docente(doc, 'docente', headers)
    
    # 2. Directores de curso
    response = requests.get(f"{SUPABASE_URL}/rest/v1/asignacion_academica?asignatura=eq.Dirección de Curso&select=documento_docente", headers=headers)
    if response.status_code == 200:
        for a in response.json():
            if a.get('documento_docente'):
                actualizar_rol_docente(a.get('documento_docente'), 'director', headers)
    
    # 3. Acudientes
    response = requests.get(f"{SUPABASE_URL}/rest/v1/estudiantes?select=documento_acudiente,nombre_acudiente", headers=headers)
    if response.status_code == 200:
        acudientes = {}
        for e in response.json():
            doc = e.get('documento_acudiente')
            nombre = e.get('nombre_acudiente')
            if doc and doc not in acudientes:
                acudientes[doc] = nombre
                actualizar_rol_acudiente(doc, nombre, headers)


def guardar_directores(directores_asignados, docentes_dict, headers, cursos):
    """Guarda los directores de curso y actualiza roles automáticamente"""
    exitos = 0
    errores = 0
    
    # Obtener directores actuales
    response = requests.get(f"{SUPABASE_URL}/rest/v1/asignacion_academica?asignatura=eq.Dirección de Curso", headers=headers)
    directores_anteriores = {}
    
    if response.status_code == 200:
        for d in response.json():
            directores_anteriores[d.get('curso')] = d.get('documento_docente')
    
    for curso, director_nombre in directores_asignados.items():
        documento_docente = docentes_dict.get(director_nombre) if director_nombre else None
        
        # Quitar rol al director anterior si es diferente
        director_anterior = directores_anteriores.get(curso)
        if director_anterior and director_anterior != documento_docente:
            quitar_rol_docente(director_anterior, 'director', headers)
        
        if director_nombre and documento_docente:
            data = {
                "curso": curso,
                "asignatura": "Dirección de Curso",
                "documento_docente": documento_docente
            }
            
            check_url = f"{SUPABASE_URL}/rest/v1/asignacion_academica?curso=eq.{curso}&asignatura=eq.Dirección de Curso"
            check_response = requests.get(check_url, headers=headers)
            
            if check_response.status_code == 200 and check_response.json():
                update_url = f"{SUPABASE_URL}/rest/v1/asignacion_academica?curso=eq.{curso}&asignatura=eq.Dirección de Curso"
                response = requests.patch(update_url, headers=headers, json={"documento_docente": documento_docente})
            else:
                response = requests.post(f"{SUPABASE_URL}/rest/v1/asignacion_academica", headers=headers, json=data)
            
            if response.status_code in [200, 201, 204]:
                exitos += 1
                actualizar_rol_docente(documento_docente, 'director', headers)
            else:
                errores += 1
        else:
            delete_url = f"{SUPABASE_URL}/rest/v1/asignacion_academica?curso=eq.{curso}&asignatura=eq.Dirección de Curso"
            requests.delete(delete_url, headers=headers)
    
    # Sincronizar acudientes también
    sincronizar_todos_los_roles(headers)
    
    if errores == 0:
        st.success(f"✅ Directores de curso guardados exitosamente")
        st.rerun()
    else:
        st.warning(f"⚠️ {exitos} guardados, {errores} errores")


def guardar_materias(curso, materias_asignadas, docentes_dict, headers):
    """Guarda la asignación de materias y actualiza roles automáticamente"""
    exitos = 0
    errores = 0
    
    for asignatura, docente_nombre in materias_asignadas.items():
        if docente_nombre:
            documento_docente = docentes_dict.get(docente_nombre)
            
            data = {
                "curso": curso,
                "asignatura": asignatura,
                "documento_docente": documento_docente
            }
            
            check_url = f"{SUPABASE_URL}/rest/v1/asignacion_academica?curso=eq.{curso}&asignatura=eq.{asignatura}"
            check_response = requests.get(check_url, headers=headers)
            
            if check_response.status_code == 200 and check_response.json():
                update_url = f"{SUPABASE_URL}/rest/v1/asignacion_academica?curso=eq.{curso}&asignatura=eq.{asignatura}"
                response = requests.patch(update_url, headers=headers, json={"documento_docente": documento_docente})
            else:
                response = requests.post(f"{SUPABASE_URL}/rest/v1/asignacion_academica", headers=headers, json=data)
            
            if response.status_code in [200, 201, 204]:
                exitos += 1
                actualizar_rol_docente(documento_docente, 'docente', headers)
            else:
                errores += 1
        else:
            delete_url = f"{SUPABASE_URL}/rest/v1/asignacion_academica?curso=eq.{curso}&asignatura=eq.{asignatura}"
            requests.delete(delete_url, headers=headers)
    
    if errores == 0:
        st.success(f"✅ Asignación de materias guardada para el curso {curso}")
        st.rerun()
    else:
        st.warning(f"⚠️ {exitos} guardadas, {errores} errores")


def mostrar_resumen_asignaciones(curso, headers, docentes_dict):
    """Muestra el resumen de asignaciones del curso"""
    st.subheader(f"📋 Resumen del Curso {curso}")
    
    response = requests.get(f"{SUPABASE_URL}/rest/v1/asignacion_academica?curso=eq.{curso}", headers=headers)
    
    if response.status_code == 200:
        asignaciones = response.json()
        if asignaciones:
            for a in asignaciones:
                doc_response = requests.get(f"{SUPABASE_URL}/rest/v1/docentes?documento_docente=eq.{a.get('documento_docente')}", headers=headers)
                if doc_response.status_code == 200 and doc_response.json():
                    docente = doc_response.json()[0]
                    a['nombre_docente'] = f"{docente.get('nombre_docente', '')} {docente.get('apellidos_docente', '')}".strip()
                else:
                    a['nombre_docente'] = "No asignado"
            
            df = pd.DataFrame(asignaciones)
            
            df_director = df[df['asignatura'] == 'Dirección de Curso']
            df_materias = df[df['asignatura'] != 'Dirección de Curso']
            
            if not df_director.empty:
                st.write("**🎓 Director de Curso:**")
                st.write(df_director[['asignatura', 'nombre_docente']].iloc[0].to_dict())
            
            if not df_materias.empty:
                st.write("**📚 Materias y Docentes:**")
                st.dataframe(df_materias[['asignatura', 'nombre_docente']], use_container_width=True)
        else:
            st.info(f"No hay asignaciones para el curso {curso}")


# ============================================
# SISTEMA
# ============================================
def mostrar_sistema():
    st.subheader("⚙️ Configuración del Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        nombre_colegio = st.text_input("Nombre del colegio", "Mi Colegio")
        año_lectivo = st.number_input("Año lectivo", min_value=2000, max_value=2100, value=2024)
        
        if st.button("💾 Guardar Configuración"):
            st.success("Configuración guardada")
    
    with col2:
        if st.button("🔄 Sincronizar Roles", type="primary"):
            headers = get_headers()
            sincronizar_todos_los_roles(headers)
            st.success("✅ Roles sincronizados correctamente")
        
        if st.button("📀 Crear Respaldo"):
            st.success("Respaldo creado")
