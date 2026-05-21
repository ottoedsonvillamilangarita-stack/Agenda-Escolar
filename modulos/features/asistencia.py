import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from utils import SUPABASE_URL, get_headers

# ============================================
# DOCENTE Y DIRECTOR - MARCAR ASISTENCIA (VERSIÓN ULTRA COMPACTA)
# ============================================

def mostrar_asistencia_docente(data):
    st.subheader("📋 Marcar Asistencia")
    
    documento_docente = data.get('documento')
    headers = get_headers()
    
    # Obtener cursos del docente (incluye dirección de curso)
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
    
    # Seleccionar curso y fecha
    col1, col2 = st.columns(2)
    with col1:
        curso = st.selectbox("Curso", cursos_unicos)
    with col2:
        fecha = st.date_input("Fecha", datetime.now())
    
    # Obtener estudiantes
    url_est = f"{SUPABASE_URL}/rest/v1/estudiantes?curso=eq.{curso}"
    response_est = requests.get(url_est, headers=headers)
    
    if response_est.status_code != 200:
        st.error("Error al cargar estudiantes")
        return
    
    estudiantes = response_est.json()
    if not estudiantes:
        st.warning(f"No hay estudiantes en el curso {curso}")
        return
    
    # Obtener asistencias existentes
    asistencias_existentes = {}
    url_asist = f"{SUPABASE_URL}/rest/v1/asistencia?curso=eq.{curso}&fecha=eq.{fecha}"
    response_asist = requests.get(url_asist, headers=headers)
    
    if response_asist.status_code == 200:
        for a in response_asist.json():
            asistencias_existentes[a.get('documento_estudiante')] = {
                "estado": a.get('estado'),
                "justificada": a.get('justificada', False)
            }
    
    # Cabecera compacta
    st.markdown(f"**{curso} - {fecha.strftime('%d/%m/%Y')}**")
    
    # Columnas: Estudiante | Estado | Justificada
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        st.markdown("**Estudiante**")
    with col2:
        st.markdown("**Estado**")
    with col3:
        st.markdown("**Justificada?**")
    st.markdown("---")
    
    # Filas ultra compactas
    datos_asistencia = []
    
    for estudiante in estudiantes:
        doc = estudiante.get('documento_estudiante')
        nombre = estudiante.get('nombre_estudiante')[:25]
        existente = asistencias_existentes.get(doc, {})
        estado_actual = existente.get('estado', "Presente")
        justificada_actual = existente.get('justificada', False)
        
        col1, col2, col3 = st.columns([2, 2, 2])
        with col1:
            st.write(f"**{nombre}**")
        with col2:
            estado = st.selectbox(
                "",
                ["Presente", "Ausente", "Retardo", "Justificado"],
                index=["Presente", "Ausente", "Retardo", "Justificado"].index(estado_actual),
                key=f"estado_{doc}_{fecha}",
                label_visibility="collapsed"
            )
        with col3:
            # Solo mostrar opción de justificada si el estado es Ausente o Retardo
            if estado in ["Ausente", "Retardo"]:
                justificada = st.checkbox(
                    "",
                    value=justificada_actual,
                    key=f"just_{doc}_{fecha}",
                    label_visibility="collapsed"
                )
            else:
                justificada = False
                st.write("—")
        
        datos_asistencia.append({
            "documento_estudiante": doc,
            "curso": curso,
            "fecha": str(fecha),
            "estado": estado,
            "justificada": justificada if estado in ["Ausente", "Retardo"] else False,
            "documento_docente": documento_docente
        })
    
    st.markdown("---")
    
    if st.button("💾 Guardar Asistencia", type="primary", use_container_width=True):
        exitos = 0
        for registro in datos_asistencia:
            check_url = f"{SUPABASE_URL}/rest/v1/asistencia?documento_estudiante=eq.{registro['documento_estudiante']}&fecha=eq.{registro['fecha']}"
            check = requests.get(check_url, headers=headers)
            
            if check.status_code == 200 and check.json():
                id_asist = check.json()[0].get('id')
                requests.patch(f"{SUPABASE_URL}/rest/v1/asistencia?id=eq.{id_asist}", 
                              headers=headers, json={"estado": registro['estado'], "justificada": registro['justificada']})
            else:
                requests.post(f"{SUPABASE_URL}/rest/v1/asistencia", headers=headers, json=registro)
            exitos += 1
        
        st.success(f"✅ Asistencia guardada para {exitos} estudiantes")
        st.balloons()


# ============================================
# ESTUDIANTE - VER ASISTENCIA CON ESTADÍSTICAS
# ============================================

