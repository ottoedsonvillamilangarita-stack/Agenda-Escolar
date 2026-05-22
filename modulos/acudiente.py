import streamlit as st
import requests
from utils import SUPABASE_URL, get_headers
from modulos.features.calificaciones import mostrar_notas_acudiente
from modulos.features.asistencia import mostrar_asistencia_acudiente
from modulos.features.horarios import mostrar_horario_semanal_detallado

def mostrar(data):
    st.title("👨‍👩‍👧 Panel del Acudiente")
    
    documento_acudiente = data.get('documento')
    headers = get_headers()
    
    # Obtener hijos
    url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_acudiente=eq.{documento_acudiente}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        hijos = response.json()
        
        if hijos:
            st.success(f"✅ Acudiente con {len(hijos)} hijo(s)")
            
            # ============================================
            # HORARIO SEMANAL para cada hijo
            # ============================================
            for hijo in hijos:
                curso = hijo.get('curso')
                nombre = hijo.get('nombre_estudiante')
                
                with st.expander(f"📘 {nombre} - Curso {curso}"):
                    st.subheader("📅 Horario Semanal")
                    mostrar_horario_semanal_detallado(curso, headers)
        else:
            st.info("No hay hijos asociados")
    
    st.divider()
    st.subheader("📌 Otras funciones")
    
    opcion = st.selectbox(
        "Seleccionar función",
        [
            "👨‍👩‍👧 Mis Hijos",
            "📖 Notas de mis hijos",
            "📋 Asistencia de mis hijos"
        ]
    )
    
    st.divider()
    
    if opcion == "👨‍👩‍👧 Mis Hijos":
        if hijos:
            for hijo in hijos:
                st.write(f"📘 {hijo.get('nombre_estudiante')} - Curso {hijo.get('curso')}")
    elif opcion == "📖 Notas de mis hijos":
        mostrar_notas_acudiente(data)
    elif opcion == "📋 Asistencia de mis hijos":
        mostrar_asistencia_acudiente(data)
