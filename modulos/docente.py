import streamlit as st
import requests
import pandas as pd
from utils import SUPABASE_URL, get_headers

def mostrar(data):
    st.title("👨‍🏫 Panel del Docente")
    
    documento_docente = data.get('documento')
    st.write(f"Bienvenido, {data.get('username', 'Docente')}")
    
    # ============================================
    # OBTENER ASIGNACIONES DEL DOCENTE
    # ============================================
    headers = get_headers()
    
    # Buscar todas las asignaciones de este docente
    url = f"{SUPABASE_URL}/rest/v1/asignacion_academica?documento_docente=eq.{documento_docente}"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        st.error("Error al cargar las asignaciones")
        return
    
    asignaciones = response.json()
    
    if not asignaciones:
        st.warning("⚠️ No tienes asignaciones académicas. Contacta al administrador.")
        return
    
    # ============================================
    # SEPARAR POR TIPO
    # ============================================
    
    # Buscar si es director de algún curso
    direcciones = [a for a in asignaciones if a.get('asignatura') == 'Dirección de Curso']
    
    # Buscar materias que dicta
    materias = [a for a in asignaciones if a.get('asignatura') != 'Dirección de Curso']
    
    # ============================================
    # MOSTRAR INFORMACIÓN
    # ============================================
    
    # Tarjeta de Director de Curso
    if direcciones:
        st.success("🎓 **Eres Director de Curso**")
        for d in direcciones:
            st.info(f"📌 Curso: **{d.get('curso')}**")
    
    # Mostrar materias por curso
    if materias:
        st.subheader("📚 Mis Materias")
        
        # Agrupar por curso
        materias_por_curso = {}
        for m in materias:
            curso = m.get('curso')
            if curso not in materias_por_curso:
                materias_por_curso[curso] = []
            materias_por_curso[curso].append(m.get('asignatura'))
        
        for curso, materias_lista in materias_por_curso.items():
            with st.expander(f"📖 Curso {curso}"):
                for materia in materias_lista:
                    st.write(f"- {materia}")
    
    # ============================================
    # MENÚ DE FUNCIONES
    # ============================================
    
    st.divider()
    st.subheader("📌 Funciones disponibles")
    
    # Inicializar función actual
    if "funcion_actual" not in st.session_state:
        st.session_state.funcion_actual = "mis_cursos"
    
    # Primera fila de botones
    col1, col2, col3, col4 = st.columns(4)
    
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
    
    with col4:
        if st.button("📊 Reportes", use_container_width=True,
                     type="primary" if st.session_state.funcion_actual == "reportes" else "secondary"):
            st.session_state.funcion_actual = "reportes"
            st.rerun()
    
    # Segunda fila de botones
    col5, col6, col7, col8 = st.columns(4)
    
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
        mostrar_mis_cursos(materias_por_curso if materias else {})
    elif st.session_state.funcion_actual == "calificaciones":
        mostrar_calificaciones()
    elif st.session_state.funcion_actual == "asistencia":
        mostrar_asistencia()
    elif st.session_state.funcion_actual == "reportes":
        mostrar_reportes()
    elif st.session_state.funcion_actual == "convivencia":
        mostrar_convivencia()
    elif st.session_state.funcion_actual == "evaluaciones":
        mostrar_evaluaciones()
    elif st.session_state.funcion_actual == "mensajes":
        mostrar_mensajes()
    elif st.session_state.funcion_actual == "mi_rendimiento":
        mostrar_mi_rendimiento()


# ============================================
# FUNCIONES DEL DOCENTE
# ============================================

def mostrar_mis_cursos(materias_por_curso):
    st.subheader("📚 Mis Cursos")
    
    if materias_por_curso:
        for curso, materias_lista in materias_por_curso.items():
            with st.expander(f"📖 Curso {curso}"):
                for materia in materias_lista:
                    st.write(f"- {materia}")
    else:
        st.info("No tienes cursos asignados")


def mostrar_calificaciones():
    st.subheader("📝 Calificaciones")
    st.info("Módulo en desarrollo - Próximamente podrás ingresar y editar notas")


def mostrar_asistencia():
    st.subheader("📋 Asistencia")
    st.info("Módulo en desarrollo - Próximamente podrás marcar asistencia")


def mostrar_reportes():
    st.subheader("📊 Reportes")
    st.info("Módulo en desarrollo - Próximamente podrás generar reportes")


def mostrar_convivencia():
    st.subheader("🤝 Convivencia Escolar")
    st.info("Módulo en desarrollo - Próximamente podrás registrar novedades")


def mostrar_evaluaciones():
    st.subheader("✏️ Evaluaciones")
    st.info("Módulo en desarrollo - Próximamente podrás crear evaluaciones")


def mostrar_mensajes():
    st.subheader("💬 Mensajes")
    st.info("Módulo en desarrollo - Próximamente podrás enviar mensajes")


def mostrar_mi_rendimiento():
    st.subheader("📈 Mi Rendimiento")
    st.info("Módulo en desarrollo - Próximamente podrás ver tu rendimiento")
