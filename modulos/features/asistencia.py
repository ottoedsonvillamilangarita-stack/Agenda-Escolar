import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from utils import SUPABASE_URL, get_headers

# ============================================
# DOCENTE - MARCAR ASISTENCIA
# ============================================

def mostrar_asistencia_docente(data):
    st.subheader("📋 Marcar Asistencia")
    
    documento_docente = data.get('documento')
    headers = get_headers()
    
    url = f"{SUPABASE_URL}/rest/v1/asignacion_academica?documento_docente=eq.{documento_docente}"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        st.error("Error al cargar cursos")
        return
    
    asignaciones = response.json()
    cursos_unicos = list(set([a.get('curso') for a in asignaciones if a.get('curso')]))
    
    if not cursos_unicos:
        st.warning("No tienes cursos asignados")
        return
    
    col1, col2 = st.columns(2)
    with col1:
        curso = st.selectbox("Curso", cursos_unicos)
    with col2:
        fecha = st.date_input("Fecha", datetime.now())
    
    url_est = f"{SUPABASE_URL}/rest/v1/estudiantes?curso=eq.{curso}"
    response_est = requests.get(url_est, headers=headers)
    
    if response_est.status_code != 200:
        st.error("Error al cargar estudiantes")
        return
    
    estudiantes = response_est.json()
    if not estudiantes:
        st.warning(f"No hay estudiantes en el curso {curso}")
        return
    
    asistencias_existentes = {}
    url_asist = f"{SUPABASE_URL}/rest/v1/asistencia?curso=eq.{curso}&fecha=eq.{fecha}"
    response_asist = requests.get(url_asist, headers=headers)
    
    if response_asist.status_code == 200:
        for a in response_asist.json():
            asistencias_existentes[a.get('documento_estudiante')] = a.get('estado')
    
    st.markdown(f"**{curso} - {fecha.strftime('%d/%m/%Y')}**")
    st.markdown("---")
    
    datos_asistencia = []
    
    for estudiante in estudiantes:
        doc = estudiante.get('documento_estudiante')
        nombre = estudiante.get('nombre_estudiante')[:25]
        estado_actual = asistencias_existentes.get(doc, "Presente")
        
        col1, col2 = st.columns([3, 2])
        with col1:
            st.write(f"**{nombre}**")
        with col2:
            estado = st.selectbox(
                "",
                ["Presente", "Ausente", "Retardo", "Justificado"],
                index=["Presente", "Ausente", "Retardo", "Justificado"].index(estado_actual),
                key=f"asis_{doc}_{fecha}",
                label_visibility="collapsed"
            )
            datos_asistencia.append({
                "documento_estudiante": doc,
                "curso": curso,
                "fecha": str(fecha),
                "estado": estado,
                "documento_docente": documento_docente
            })
    
    if st.button("💾 Guardar Asistencia", type="primary", use_container_width=True):
        for registro in datos_asistencia:
            check_url = f"{SUPABASE_URL}/rest/v1/asistencia?documento_estudiante=eq.{registro['documento_estudiante']}&fecha=eq.{registro['fecha']}"
            check = requests.get(check_url, headers=headers)
            
            if check.status_code == 200 and check.json():
                id_asist = check.json()[0].get('id')
                requests.patch(f"{SUPABASE_URL}/rest/v1/asistencia?id=eq.{id_asist}", 
                              headers=headers, json={"estado": registro['estado']})
            else:
                requests.post(f"{SUPABASE_URL}/rest/v1/asistencia", headers=headers, json=registro)
        
        st.success("✅ Asistencia guardada")
        st.balloons()


# ============================================
# ESTUDIANTE - VER ASISTENCIA
# ============================================

def mostrar_asistencia_estudiante(data):
    st.subheader("📋 Reporte de Asistencia")
    
    documento = data.get('documento')
    headers = get_headers()
    
    url = f"{SUPABASE_URL}/rest/v1/asistencia?documento_estudiante=eq.{documento}"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        st.error("Error al cargar asistencia")
        return
    
    asistencias = response.json()
    
    if not asistencias:
        st.info("No hay registros de asistencia")
        return
    
    df = pd.DataFrame(asistencias)
    df['fecha'] = pd.to_datetime(df['fecha'])
    
    total = len(df)
    presentes = len(df[df['estado'] == 'Presente'])
    retardos = len(df[df['estado'] == 'Retardo'])
    ausentes = len(df[df['estado'] == 'Ausente'])
    porcentaje = (presentes / total * 100) if total > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total días", total)
    col2.metric("✅ Presente", presentes)
    col3.metric("⏰ Retardo", retardos)
    col4.metric("❌ Ausente", ausentes)
    
    st.metric("📊 Porcentaje de asistencia", f"{porcentaje:.0f}%")
    st.progress(porcentaje / 100)
    
    st.divider()
    st.write("**Detalle:**")
    df_mostrar = df[['fecha', 'estado']].sort_values('fecha', ascending=False)
    df_mostrar['fecha'] = df_mostrar['fecha'].dt.strftime('%d/%m/%Y')
    st.dataframe(df_mostrar, use_container_width=True)


