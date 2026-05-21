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
    
    # Obtener cursos del docente
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
    
    # Obtener estudiantes del curso
    url_est = f"{SUPABASE_URL}/rest/v1/estudiantes?curso=eq.{curso}"
    response_est = requests.get(url_est, headers=headers)
    
    if response_est.status_code != 200:
        st.error("Error al cargar estudiantes")
        return
    
    estudiantes = response_est.json()
    if not estudiantes:
        st.warning(f"No hay estudiantes en el curso {curso}")
        return
    
    # Obtener asistencias existentes para esta fecha
    asistencias_existentes = {}
    url_asist = f"{SUPABASE_URL}/rest/v1/asistencia?curso=eq.{curso}&fecha=eq.{fecha}"
    response_asist = requests.get(url_asist, headers=headers)
    
    if response_asist.status_code == 200:
        for a in response_asist.json():
            asistencias_existentes[a.get('documento_estudiante')] = a.get('estado')
    
    # Mostrar estudiantes con selector de estado
    st.markdown("---")
    st.write(f"**Curso {curso} - {fecha.strftime('%d/%m/%Y')}**")
    st.markdown("---")
    
    datos_asistencia = []
    
    for estudiante in estudiantes:
        doc = estudiante.get('documento_estudiante')
        nombre = estudiante.get('nombre_estudiante')
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
        st.divider()
    
    # Guardar
    if st.button("💾 Guardar Asistencia", type="primary", use_container_width=True):
        exitos = 0
        for registro in datos_asistencia:
            # Verificar si ya existe
            check_url = f"{SUPABASE_URL}/rest/v1/asistencia?documento_estudiante=eq.{registro['documento_estudiante']}&fecha=eq.{registro['fecha']}"
            check = requests.get(check_url, headers=headers)
            
            if check.status_code == 200 and check.json():
                # Actualizar
                id_asist = check.json()[0].get('id')
                requests.patch(f"{SUPABASE_URL}/rest/v1/asistencia?id=eq.{id_asist}", 
                              headers=headers, json={"estado": registro['estado']})
            else:
                # Insertar
                requests.post(f"{SUPABASE_URL}/rest/v1/asistencia", headers=headers, json=registro)
            exitos += 1
        
        st.success(f"✅ Asistencia guardada para {exitos} estudiantes")
        st.balloons()


# ============================================
# ESTUDIANTE - VER SU ASISTENCIA
# ============================================

def mostrar_asistencia_estudiante(data):
    st.subheader("📋 Mi Asistencia")
    
    documento = data.get('documento')
    headers = get_headers()
    
    # Obtener asistencia del estudiante
    url = f"{SUPABASE_URL}/rest/v1/asistencia?documento_estudiante=eq.{documento}"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        st.error("Error al cargar asistencia")
        return
    
    asistencias = response.json()
    
    if not asistencias:
        st.info("No hay registros de asistencia")
        return
    
    # Convertir a DataFrame
    df = pd.DataFrame(asistencias)
    df['fecha'] = pd.to_datetime(df['fecha'])
    
    # Estadísticas
    total = len(df)
    presentes = len(df[df['estado'] == 'Presente'])
    ausentes = len(df[df['estado'] == 'Ausente'])
    retardos = len(df[df['estado'] == 'Retardo'])
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📊 Total", total)
    col2.metric("✅ Presentes", presentes)
    col3.metric("❌ Ausentes", ausentes)
    col4.metric("⏰ Retardos", retardos)
    
    # Porcentaje de asistencia
    porcentaje = (presentes / total * 100) if total > 0 else 0
    st.progress(porcentaje / 100)
    st.caption(f"📈 Porcentaje de asistencia: {porcentaje:.1f}%")
    
    st.divider()
    
    # Mostrar tabla de asistencia
    st.write("**Detalle de asistencia:**")
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
    
    # Obtener hijos
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
        
        with st.expander(f"📘 {nombre_hijo} - Curso {hijo.get('curso')}"):
            url_asist = f"{SUPABASE_URL}/rest/v1/asistencia?documento_estudiante=eq.{doc_hijo}"
            response_asist = requests.get(url_asist, headers=headers)
            
            if response_asist.status_code == 200:
                asistencias = response_asist.json()
                if asistencias:
                    df = pd.DataFrame(asistencias)
                    df['fecha'] = pd.to_datetime(df['fecha'])
                    
                    # Estadísticas
                    total = len(df)
                    presentes = len(df[df['estado'] == 'Presente'])
                    porcentaje = (presentes / total * 100) if total > 0 else 0
                    
                    st.write(f"**Total días:** {total}")
                    st.write(f"**Presentes:** {presentes}")
                    st.write(f"**Porcentaje:** {porcentaje:.1f}%")
                    
                    st.progress(porcentaje / 100)
                    
                    # Tabla
                    df_mostrar = df[['fecha', 'estado']].sort_values('fecha', ascending=False)
                    df_mostrar['fecha'] = df_mostrar['fecha'].dt.strftime('%d/%m/%Y')
                    st.dataframe(df_mostrar, use_container_width=True)
                else:
                    st.info("Sin registros de asistencia")


# ============================================
# DIRECTOR - VER ASISTENCIA DEL CURSO
# ============================================

def mostrar_asistencia_director(data):
    st.subheader("📋 Asistencia del Curso")
    
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
    
    # Seleccionar período
    fecha_inicio = st.date_input("Fecha inicio")
    fecha_fin = st.date_input("Fecha fin")
    
    if st.button("📊 Ver reporte", type="primary"):
        # Obtener estudiantes
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
            
            # Obtener asistencias en el período
            url_asist = f"{SUPABASE_URL}/rest/v1/asistencia?documento_estudiante=eq.{doc}&fecha=gte.{fecha_inicio}&fecha=lte.{fecha_fin}"
            response_asist = requests.get(url_asist, headers=headers)
            
            if response_asist.status_code == 200:
                asistencias = response_asist.json()
                total = len(asistencias)
                presentes = len([a for a in asistencias if a['estado'] == 'Presente'])
                porcentaje = (presentes / total * 100) if total > 0 else 0
                
                reporte.append({
                    "Estudiante": nombre,
                    "Total días": total,
                    "Presentes": presentes,
                    "Porcentaje": f"{porcentaje:.1f}%"
                })
        
        if reporte:
            df = pd.DataFrame(reporte)
            st.dataframe(df, use_container_width=True)
            
            # Descargar
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar reporte", data=csv, file_name=f"asistencia_{curso}.csv", mime="text/csv")
