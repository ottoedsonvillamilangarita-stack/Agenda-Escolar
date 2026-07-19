import streamlit as st
import requests
import pandas as pd
from utils import SUPABASE_URL, get_headers
from modulos.features.calificaciones import mostrar_notas_curso
from modulos.features.asistencia import mostrar_asistencia_director, mostrar_reporte_asistencia_director
from modulos.features.horarios import mostrar_horario_unificado


def mostrar(data):
    st.title("🧭 Director de Grupo")
    
    documento_docente = data.get('documento')
    st.write(f"Bienvenido, {data.get('username', 'Director')}")
    
    headers = get_headers()
    
    # =============================================
    # 1. BUSCAR CURSO QUE DIRIGE
    # =============================================
    # Usar el texto exacto: 'DIRECCION DE CURSO' (mayúsculas)
    url = f"{SUPABASE_URL}/rest/v1/asignacion_academica?documento_docente=eq.{documento_docente}&asignatura=ilike.%direccion%"
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
    
    # =============================================
    # 2. MOSTRAR HORARIO DEL CURSO
    # =============================================
    st.subheader(f"📅 Horario de {curso_dirige}")
    
    url_horario = f"{SUPABASE_URL}/rest/v1/horario_base?curso=eq.{curso_dirige}&order=dia_semana.asc,orden_clase.asc"
    response_horario = requests.get(url_horario, headers=headers)
    
    if response_horario.status_code == 200:
        horarios = response_horario.json()
        if horarios:
            # Mostrar horario con tipo "estudiante" (muestra asignatura + docente)
            mostrar_horario_unificado(horarios, f"📅 Horario de {curso_dirige}", "estudiante")
        else:
            st.info(f"⚠️ No hay horario configurado para {curso_dirige}")
    else:
        st.info(f"⚠️ No se pudo cargar el horario de {curso_dirige}")
    
    st.divider()
    
    # =============================================
    # 3. FUNCIONES DEL DIRECTOR (PESTAÑAS)
    # =============================================
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Estudiantes", "📖 Notas del Curso", "📋 Asistencia", "📊 Reportes"])
    
    with tab1:
        st.subheader(f"📋 Estudiantes del Curso {curso_dirige}")
        
        url_est = f"{SUPABASE_URL}/rest/v1/estudiantes?curso=eq.{curso_dirige}"
        response_est = requests.get(url_est, headers=headers)
        
        if response_est.status_code == 200:
            estudiantes = response_est.json()
            if estudiantes:
                df = pd.DataFrame(estudiantes)
                # Mostrar columnas relevantes
                columnas = ['nombre_estudiante', 'apellidos_estudiante', 'documento_estudiante']
                df_mostrar = df[[c for c in columnas if c in df.columns]]
                st.dataframe(df_mostrar, use_container_width=True)
                st.caption(f"Total: {len(estudiantes)} estudiantes")
            else:
                st.info("No hay estudiantes en este curso")
    
    with tab2:
        mostrar_notas_curso(data)
    
    with tab3:
        mostrar_asistencia_director(data)
    
    with tab4:
        mostrar_reporte_asistencia_director(data)
