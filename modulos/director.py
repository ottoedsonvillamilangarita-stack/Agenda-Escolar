import streamlit as st
import requests
import pandas as pd
from utils import SUPABASE_URL, get_headers
from modulos.features.calificaciones import mostrar_notas_curso
from modulos.features.asistencia import mostrar_asistencia_director
from modulos.features.horarios import mostrar_horario_tabla

def mostrar(data):
    st.title("🧭 Director de Grupo")
    
    documento_docente = data.get('documento')
    st.write(f"Bienvenido, {data.get('username', 'Director')}")
    
    headers = get_headers()
    
    # Obtener curso que dirige
    url = f"{SUPABASE_URL}/rest/v1/asignacion_academica?documento_docente=eq.{documento_docente}&asignatura=eq.Dirección de Curso"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200 or not response.json():
        st.warning("No eres director de ningún curso")
        return
    
    curso_dirige = response.json()[0].get('curso')
    st.success(f"🎓 Director del curso: **{curso_dirige}**")
    
    # ============================================
    # HORARIO SEMANAL del curso (tabla)
    # ============================================
    st.subheader("📅 Horario Semanal del Curso")
    mostrar_horario_tabla(curso_dirige, headers)
    
    st.divider()
    
    # Pestañas
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Estudiantes", "📖 Notas del Curso", "📋 Asistencia", "📊 Reportes"])
    
    with tab1:
        url_est = f"{SUPABASE_URL}/rest/v1/estudiantes?curso=eq.{curso_dirige}"
        response_est = requests.get(url_est, headers=headers)
        
        if response_est.status_code == 200:
            estudiantes = response_est.json()
            if estudiantes:
                df = pd.DataFrame(estudiantes)
                st.dataframe(df[['nombre_estudiante', 'documento_estudiante']], use_container_width=True)
                st.caption(f"Total: {len(estudiantes)} estudiantes")
            else:
                st.info("No hay estudiantes")
    
    with tab2:
        mostrar_notas_curso(data)
    
    with tab3:
    st.subheader("📋 Asistencia del Curso")
    
    headers = get_headers()
    
    # Obtener curso que dirige
    url_dir = f"{SUPABASE_URL}/rest/v1/asignacion_academica?documento_docente=eq.{documento_docente}&asignatura=eq.Dirección de Curso"
    response_dir = requests.get(url_dir, headers=headers)
    
    if response_dir.status_code != 200 or not response_dir.json():
        st.warning("No eres director de ningún curso")
    else:
        curso = response_dir.json()[0].get('curso')
        st.success(f"📌 Curso: {curso}")
        
        # Usar session_state para controlar el modo
        if "modo_marcar_asistencia" not in st.session_state:
            st.session_state.modo_marcar_asistencia = False
        
        if st.session_state.modo_marcar_asistencia:
            # Mostrar formulario de marcar asistencia
            from modulos.features.asistencia import mostrar_asistencia_docente
            mostrar_asistencia_docente(data)
            if st.button("🔙 Volver a Reporte", use_container_width=True):
                st.session_state.modo_marcar_asistencia = False
                st.rerun()
        else:
            # Mostrar botón y reporte
            if st.button("📋 Marcar Asistencia Hoy", use_container_width=True):
                st.session_state.modo_marcar_asistencia = True
                st.rerun()
            
            st.divider()
            
            col1, col2 = st.columns(2)
            with col1:
                fecha_inicio = st.date_input("Desde")
            with col2:
                fecha_fin = st.date_input("Hasta")
            
            if st.button("📊 Generar Reporte", type="primary", use_container_width=True):
                from modulos.features.asistencia import mostrar_reporte_asistencia
                mostrar_reporte_asistencia(curso, fecha_inicio, fecha_fin, headers, f"Reporte de Asistencia - Curso {curso}")
        mostrar_asistencia_director(data)
    
    with tab4:
        st.info("🚧 Módulo en desarrollo")
