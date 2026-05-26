import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from utils import SUPABASE_URL, get_headers
from modulos.features.asistencia import mostrar_reporte_asistencia

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
    """Reporte de ausencias por estudiante (usando función unificada)"""
    
    curso = st.selectbox("Seleccionar curso", cursos_unicos, key="reporte_ausencias_curso")
    
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Desde", datetime.now().replace(day=1), key="reporte_fecha_ini")
    with col2:
        fecha_fin = st.date_input("Hasta", datetime.now(), key="reporte_fecha_fin")
    
    if st.button("📊 Generar reporte", type="primary", use_container_width=True):
        headers = get_headers()
        mostrar_reporte_asistencia(curso, fecha_inicio, fecha_fin, headers, f"Reporte de Asistencia - Curso {curso}")


def mostrar_resumen_ausencias(cursos_unicos, documento_docente):
    """Resumen de ausencias por curso"""
    st.info("🚧 Módulo en desarrollo - Próximamente")
    st.write("Este reporte mostrará un resumen comparativo entre cursos")


def mostrar_evolucion_asistencia(cursos_unicos, documento_docente):
    """Evolución de asistencia en el tiempo"""
    st.info("🚧 Módulo en desarrollo - Próximamente")
    st.write("Este reporte mostrará gráficas de evolución de asistencia")

def mostrar_reporte_asistencia_director(data):
    st.subheader("📊 Reporte de Asistencia")
    
    documento_docente = data.get('documento')
    headers = get_headers()
    
    # Obtener curso que dirige
    url_dir = f"{SUPABASE_URL}/rest/v1/asignacion_academica?documento_docente=eq.{documento_docente}&asignatura=eq.Dirección de Curso"
    response_dir = requests.get(url_dir, headers=headers)
    
    if response_dir.status_code != 200 or not response_dir.json():
        st.warning("No eres director de ningún curso")
        return
    
    curso = response_dir.json()[0].get('curso')
    st.success(f"📌 Curso: {curso}")
    
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Desde")
    with col2:
        fecha_fin = st.date_input("Hasta")
    
    if st.button("📊 Generar Reporte", type="primary", use_container_width=True):
        url_datos = f"{SUPABASE_URL}/rest/v1/asistencia?curso=eq.{curso}&fecha=gte.{fecha_inicio}&fecha=lte.{fecha_fin}"
        response_datos = requests.get(url_datos, headers=headers)
        
        if response_datos.status_code == 200:
            datos = response_datos.json()
            if datos:
                # Procesar por estudiante
                resumen = {}
                for reg in datos:
                    doc = reg.get('documento_estudiante')
                    if doc not in resumen:
                        resumen[doc] = {"presentes": 0, "ausentes": 0, "retardos": 0, "uniformes": 0, "justificados": 0}
                    
                    if reg.get('estado') == 'Presente':
                        resumen[doc]["presentes"] += 1
                    else:
                        resumen[doc]["ausentes"] += 1
                        if reg.get('justificado'):
                            resumen[doc]["justificados"] += 1
                    
                    if reg.get('retardo'):
                        resumen[doc]["retardos"] += 1
                    if reg.get('uniforme_malo'):
                        resumen[doc]["uniformes"] += 1
                
                # Mostrar tabla
                st.markdown("---")
                col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
                with col1:
                    st.markdown("**Estudiante**")
                with col2:
                    st.markdown("**Presentes**")
                with col3:
                    st.markdown("**Ausentes**")
                with col4:
                    st.markdown("**Retardos**")
                with col5:
                    st.markdown("**Uniforme**")
                st.markdown("---")
                
                for doc, vals in resumen.items():
                    url_nom = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{doc}"
                    resp_nom = requests.get(url_nom, headers=headers)
                    nombre = resp_nom.json()[0].get('nombre_estudiante') if resp_nom.status_code == 200 else doc
                    
                    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
                    with col1:
                        st.write(f"**{nombre[:25]}**")
                    with col2:
                        st.write(f"{vals['presentes']}")
                    with col3:
                        st.write(f"{vals['ausentes']}")
                        if vals['justificados'] > 0:
                            st.caption(f"({vals['justificados']} justif.)")
                    with col4:
                        st.write(f"{vals['retardos']}")
                    with col5:
                        st.write(f"{vals['uniformes']}")
                
                st.markdown("---")
                
                # Descargar
                df = pd.DataFrame([{"Estudiante": doc, **vals} for doc, vals in resumen.items()])
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Descargar CSV", data=csv, file_name=f"asistencia_{curso}.csv", mime="text/csv")
            else:
                st.info("No hay registros")