def mostrar_asistencia_estudiante(data):
    st.subheader("📋 Mi Asistencia")
    
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
    
    # Estadísticas detalladas
    total = len(df)
    presentes = len(df[df['estado'] == 'Presente'])
    retardos = len(df[df['estado'] == 'Retardo'])
    
    # Ausentes: justificados vs no justificados
    ausentes_total = len(df[df['estado'] == 'Ausente'])
    ausentes_justificados = len(df[(df['estado'] == 'Ausente') & (df['justificada'] == True)])
    ausentes_no_justificados = ausentes_total - ausentes_justificados
    
    porcentaje_asistencia = (presentes / total * 100) if total > 0 else 0
    
    # Tarjetas de estadísticas
    col1, col2 = st.columns(2)
    with col1:
        st.metric("✅ Presentes", presentes)
        st.metric("⏰ Retardos", retardos)
    with col2:
        st.metric("📊 Asistencia", f"{porcentaje_asistencia:.0f}%")
        st.metric("❌ Ausencias", ausentes_total)
    
    st.divider()
    
    # Detalle de ausencias justificadas vs no justificadas
    st.write("**📋 Detalle de ausencias:**")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"📌 Justificadas: {ausentes_justificados}")
    with col2:
        st.warning(f"⚠️ No justificadas: {ausentes_no_justificados}")
    
    if ausentes_no_justificados > 3:
        st.error(f"🚨 Alerta: {ausentes_no_justificados} ausencias sin justificar")
    
    st.divider()
    
    # Tabla de asistencia
    st.write("**Registro detallado:**")
    df_mostrar = df[['fecha', 'estado', 'justificada']].sort_values('fecha', ascending=False)
    df_mostrar['fecha'] = df_mostrar['fecha'].dt.strftime('%d/%m')
    df_mostrar['justificada'] = df_mostrar['justificada'].apply(lambda x: "✅" if x else "❌")
    df_mostrar.columns = ['Fecha', 'Estado', 'Justif.']
    st.dataframe(df_mostrar, use_container_width=True)
    
    # Barra de progreso
    st.progress(porcentaje_asistencia / 100)


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
                    total = len(df)
                    presentes = len(df[df['estado'] == 'Presente'])
                    ausentes_total = len(df[df['estado'] == 'Ausente'])
                    ausentes_justificados = len(df[(df['estado'] == 'Ausente') & (df['justificada'] == True)])
                    ausentes_no_justificados = ausentes_total - ausentes_justificados
                    porcentaje = (presentes / total * 100) if total > 0 else 0
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("✅ Presentes", presentes)
                    col2.metric("📊 %", f"{porcentaje:.0f}%")
                    col3.metric("❌ Ausencias", ausentes_total)
                    
                    if ausentes_no_justificados > 0:
                        st.warning(f"⚠️ Ausencias sin justificar: {ausentes_no_justificados}")
                    
                    # Tabla compacta
                    df_mostrar = df[['fecha', 'estado']].sort_values('fecha', ascending=False)
                    df_mostrar['fecha'] = pd.to_datetime(df_mostrar['fecha']).dt.strftime('%d/%m')
                    st.dataframe(df_mostrar, use_container_width=True)
                else:
                    st.info("Sin registros")


# ============================================
# DIRECTOR - REPORTE DE ASISTENCIA DEL CURSO
# ============================================

def mostrar_asistencia_director(data):
    st.subheader("📋 Reporte de Asistencia del Curso")
    
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
    
    # Botón para marcar asistencia (director también puede)
    if st.button("📋 Marcar Asistencia Hoy", use_container_width=True):
        mostrar_asistencia_docente(data)
        return
    
    st.divider()
    
    # Seleccionar período
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
                ausentes_total = len([a for a in asistencias if a['estado'] == 'Ausente'])
                ausentes_justificados = len([a for a in asistencias if a['estado'] == 'Ausente' and a.get('justificada', False)])
                ausentes_no_justificados = ausentes_total - ausentes_justificados
                porcentaje = (presentes / total * 100) if total > 0 else 0
                
                reporte.append({
                    "Estudiante": nombre,
                    "Presentes": presentes,
                    "Ausencias": ausentes_total,
                    "Justificadas": ausentes_justificados,
                    "No Justif.": ausentes_no_justificados,
                    "% Asist.": f"{porcentaje:.0f}"
                })
        
        if reporte:
            df = pd.DataFrame(reporte)
            st.dataframe(df, use_container_width=True)
            
            # Resaltar estudiantes con muchas ausencias
            df_alerta = df[df['No Justif.'] > 3]
            if not df_alerta.empty:
                st.warning("🚨 Estudiantes con más de 3 ausencias sin justificar:")
                st.dataframe(df_alerta[['Estudiante', 'No Justif.']], use_container_width=True)
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar reporte", data=csv, file_name=f"asistencia_{curso}.csv", mime="text/csv")
        else:
            st.info("No hay datos en el período seleccionado")
