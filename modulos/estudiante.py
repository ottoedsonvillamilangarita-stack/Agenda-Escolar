import streamlit as st
import requests
import pandas as pd
from utils import SUPABASE_URL, get_headers
from modulos.features.calificaciones import mostrar_notas_estudiante
from modulos.features.asistencia import mostrar_asistencia_estudiante
from modulos.features.horarios import mostrar_horario_estudiante

def mostrar(data):
    st.title("🎓 Panel del Estudiante")
    
    documento_estudiante = data.get('documento')
    st.write(f"Bienvenido, Estudiante")
    
    headers = get_headers()
    
    # Obtener información del estudiante
    url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{documento_estudiante}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        datos = response.json()
        if datos:
            estudiante = datos[0]
            st.success(f"✅ {estudiante.get('nombre_estudiante', 'Estudiante')}")
            st.info(f"📚 Curso: {estudiante.get('curso', 'N/A')}")
        else:
            st.warning("No se encontró información del estudiante")
    else:
        st.error(f"Error al cargar datos: {response.status_code}")
    
    st.divider()
    st.subheader("📌 Funciones disponibles")
    
    # Menú principal
    opcion = st.selectbox(
    "Seleccionar función",
    [
        "📖 Mis Notas",
        "📋 Mi Asistencia",
        "📅 Mi Horario",  # ← Agrega esta línea
        "👤 Mi Perfil"
    ]
)
    
    st.divider()
    
    if opcion == "📖 Mis Notas":
        mostrar_notas_estudiante(data)
    
    elif opcion == "📋 Mi Asistencia":
        mostrar_asistencia_estudiante(data)
    
    elif opcion == "📅 Mi Horario":
        mostrar_horario(data)
    
    elif opcion == "👤 Mi Perfil":
        mostrar_perfil(data)
elif opcion == "📅 Mi Horario":
    mostrar_horario_estudiante(data)

def mostrar_horario(data):
    st.subheader("📅 Mi Horario")
    
    documento = data.get('documento')
    headers = get_headers()
    
    # Obtener curso del estudiante
    url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{documento}"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200 or not response.json():
        st.warning("No se pudo obtener el curso")
        return
    
    curso = response.json()[0].get('curso')
    st.info(f"📌 Horario del curso {curso}")
    
    # Horario de ejemplo (esto luego se conectará a una tabla)
    horario = {
        "Lunes": ["Matemáticas", "Español", "Ciencias", "Descanso", "Sociales"],
        "Martes": ["Inglés", "Matemáticas", "Educación Física", "Descanso", "Artes"],
        "Miércoles": ["Ciencias", "Sociales", "Español", "Descanso", "Matemáticas"],
        "Jueves": ["Ética", "Inglés", "Ciencias", "Descanso", "Matemáticas"],
        "Viernes": ["Educación Física", "Artes", "Sociales", "Descanso", "Inglés"]
    }
    
    for dia, materias in horario.items():
        with st.expander(f"📅 {dia}"):
            for i, materia in enumerate(materias, 1):
                st.write(f"{i}. {materia}")
    
    st.info("🚧 Horario en desarrollo - Próximamente se conectará a base de datos")


def mostrar_perfil(data):
    st.subheader("👤 Mi Perfil")
    
    documento = data.get('documento')
    headers = get_headers()
    
    url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{documento}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200 and response.json():
        estudiante = response.json()[0]
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Nombre:**")
            st.write("**Apellidos:**")
            st.write("**Documento:**")
            st.write("**Curso:**")
            st.write("**Acudiente:**")
            st.write("**Teléfono acudiente:**")
        with col2:
            st.write(estudiante.get('nombre_estudiante', 'N/A'))
            st.write(estudiante.get('apellidos_estudiante', 'N/A'))
            st.write(estudiante.get('documento_estudiante', 'N/A'))
            st.write(estudiante.get('curso', 'N/A'))
            st.write(estudiante.get('nombre_acudiente', 'N/A'))
            st.write(estudiante.get('telefono_acudiente', 'N/A'))
    else:
        st.error("Error al cargar perfil")
