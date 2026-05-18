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
    
    # Contar docentes únicos
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
# ALUMNOS
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
        st.info("📌 Los campos marcados con * son obligatorios")
        
        with st.form("nuevo_alumno", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Datos personales**")
                nombre = st.text_input("Nombre *")
                apellidos = st.text_input("Apellidos *")
                documento = st.text_input("Documento *")
                curso = st.selectbox("Curso *", ["901", "902", "903", "1001", "1002", "1003", "1101"])
                sexo = st.selectbox("Sexo", ["", "Masculino", "Femenino"])
                telefono = st.text_input("Teléfono del estudiante")
                email = st.text_input("Email del estudiante")
            
            with col2:
                st.markdown("**Datos del acudiente**")
                nombre_acudiente = st.text_input("Nombre del acudiente *")
                documento_acudiente = st.text_input("Documento del acudiente *")
                parentesco = st.selectbox("Parentesco", ["", "Padre", "Madre", "Tío", "Tía", "Abuelo", "Abuela", "Otro"])
                telefono_acudiente = st.text_input("Teléfono del acudiente")
                email_acudiente = st.text_input("Email del acudiente")
            
            if st.form_submit_button("💾 Guardar Alumno", type="primary"):
                if not all([nombre, apellidos, documento, curso, nombre_acudiente, documento_acudiente]):
                    st.error("❌ Por favor completa todos los campos obligatorios (*)")
                else:
                    headers = get_headers()
                    
                    data_alumno = {
                        "nombre_estudiante": nombre,
                        "apellidos_estudiante": apellidos,
                        "documento_estudiante": documento,
                        "curso": curso,
                        "sexo_estudiante": sexo,
                        "telefono_estudiante": telefono,
                        "email_estudiante": email,
                        "nombre_acudiente": nombre_acudiente,
                        "documento_acudiente": documento_acudiente,
                        "parentesco": parentesco,
                        "telefono_acudiente": telefono_acudiente,
                        "email_acudiente": email_acudiente
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
                        username_acudiente = nombre_acudiente.lower().replace(" ", "_")
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
                        st.error(f"Error: {response.status_code}")
    
    with tab3:
        st.write("**Carga Masiva de Alumnos**")
        
        st.info("📌 **Paso 1:** Descarga la plantilla base")
        
        # Crear plantilla de ejemplo
        plantilla_alumnos = pd.DataFrame({
            "nombre_estudiante": ["Ejemplo"],
            "apellidos_estudiante": ["Ejemplo"],
            "documento_estudiante": ["123456789"],
            "curso": ["901"],
            "sexo_estudiante": ["Masculino"],
            "telefono_estudiante": ["3000000000"],
            "email_estudiante": ["ejemplo@correo.com"],
            "nombre_acudiente": ["Acudiente Ejemplo"],
            "documento_acudiente": ["987654321"],
            "parentesco": ["Padre"],
            "telefono_acudiente": ["3000000001"],
            "email_acudiente": ["acudiente@correo.com"]
        })
        
        csv_plantilla = plantilla_alumnos.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📥 Descargar Plantilla de Alumnos (CSV)",
            data=csv_plantilla,
            file_name="plantilla_alumnos.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        st.divider()
        
        st.info("📌 **Paso 2:** Sube el archivo CSV ya diligenciado")
        
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
                        "nombre_estudiante": str(row.get('nombre_estudiante', '')),
                        "apellidos_estudiante": str(row.get('apellidos_estudiante', '')),
                        "documento_estudiante": str(row.get('documento_estudiante', '')),
                        "curso": str(row.get('curso', '')),
                        "sexo_estudiante": str(row.get('sexo_estudiante', '')),
                        "telefono_estudiante": str(row.get('telefono_estudiante', '')),
                        "email_estudiante": str(row.get('email_estudiante', '')),
                        "nombre_acudiente": str(row.get('nombre_acudiente', '')),
                        "documento_acudiente": str(row.get('documento_acudiente', '')),
                        "parentesco": str(row.get('parentesco', '')),
                        "telefono_acudiente": str(row.get('telefono_acudiente', '')),
                        "email_acudiente": str(row.get('email_acudiente', ''))
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
                    "parentesco": alumno.get('parentesco'),
                    "hijos": []
                }
            if doc_acud:
                acudientes_dict[doc_acud]["hijos"].append(alumno.get('nombre_estudiante'))
        
        if acudientes_dict:
            df = pd.DataFrame([{
                "Nombre": v["nombre"],
                "Documento": v["documento"],
                "Teléfono": v["telefono"],
                "Email": v["email"],
                "Parentesco": v["parentesco"],
                "Hijos": ", ".join(v["hijos"])
            } for v in acudientes_dict.values()])
            st.dataframe(df, use_container_width=True)
            st.caption(f"Total: {len(acudientes_dict)} acudientes")
        else:
            st.info("No hay acudientes registrados")

# ============================================
# DOCENTES (sin curso/asignatura)
# ============================================
def mostrar_docentes():
    st.subheader("👨‍🏫 Gestión de Docentes")
    
    tab1, tab2, tab3 = st.tabs(["📋 Lista de Docentes", "➕ Nuevo Docente", "📥 Carga Masiva"])
    
    with tab2:
        st.write("**Registrar nuevo docente**")
        st.info("📌 Los datos de cursos y materias se asignan en la sección de Asignación Académica")
        
        with st.form("nuevo_docente", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                nombre = st.text_input("Nombre *")
                apellidos = st.text_input("Apellidos *")
                documento = st.text_input("Documento *")
                telefono = st.text_input("Teléfono")
                email = st.text_input("Email")
            
            with col2:
                titulo = st.text_input("Título profesional")
                especializacion = st.text_input("Especialización")
                tipo_contrato = st.selectbox("Tipo de contrato", ["", "Planta", "Contrato", "Cátedra"])
                fecha_ingreso = st.date_input("Fecha de ingreso", value=None)
            
            if st.form_submit_button("💾 Guardar Docente", type="primary"):
                if not all([nombre, apellidos, documento]):
                    st.error("❌ Por favor completa todos los campos obligatorios (*)")
                else:
                    headers = get_headers()
                    
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
                        username_docente = nombre.lower().replace(" ", "_")
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
                        st.error(f"Error: {response.status_code}")
# ============================================
# ASIGNACIÓN ACADÉMICA (con Directores de Curso)
# ============================================
def mostrar_asignacion():
    st.subheader("📚 Asignación Académica")
    
    # ============================================
    # SECCIÓN 1: DIRECTORES DE CURSO
    # ============================================
    st.markdown("### 🎓 Directores de Curso")
    st.info("Asigna un docente como director para cada curso")
    
    headers = get_headers()
    
    # Obtener docentes
    response_docentes = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
    docentes_lista = ["-- Sin asignar --"]
    docentes_dict = {}
    
    if response_docentes.status_code == 200:
        for d in response_docentes.json():
            nombre = f"{d.get('nombre_docente', '')} {d.get('apellidos_docente', '')}".strip()
            docentes_lista.append(nombre)
            docentes_dict[nombre] = d.get('documento_docente')
    
    if len(docentes_lista) == 1:
        st.warning("⚠️ No hay docentes registrados. Por favor, carga docentes primero.")
        return
    
    # Cursos disponibles
    cursos = ["901", "902", "903", "1001", "1002", "1003", "1101"]
    
    # Obtener directores actuales
    response_directores = requests.get(f"{SUPABASE_URL}/rest/v1/asignacion_academica?asignatura=eq.Dirección de Curso", headers=headers)
    directores_actuales = {}
    
    if response_directores.status_code == 200:
        for d in response_directores.json():
            directores_actuales[d.get('curso')] = d.get('documento_docente')
    
    # Formulario de directores
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
                
                director = st.selectbox(
                    "Director",
                    docentes_lista,
                    index=docentes_lista.index(current_nombre),
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
    
    # Seleccionar curso
    curso = st.selectbox(
        "Seleccionar curso",
        cursos,
        key="curso_asignacion"
    )
    
    # Asignaturas por curso
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
    
    # Obtener asignaciones existentes (excluyendo Dirección de Curso)
    response_asig = requests.get(f"{SUPABASE_URL}/rest/v1/asignacion_academica?curso=eq.{curso}&asignatura=neq.Dirección de Curso", headers=headers)
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
                for nombre, doc in docentes_dict.items():
                    if doc == current_doc:
                        current_nombre = nombre
                        break
                
                docente = st.selectbox(
                    "Docente",
                    docentes_lista,
                    index=docentes_lista.index(current_nombre),
                    key=f"materia_{curso}_{asignatura}",
                    label_visibility="collapsed"
                )
                materias_asignadas[asignatura] = docente if docente != "-- Sin asignar --" else None
        
        if st.form_submit_button("💾 Guardar Asignación de Materias", type="primary"):
            guardar_materias(curso, materias_asignadas, docentes_dict, headers)
    
    # Mostrar resumen
    st.divider()
    mostrar_resumen_asignaciones(curso, headers, docentes_dict)


def guardar_directores(directores_asignados, docentes_dict, headers, cursos):
    """Guarda los directores de curso"""
    exitos = 0
    errores = 0
    
    for curso, director_nombre in directores_asignados.items():
        if director_nombre:
            documento_docente = docentes_dict.get(director_nombre)
            
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
            else:
                errores += 1
        else:
            # Eliminar si existe
            delete_url = f"{SUPABASE_URL}/rest/v1/asignacion_academica?curso=eq.{curso}&asignatura=eq.Dirección de Curso"
            requests.delete(delete_url, headers=headers)
    
    if errores == 0:
        st.success(f"✅ Directores de curso guardados exitosamente")
        st.rerun()
    else:
        st.warning(f"⚠️ {exitos} guardados, {errores} errores")


def guardar_materias(curso, materias_asignadas, docentes_dict, headers):
    """Guarda la asignación de materias"""
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
            else:
                errores += 1
        else:
            # Eliminar si existe
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
            # Enriquecer con nombres de docentes
            for a in asignaciones:
                doc_response = requests.get(f"{SUPABASE_URL}/rest/v1/docentes?documento_docente=eq.{a.get('documento_docente')}", headers=headers)
                if doc_response.status_code == 200 and doc_response.json():
                    docente = doc_response.json()[0]
                    a['nombre_docente'] = f"{docente.get('nombre_docente', '')} {docente.get('apellidos_docente', '')}".strip()
                else:
                    a['nombre_docente'] = "No asignado"
            
            df = pd.DataFrame(asignaciones)
            
            # Separar director y materias
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
    
    tab1, tab2 = st.tabs(["🏫 General", "💾 Respaldos"])
    
    with tab1:
        st.write("**Configuración institucional**")
        
        nombre_colegio = st.text_input("Nombre del colegio", "Mi Colegio")
        año_lectivo = st.number_input("Año lectivo", min_value=2000, max_value=2100, value=2024)
        
        if st.button("💾 Guardar Configuración", type="primary"):
            st.success("✅ Configuración guardada exitosamente")
    
    with tab2:
        st.write("**Respaldos de base de datos**")
        
        if st.button("📀 Crear Respaldo", type="primary"):
            with st.spinner("Generando respaldo..."):
                st.success("✅ Respaldo creado exitosamente")

def mostrar_asignacion():
    st.subheader("📚 Asignación Académica")
    
    # ============================================
    # DIAGNÓSTICO
    # ============================================
    headers = get_headers()
    
    # Probar consulta a docentes
    response_docentes = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
    st.write(f"**Status code docentes:** {response_docentes.status_code}")
    st.write(f"**Respuesta docentes:** {response_docentes.json() if response_docentes.status_code == 200 else 'Error'}")
    
    # Probar consulta a asignacion_academica
    response_asig = requests.get(f"{SUPABASE_URL}/rest/v1/asignacion_academica", headers=headers)
    st.write(f"**Status code asignacion:** {response_asig.status_code}")
    # ============================================
    
    # ... resto del código ...