# ============================================
# ACUDIENTE - VER ASISTENCIA DE HIJOS
# ============================================

def mostrar_asistencia_acudiente(data):
    st.subheader("📋 Asistencia de mis hijos")
    
    documento_acudiente = data.get('documento')
    headers = get_headers()
    
    url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_acudiente=eq.{documento_acudiente}"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        st.error("Error al cargar datos")
        return
    
    hijos = response.json()
    if not hijos:
        st.info("No hay hijos asociados")
        return
    
    for hijo in hijos:
        doc_hijo = hijo.get('documento_estudiante')
        nombre_hijo = hijo.get('nombre_estudiante')
        
        with st.expander(f"📘 {nombre_hijo} - {hijo.get('curso')}"):
            url_asist = f"{SUPABASE_URL}/rest/v1/asistencia?documento_estudiante=eq.{doc_hijo}"
            response_asist = requests.get(url_asist, headers=headers)
            
            if response_asist.status_code == 200:
                asistencias = response_asist.json()
                if asistencias:
                    df = pd.DataFrame(asistencias)
                    presentes = len(df[df['estado'] == 'Presente'])
                    total = len(df)
                    porcentaje = (presentes / total * 100) if total > 0 else 0
                    
                    st.metric("Asistencia", f"{porcentaje:.0f}%")
                    st.progress(porcentaje / 100)
                    
                    df_mostrar = df[['fecha', 'estado']].sort_values('fecha', ascending=False)
                    df_mostrar['fecha'] = pd.to_datetime(df_mostrar['fecha']).dt.strftime('%d/%m/%Y')
                    st.dataframe(df_mostrar, use_container_width=True)
                else:
                    st.info("Sin registros")


# ============================================
# DIRECTOR - REPORTE DE ASISTENCIA
# ============================================

def mostrar_asistencia_director(data):
    st.subheader("📋 Reporte de Asistencia del Curso")
    
    documento_docente = data.get('documento')
    headers = get_headers()
    
    url_dir = f"{SUPABASE_URL}/rest/v1/asignacion_academica?documento_docente=eq.{documento_docente}&asignatura=eq.Dirección de Curso"
    response_dir = requests.get(url_dir, headers=headers)
    
    if response_dir.status_code != 200 or not response_dir.json():
        st.warning("No eres director de ningún curso")
        return
    
    curso = response_dir.json()[0].get('curso')
    st.success(f"📌 Curso: {curso}")
    
    if st.button("📋 Marcar Asistencia Hoy", use_container_width=True):
        mostrar_asistencia_docente(data)
        return
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Desde")
    with col2:
        fecha_fin = st.date_input("Hasta")
    
    if st.button("📊 Generar Reporte", type="primary", use_container_width=True):
        url_est = f"{SUPABASE_URL}/rest/v1/estudiantes?curso=eq.{curso}"
        response_est = requests.get(url_est, headers=headers)
        
        if response_est.status_code != 200:
            st.error("Error al cargar estudiantes")
            return
        
        estudiantes = response_est.json()
        
        reporte = []
        for estudiante in estudiantes:
            doc = estudiante.get('documento_estudiante')
            nombre = estudiante.get('nombre_estudiante')
            
            url_asist = f"{SUPABASE_URL}/rest/v1/asistencia?documento_estudiante=eq.{doc}&fecha=gte.{fecha_inicio}&fecha=lte.{fecha_fin}"
            response_asist = requests.get(url_asist, headers=headers)
            
            if response_asist.status_code == 200:
                asistencias = response_asist.json()
                total = len(asistencias)
                presentes = len([a for a in asistencias if a['estado'] == 'Presente'])
                porcentaje = (presentes / total * 100) if total > 0 else 0
                
                reporte.append({
                    "Estudiante": nombre,
                    "Presentes": presentes,
                    "Total": total,
                    "%": f"{porcentaje:.0f}"
                })
        
        if reporte:
            df = pd.DataFrame(reporte)
            st.dataframe(df, use_container_width=True)
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar", data=csv, file_name=f"asistencia_{curso}.csv", mime="text/csv")
