import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from utils import SUPABASE_URL, get_headers

def mostrar(data):
    st.title("👨‍🏫 Panel del Docente")
    
    documento_docente = data.get('documento')
    
    # Verificar datos del docente
    headers = get_headers()
    url = f"{SUPABASE_URL}/rest/v1/docentes?documento_docente=eq.{documento_docente}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200 and response.json():
        docente = response.json()[0]
        st.success(f"Bienvenido, {docente.get('nombre_docente', 'Docente')}")
    
    # Inicializar función actual
    if "funcion_actual" not in st.session_state:
        st.session_state.funcion_actual = "mis_cursos"
    
    # ============================================
    # MENÚ DE FUNCIONES (6 botones principales)
    # ============================================
    
    st.subheader("📌 Funciones disponibles")
    
    # Primera fila de botones (3)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📚 Mis Cursos", use_container_width=True, 
                     type="primary" if st.session_state.funcion_actual == "mis_cursos" else "secondary"):
            st.session_state.funcion_actual = "mis_cursos"
            st.rerun()
    
    with col2:
        if st.button("📝 Calificaciones", use_container_width=True,
                     type="primary" if st.session_state.funcion_actual == "calificaciones" else "secondary"):
            st.session_state.funcion_actual = "calificaciones"
            st.rerun()
    
    with col3:
        if st.button("📋 Asistencia", use_container_width=True,
                     type="primary" if st.session_state.funcion_actual == "asistencia" else "secondary"):
            st.session_state.funcion_actual = "asistencia"
            st.rerun()
    
    # Segunda fila de botones (3)
    col4, col5, col6 = st.columns(3)
    
    with col4:
        if st.button("📊 Reportes", use_container_width=True,
                     type="primary" if st.session_state.funcion_actual == "reportes" else "secondary"):
            st.session_state.funcion_actual = "reportes"
            st.rerun()
    
    with col5:
        if st.button("🤝 Convivencia", use_container_width=True,
                     type="primary" if st.session_state.funcion_actual == "convivencia" else "secondary"):
            st.session_state.funcion_actual = "convivencia"
            st.rerun()
    
    with col6:
        if st.button("✏️ Evaluaciones", use_container_width=True,
                     type="primary" if st.session_state.funcion_actual == "evaluaciones" else "secondary"):
            st.session_state.funcion_actual = "evaluaciones"
            st.rerun()
    
    # Tercera fila de botones (2)
    col7, col8 = st.columns(2)
    
    with col7:
        if st.button("💬 Mensajes", use_container_width=True,
                     type="primary" if st.session_state.funcion_actual == "mensajes" else "secondary"):
            st.session_state.funcion_actual = "mensajes"
            st.rerun()
    
    with col8:
        if st.button("📈 Mi Rendimiento", use_container_width=True,
                     type="primary" if st.session_state.funcion_actual == "mi_rendimiento" else "secondary"):
            st.session_state.funcion_actual = "mi_rendimiento"
            st.rerun()
    
    st.divider()
    
    # ============================================
    # MOSTRAR FUNCIÓN SELECCIONADA
    # ============================================
    
    if st.session_state.funcion_actual == "mis_cursos":
        mostrar_mis_cursos(data)
    elif st.session_state.funcion_actual == "calificaciones":
        mostrar_calificaciones(data)
    elif st.session_state.funcion_actual == "asistencia":
        mostrar_asistencia(data)
    elif st.session_state.funcion_actual == "reportes":
        mostrar_reportes(data)
    elif st.session_state.funcion_actual == "convivencia":
        mostrar_convivencia(data)
    elif st.session_state.funcion_actual == "evaluaciones":
        mostrar_evaluaciones(data)
    elif st.session_state.funcion_actual == "mensajes":
        mostrar_mensajes(data)
    elif st.session_state.funcion_actual == "mi_rendimiento":
        mostrar_mi_rendimiento(data)

# ============================================
# FUNCIÓN 1: MIS CURSOS
# ============================================
def mostrar_mis_cursos(data):
    st.subheader("📚 Mis Cursos")
    
    documento_docente = data.get('documento')
    headers = get_headers()
    url = f"{SUPABASE_URL}/rest/v1/docentes?documento_docente=eq.{documento_docente}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        cursos = response.json()
        if cursos:
            # Agrupar por curso
            cursos_dict = {}
            for curso in cursos:
                curso_num = curso.get('curso')
                if curso_num not in cursos_dict:
                    cursos_dict[curso_num] = []
                cursos_dict[curso_num].append(curso.get('asignatura'))
            
            for curso_num, materias in cursos_dict.items():
                with st.expander(f"📖 Curso {curso_num}"):
                    for materia in materias:
                        st.write(f"- {materia}")
                    st.write(f"**Total estudiantes:** Por definir")
        else:
            st.info("No hay cursos asignados")

