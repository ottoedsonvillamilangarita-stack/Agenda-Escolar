import streamlit as st
import requests
import pandas as pd
from utils import SUPABASE_URL, get_headers
from modulos.features.calificaciones import mostrar_notas_curso
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
    st.success(f"🎓 Director del curso: **{curso_dirige}**")
    
    # Pestañas (solo 3)
    tab1, tab2, tab3 = st.tabs(["📋 Estudiantes", "📖 Notas del Curso", "📋 Asistencia"])
    
    with tab1:
        st.subheader(f"📋 Estudiantes del Curso {curso_dirige}")
        
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
        mostrar_asistencia_director(data)
