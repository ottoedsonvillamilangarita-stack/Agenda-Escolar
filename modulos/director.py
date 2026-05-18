import streamlit as st
import requests
import pandas as pd
from utils import SUPABASE_URL, get_headers

def mostrar(data):
    st.title("🧭 Director de Grupo")
    
    documento_docente = data.get('documento')
    st.write(f"Bienvenido, {data.get('username', 'Director')}")
    
    # ============================================
    # OBTENER CURSO QUE DIRIGE
    # ============================================
    headers = get_headers()
    
    # Buscar en asignacion_academica si es director de algún curso
    url = f"{SUPABASE_URL}/rest/v1/asignacion_academica?documento_docente=eq.{documento_docente}&asignatura=eq.Dirección de Curso"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        st.error("Error al cargar la información")
        return
    
    direccion = response.json()
    
    if not direccion:
        st.warning("No eres director de ningún curso")
        return
    
    curso_dirige = direccion[0].get('curso')
    st.success(f"🎓 Eres director del curso: **{curso_dirige}**")
    
    # ============================================
    # OBTENER ESTUDIANTES DEL CURSO
    # ============================================
    url_est = f"{SUPABASE_URL}/rest/v1/estudiantes?curso=eq.{curso_dirige}"
    response_est = requests.get(url_est, headers=headers)
    
    if response_est.status_code != 200:
        st.error("Error al cargar los estudiantes")
        return
    
    estudiantes = response_est.json()
    
    # ============================================
    # MOSTRAR PANEL DE DIRECTOR
    # ============================================
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Estudiantes", "📈 Rendimiento", "📋 Asistencia", "📊 Reportes"])
    
    with tab1:
        st.subheader(f"📋 Estudiantes del Curso {curso_dirige}")
        
        if estudiantes:
            df = pd.DataFrame(estudiantes)
            columnas = ['nombre_estudiante', 'apellidos_estudiante', 'documento_estudiante']
            columnas_existentes = [col for col in columnas if col in df.columns]
            st.dataframe(df[columnas_existentes], use_container_width=True)
            st.caption(f"Total: {len(estudiantes)} estudiantes")
        else:
            st.info(f"No hay estudiantes en el curso {curso_dirige}")
    
    with tab2:
        st.subheader("📈 Rendimiento Académico")
        st.info("Módulo en desarrollo - Próximamente")
    
    with tab3:
        st.subheader("📋 Asistencia")
        st.info("Módulo en desarrollo - Próximamente")
    
    with tab4:
        st.subheader("📊 Reportes")
        st.info("Módulo en desarrollo - Próximamente")