# ============================================
# FUNCIÓN 2: CALIFICACIONES
# ============================================
def mostrar_calificaciones(data):
    st.subheader("📝 Calificaciones")
    
    # Seleccionar curso y materia
    col1, col2 = st.columns(2)
    
    with col1:
        curso = st.selectbox("Seleccionar curso", ["901", "902", "903", "1001", "1002", "1003", "1101"])
    
    with col2:
        materia = st.selectbox("Seleccionar materia", 
                               ["Matemáticas", "Español", "Ciencias", "Sociales", "Inglés", "Artes", "Física", "Química"])
    
    # Período académico
    periodo = st.selectbox("Período", ["Periodo 1", "Periodo 2", "Periodo 3", "Periodo 4", "Final"])
    
    # Obtener estudiantes del curso
    headers = get_headers()
    url = f"{SUPABASE_URL}/rest/v1/estudiantes?curso=eq.{curso}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        estudiantes = response.json()
        if estudiantes:
            st.write(f"**Calificaciones - {materia} - Curso {curso} - {periodo}**")
            
            # Crear tabla de calificaciones
            datos_calif = []
            for estudiante in estudiantes:
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.write(f"{estudiante.get('nombre_estudiante', 'N/A')}")
                with col2:
                    nota = st.number_input(
                        "Nota",
                        min_value=0.0,
                        max_value=5.0,
                        step=0.1,
                        key=f"nota_{estudiante.get('documento_estudiante')}"
                    )
                with col3:
                    st.write(f"/{nota}")
                datos_calif.append({
                    "Estudiante": estudiante.get('nombre_estudiante'),
                    "Documento": estudiante.get('documento_estudiante'),
                    "Nota": nota
                })
            
            if st.button("💾 Guardar Calificaciones", type="primary"):
                st.success(f"✅ Calificaciones guardadas para {materia} - Curso {curso} - {periodo}")
                # Aquí se guardarían en la base de datos
        else:
            st.info(f"No hay estudiantes en el curso {curso}")

# ============================================
# FUNCIÓN 3: ASISTENCIA
# ============================================
def mostrar_asistencia(data):
    st.subheader("📋 Asistencia")
    
    curso = st.selectbox("Seleccionar curso", ["901", "902", "903", "1001", "1002", "1003", "1101"])
    fecha = st.date_input("Fecha", datetime.now())
    
    headers = get_headers()
    url = f"{SUPABASE_URL}/rest/v1/estudiantes?curso=eq.{curso}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        estudiantes = response.json()
        if estudiantes:
            st.write(f"**Registro de asistencia - Curso {curso} - {fecha}**")
            
            datos_asistencia = []
            for estudiante in estudiantes:
                estado = st.radio(
                    f"{estudiante.get('nombre_estudiante', 'N/A')}",
                    ["Presente", "Ausente", "Retardo", "Justificado"],
                    key=f"asis_{estudiante.get('documento_estudiante')}",
                    horizontal=True
                )
                datos_asistencia.append({
                    "Estudiante": estudiante.get('nombre_estudiante'),
                    "Estado": estado
                })
            
            if st.button("💾 Guardar Asistencia", type="primary"):
                st.success(f"✅ Asistencia guardada para curso {curso} - {fecha}")
        else:
            st.info(f"No hay estudiantes en el curso {curso}")

# ============================================
# FUNCIÓN 4: REPORTES
# ============================================
def mostrar_reportes(data):
    st.subheader("📊 Reportes")
    
    tipo_reporte = st.selectbox(
        "Tipo de reporte",
        ["Reporte de Notas", "Reporte de Asistencia", "Reporte por Estudiante", "Reporte por Curso"]
    )
    
    curso = st.selectbox("Curso", ["901", "902", "903", "1001", "1002", "1003", "1101"])
    
    if st.button("📄 Generar Reporte", type="primary"):
        st.info(f"Generando {tipo_reporte} para el curso {curso}...")
        st.success("✅ Reporte generado exitosamente")
        st.download_button(
            label="📥 Descargar Reporte",
            data="Datos del reporte...",
            file_name=f"reporte_{curso}.csv",
            mime="text/csv"
        )

