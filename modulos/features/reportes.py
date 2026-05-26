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
    
    # Selector de tipo de reporte
    tipo_reporte = st.selectbox(
        "Tipo de reporte",
        ["📋 Ausencias por estudiante", "📊 Resumen de ausencias por curso", "📈 Evolución de asistencia"]
    )
    
    if tipo_reporte == "📋 Ausencias por estudiante":
        mostrar_ausencias_por_estudiante(cursos_unicos, documento_docente)
    
    elif tipo_reporte == "📊 Resumen de ausencias por curso":
        mostrar_resumen_ausencias(cursos_unicos, documento_docente)
    
    elif tipo_reporte == "📈 Evolución de asistencia":
        mostrar_evolucion_asistencia(cursos_unicos, documento_docente)


def mostrar_ausencias_por_estudiante(cursos_unicos, documento_docente):
    """Reporte de ausencias por estudiante"""
    
    curso = st.selectbox("Seleccionar curso", cursos_unicos, key="reporte_ausencias_curso")
    
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Desde", datetime.now().replace(day=1), key="reporte_fecha_ini")
    with col2:
        fecha_fin = st.date_input("Hasta", datetime.now(), key="reporte_fecha_fin")
    
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
        
        # Obtener todas las asistencias del período
        url_asist = f"{SUPABASE_URL}/rest/v1/asistencia?curso=eq.{curso}&fecha=gte.{fecha_inicio}&fecha=lte.{fecha_fin}"
        response_asist = requests.get(url_asist, headers=headers)
        
        # Procesar por estudiante
        resumen = {}
        for est in estudiantes:
            doc = est.get('documento_estudiante')
            resumen[doc] = {
                "nombre": est.get('nombre_estudiante'),
                "ausentes": 0,
                "justificados": 0,
                "retardos": 0,
                "uniformes": 0
            }
        
        if response_asist.status_code == 200:
            asistencias = response_asist.json()
            for a in asistencias:
                doc = a.get('documento_estudiante')
                if doc in resumen:
                    if a.get('estado') == 'Ausente':
                        resumen[doc]["ausentes"] += 1
                        if a.get('justificado'):
                            resumen[doc]["justificados"] += 1
                    if a.get('retardo'):
                        resumen[doc]["retardos"] += 1
                    if a.get('uniforme_malo'):
                        resumen[doc]["uniformes"] += 1
        
        # Mostrar tabla
        st.markdown("---")
        col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 1, 1, 1])
        with col1:
            st.markdown("**Estudiante**")
        with col2:
            st.markdown("**Ausencias**")
        with col3:
            st.markdown("**Justif.**")
        with col4:
            st.markdown("**No Justif.**")
        with col5:
            st.markdown("**Retardos**")
        with col6:
            st.markdown("**Uniforme**")
        st.markdown("---")
        
        for doc, vals in resumen.items():
            no_justif = vals["ausentes"] - vals["justificados"]
            col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 1, 1, 1])
            with col1:
                st.write(f"**{vals['nombre'][:25]}**")
            with col2:
                st.write(f"{vals['ausentes']}")
            with col3:
                st.write(f"{vals['justificados']}")
            with col4:
                if no_justif > 0:
                    st.warning(f"{no_justif}")
                else:
                    st.write("0")
            with col5:
                st.write(f"{vals['retardos']}")
            with col6:
                st.write(f"{vals['uniformes']}")
        
        st.markdown("---")
        
        # Alertas
        st.subheader("🚨 Alertas")
        estudiantes_alerta = []
        for doc, vals in resumen.items():
            no_justif = vals["ausentes"] - vals["justificados"]
            if no_justif > 3 or vals['retardos'] > 5 or vals['uniformes'] > 3:
                estudiantes_alerta.append({
                    "nombre": vals['nombre'],
                    "ausencias": no_justif,
                    "retardos": vals['retardos'],
                    "uniforme": vals['uniformes']
                })
        
        if estudiantes_alerta:
            for e in estudiantes_alerta:
                st.write(f"• **{e['nombre']}**: {e['ausencias']} ausencias, {e['retardos']} retardos, {e['uniforme']} uniforme")
        else:
            st.success("✅ No hay estudiantes con alertas")
        
        # Descargar
        df = pd.DataFrame([{
            "Estudiante": vals['nombre'], 
            "Ausencias": vals['ausentes'],
            "Justificadas": vals['justificados'],
            "No Justificadas": vals['ausentes'] - vals['justificados'],
            "Retardos": vals['retardos'],
            "Uniforme": vals['uniformes']
        } for doc, vals in resumen.items()])
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar CSV", data=csv, file_name=f"asistencia_{curso}.csv", mime="text/csv")


def mostrar_resumen_ausencias(cursos_unicos, documento_docente):
    """Resumen de ausencias por curso"""
    st.info("🚧 Módulo en desarrollo - Próximamente")
    st.write("Este reporte mostrará un resumen comparativo entre cursos")


def mostrar_evolucion_asistencia(cursos_unicos, documento_docente):
    """Evolución de asistencia en el tiempo"""
    st.info("🚧 Módulo en desarrollo - Próximamente")
    st.write("Este reporte mostrará gráficas de evolución de asistencia")
