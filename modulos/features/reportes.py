import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from utils import SUPABASE_URL, get_headers

def mostrar_reportes_docente(data):
    st.subheader("📊 Reportes")
    
    documento_docente = data.get('documento')
    headers = get_headers()
    
    # Obtener cursos del docente
    url = f"{SUPABASE_URL}/rest/v1/asignacion_academica?documento_docente=eq.{documento_docente}&asignatura=neq.Dirección de Curso"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        st.error("Error al cargar cursos")
        return
    
    asignaciones = response.json()
    cursos_unicos = list(set([a.get('curso') for a in asignaciones if a.get('curso')]))
    
    if not cursos_unicos:
        st.warning("No tienes cursos asignados")
        return
    
    # Selector de curso
    curso = st.selectbox("Seleccionar curso", cursos_unicos)
    
    # Selección de fechas (mismo renglón)
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Desde", datetime.now().replace(day=1))
    with col2:
        fecha_fin = st.date_input("Hasta", datetime.now())
    
    if st.button("📊 Generar reporte", type="primary", use_container_width=True):
        headers = get_headers()
        
        # Obtener estudiantes del curso
        url_est = f"{SUPABASE_URL}/rest/v1/estudiantes?curso=eq.{curso}"
        response_est = requests.get(url_est, headers=headers)
        
        if response_est.status_code != 200:
            st.error("Error al cargar estudiantes")
            return
        
        estudiantes = response_est.json()
        
        if not estudiantes:
            st.warning("No hay estudiantes en este curso")
            return
        
        # Cabecera compacta (igual que en notas)
        st.markdown("---")
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        with col1:
            st.markdown("**Estudiante**")
        with col2:
            st.markdown("**Ausencias**")
        with col3:
            st.markdown("**Justif.**")
        with col4:
            st.markdown("**No Justif.**")
        st.markdown("---")
        
        # Filas compactas
        reporte = []
        for estudiante in estudiantes:
            doc = estudiante.get('documento_estudiante')
            nombre = estudiante.get('nombre_estudiante')[:25]
            
            url_asist = f"{SUPABASE_URL}/rest/v1/asistencia?documento_estudiante=eq.{doc}&fecha=gte.{fecha_inicio}&fecha=lte.{fecha_fin}"
            response_asist = requests.get(url_asist, headers=headers)
            
            ausentes_total = 0
            ausentes_justificados = 0
            
            if response_asist.status_code == 200:
                asistencias = response_asist.json()
                ausentes_total = len([a for a in asistencias if a['estado'] == 'Ausente'])
                ausentes_justificados = len([a for a in asistencias if a['estado'] == 'Ausente' and a.get('justificada', False)])
            
            ausentes_no_justificados = ausentes_total - ausentes_justificados
            
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            with col1:
                st.write(f"**{nombre}**")
            with col2:
                st.write(f"{ausentes_total}")
            with col3:
                st.write(f"✅ {ausentes_justificados}" if ausentes_justificados > 0 else "—")
            with col4:
                if ausentes_no_justificados > 0:
                    st.warning(f"⚠️ {ausentes_no_justificados}")
                else:
                    st.write("—")
            
            reporte.append({
                "Estudiante": nombre,
                "Ausencias": ausentes_total,
                "Justificadas": ausentes_justificados,
                "No Justificadas": ausentes_no_justificados
            })
        
        st.markdown("---")
        
        # Alerta: estudiantes con más de 3 faltas sin justificar
        df = pd.DataFrame(reporte)
        df_alerta = df[df['No Justificadas'] > 3]
        
        if not df_alerta.empty:
            st.error("🚨 ESTUDIANTES CON MÁS DE 3 AUSENCIAS SIN JUSTIFICAR")
            st.markdown("---")
            
            # Mostrar tabla compacta de alerta
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown("**Estudiante**")
            with col2:
                st.markdown("**Ausencias**")
            with col3:
                st.markdown("**Sin Justif.**")
            st.markdown("---")
            
            for _, row in df_alerta.iterrows():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{row['Estudiante']}**")
                with col2:
                    st.write(f"{row['Ausencias']}")
                with col3:
                    st.warning(f"⚠️ {row['No Justificadas']}")
            
            st.markdown("---")
        else:
            st.success("✅ No hay estudiantes con más de 3 ausencias sin justificar")
        
        # Descargar reporte completo
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Descargar reporte completo (CSV)", 
            data=csv, 
            file_name=f"ausencias_{curso}_{fecha_inicio}_{fecha_fin}.csv", 
            mime="text/csv"
        )