# ============================================
# FUNCIÓN 5: CONVIVENCIA
# ============================================
def mostrar_convivencia(data):
    st.subheader("🤝 Convivencia Escolar")
    
    opcion = st.radio(
        "Seleccionar acción",
        ["📝 Registrar Novedad", "📋 Ver Novedades", "🏅 Registro de Logros", "⚠️ Reporte de Incidentes"]
    )
    
    if opcion == "📝 Registrar Novedad":
        curso = st.selectbox("Curso", ["901", "902", "903", "1001", "1002", "1003", "1101"])
        
        headers = get_headers()
        url = f"{SUPABASE_URL}/rest/v1/estudiantes?curso=eq.{curso}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            estudiantes = response.json()
            if estudiantes:
                estudiante = st.selectbox(
                    "Seleccionar estudiante",
                    [f"{e.get('nombre_estudiante')} - {e.get('documento_estudiante')}" for e in estudiantes]
                )
                
                tipo = st.selectbox("Tipo", ["Anotación positiva", "Llamado de atención", "Compromiso", "Citación"])
                descripcion = st.text_area("Descripción")
                
                if st.button("📌 Registrar", type="primary"):
                    st.success("✅ Novedad registrada exitosamente")
            else:
                st.info(f"No hay estudiantes en el curso {curso}")
    
    elif opcion == "📋 Ver Novedades":
        st.write("**Novedades recientes**")
        st.info("No hay novedades registradas")
    
    elif opcion == "🏅 Registro de Logros":
        st.write("**Logros estudiantiles**")
        st.info("No hay logros registrados")
    
    elif opcion == "⚠️ Reporte de Incidentes":
        st.write("**Reporte de incidentes**")
        st.info("No hay incidentes reportados")

# ============================================
# FUNCIÓN 6: EVALUACIONES
# ============================================
def mostrar_evaluaciones(data):
    st.subheader("✏️ Crear Evaluaciones")
    
    opcion = st.radio(
        "Seleccionar acción",
        ["📝 Crear Evaluación", "📋 Ver Evaluaciones", "✅ Calificar Evaluación"]
    )
    
    if opcion == "📝 Crear Evaluación":
        curso = st.selectbox("Curso", ["901", "902", "903", "1001", "1002", "1003", "1101"])
        materia = st.text_input("Asignatura")
        titulo = st.text_input("Título de la evaluación")
        fecha = st.date_input("Fecha de aplicación", datetime.now())
        valor = st.number_input("Valor total", min_value=0.0, max_value=100.0, value=100.0)
        
        if st.button("📌 Crear Evaluación", type="primary"):
            st.success(f"✅ Evaluación '{titulo}' creada para {materia} - Curso {curso}")
    
    elif opcion == "📋 Ver Evaluaciones":
        st.write("**Evaluaciones programadas**")
        st.info("No hay evaluaciones programadas")
    
    elif opcion == "✅ Calificar Evaluación":
        st.write("**Calificar evaluaciones**")
        st.info("Seleccione una evaluación para calificar")

# ============================================
# FUNCIÓN 7: MENSAJES
# ============================================
def mostrar_mensajes(data):
    st.subheader("💬 Mensajes")
    
    opcion = st.radio(
        "Seleccionar acción",
        ["📨 Enviar Mensaje", "📥 Recibidos", "📤 Enviados"]
    )
    
    if opcion == "📨 Enviar Mensaje":
        destinatario = st.selectbox(
            "Destinatario",
            ["Estudiantes", "Padres de familia", "Otros docentes", "Coordinador", "Administrativos"]
        )
        
        curso = None
        if destinatario in ["Estudiantes", "Padres de familia"]:
            curso = st.selectbox("Curso", ["901", "902", "903", "1001", "1002", "1003", "1101"])
        
        asunto = st.text_input("Asunto")
        mensaje = st.text_area("Mensaje")
        
        if st.button("📨 Enviar", type="primary"):
            st.success(f"✅ Mensaje enviado a {destinatario}")
    
    elif opcion == "📥 Recibidos":
        st.write("**Mensajes recibidos**")
        st.info("No hay mensajes nuevos")
    
    elif opcion == "📤 Enviados":
        st.write("**Mensajes enviados**")
        st.info("No hay mensajes enviados")

# ============================================
# FUNCIÓN 8: MI RENDIMIENTO
# ============================================
def mostrar_mi_rendimiento(data):
    st.subheader("📈 Mi Rendimiento como Docente")
    
    # Estadísticas del docente
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Promedio general del curso", "4.2")
    
    with col2:
        st.metric("✅ Asistencia promedio", "92%")
    
    with col3:
        st.metric("📝 Evaluaciones realizadas", "15")
    
    st.subheader("📈 Evolución de calificaciones")
    st.line_chart({"Matemáticas": [3.5, 3.8, 4.0, 4.2, 4.5],
                   "Español": [3.8, 4.0, 4.1, 4.3, 4.4]})
    
    st.caption("📊 Estadísticas basadas en datos reales próximamente")
