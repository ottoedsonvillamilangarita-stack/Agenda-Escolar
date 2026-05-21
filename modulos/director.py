import streamlit as st
import requests
import pandas as pd
from utils import SUPABASE_URL, get_headers
from modulos.features.calificaciones import mostrar_notas_curso# ← NUEVO IMPORT
from modulos.features.asistencia import mostrar_asistencia_director

def mostrar(data):
    st.title("🧭 Director de Grupo")
    
    documento_docente = data.get('documento')
    st.write(f"Bienvenido, {data.get('username', 'Director')}")
    
    headers = get_headers()
    
    # Buscar curso que dirige
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
    # PESTAÑAS (AGREGAMOS UNA NUEVA)
    # ============================================
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Estudiantes", "📖 Notas del Curso", "📈 Rendimiento", "📋 Asistencia", "📊 Reportes"])
    
    with tab1:
        st.subheader(f"📋 Estudiantes del Curso {curso_dirige}")
        
        url_est = f"{SUPABASE_URL}/rest/v1/estudiantes?curso=eq.{curso_dirige}"
        response_est = requests.get(url_est, headers=headers)
        
        if response_est.status_code != 200:
            st.error("Error al cargar los estudiantes")
        else:
            estudiantes = response_est.json()
            if estudiantes:
                df = pd.DataFrame(estudiantes)
                columnas = ['nombre_estudiante', 'apellidos_estudiante', 'documento_estudiante']
                columnas_existentes = [col for col in columnas if col in df.columns]
                st.dataframe(df[columnas_existentes], use_container_width=True)
                st.caption(f"Total: {len(estudiantes)} estudiantes")
            else:
                st.info(f"No hay estudiantes en el curso {curso_dirige}")
    
    with tab2:
        # NUEVA PESTAÑA: NOTAS DEL CURSO
        mostrar_notas_curso(data)
    
    with tab3:
        st.subheader("📈 Rendimiento Académico")
        st.info("Módulo en desarrollo")
    
   with tab4:
    mostrar_asistencia_director(data)
    
    with tab5:
        st.subheader("📊 Reportes")
        st.info("Módulo en desarrollo")
