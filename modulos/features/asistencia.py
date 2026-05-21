import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from utils import SUPABASE_URL, get_headers

# ============================================
# DOCENTE - MARCAR ASISTENCIA
# ============================================

def mostrar_asistencia_docente(data):
    # ... (tu código existente) ...
    pass

# ============================================
# ESTUDIANTE - VER ASISTENCIA
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
    
    st.progress(porcentaje / 100)
    
    st.divider()
    
    st.write("**Registro:**")
    df_mostrar = df[['fecha', 'estado']].sort_values('fecha', ascending=False)
    df_mostrar['fecha'] = df_mostrar['fecha'].dt.strftime('%d/%m')
    st.dataframe(df_mostrar, use_container_width=True)

# ============================================
# ACUDIENTE - VER ASISTENCIA DE HIJOS
# ============================================

def mostrar_asistencia_acudiente(data):
    # ... (tu código existente) ...
    pass

# ============================================
# DIRECTOR - REPORTE DE ASISTENCIA
# ============================================

def mostrar_asistencia_director(data):
    # ... (tu código existente) ...
    pass
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
    
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        st.markdown("**Estudiante**")
    with col2:
        st.markdown("**Estado**")
    with col3:
        st.markdown("**Justificada?**")
    st.markdown("---")
    
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
