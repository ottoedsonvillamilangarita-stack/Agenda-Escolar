import streamlit as st
import requests
import pandas as pd
from utils import SUPABASE_URL, get_headers
from modulos.features.calificaciones import mostrar_configuracion_notas, mostrar_ingreso_notas
from modulos.features.asistencia import mostrar_asistencia_docente
from modulos.features.reportes import mostrar_reportes_docente

def mostrar(data):
    st.title("👨‍🏫 Panel del Docente")
    
    documento_docente = data.get('documento')
    st.write(f"Bienvenido, {data.get('username', 'Docente')}")
    
    # ============================================
    # OBTENER ASIGNACIONES DEL DOCENTE
    # ============================================
    headers = get_headers()
    
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
    direcciones = [a for a in asignaciones if a.get('asignatura') == 'Dirección de Curso']
    materias = [a for a in asignaciones if a.get('asignatura') != 'Dirección de Curso']
    
    # Mostrar información del director de curso
    if direcciones:
        st.success("🎓 **Eres Director de Curso**")
        for d in direcciones:
            st.info(f"📌 Curso: **{d.get('curso')}**")
    
    # Mostrar materias por curso
    materias_por_curso = {}
    if materias:
        st.subheader("📚 Mis Materias")
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
    # MENÚ DESPLEGABLE (SELECTBOX)
    # ============================================
    st.divider()
    st.subheader("📌 Funciones disponibles")
    
    opcion_menu = st.selectbox(
    "Seleccionar una función",
    [
        "📚 Mis Cursos",
        "📝 Ingresar Notas",
        "⚙️ Configurar Notas",
        "📋 Asistencia",
        "📊 Reportes",
        "🤝 Convivencia",
        "✏️ Evaluaciones",
        "💬 Mensajes",
        "📈 Mi Rendimiento"
    ],
    key="menu_docente"
)
    
    st.divider()
    
    # ============================================
    # REDIRECCIÓN SEGÚN OPCIÓN SELECCIONADA
    # ============================================
    
    if opcion_menu == "📚 Mis Cursos":
        mostrar_mis_cursos(materias_por_curso)
    elif opcion_menu == "📝 Ingresar Notas":
        mostrar_ingreso_notas(data)
    elif opcion_menu == "⚙️ Configurar Notas":
        mostrar_configuracion_notas(data)
   elif opcion_menu == "📋 Asistencia":
    mostrar_asistencia_docente(data) 
    elif opcion_menu == "📊 Reportes":
        mostrar_reportes()
    elif opcion_menu == "🤝 Convivencia":
        mostrar_convivencia()
    elif opcion_menu == "✏️ Evaluaciones":
        mostrar_evaluaciones()
    elif opcion_menu == "💬 Mensajes":
        mostrar_mensajes()
    elif opcion_menu == "📈 Mi Rendimiento":
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
