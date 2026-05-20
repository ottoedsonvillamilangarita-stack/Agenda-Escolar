import streamlit as st
import requests
import pandas as pd
from utils import SUPABASE_URL, get_headers

# ============================================
# CONFIGURACIÓN DE TIPOS DE NOTA
# ============================================

def mostrar_configuracion_notas(data):
    st.subheader("⚙️ Configurar Tipos de Nota")
    
    documento_docente = data.get('documento')
    headers = get_headers()
    
    url = f"{SUPABASE_URL}/rest/v1/asignacion_academica?documento_docente=eq.{documento_docente}&asignatura=neq.Dirección de Curso"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        st.error("Error al cargar materias")
        return
    
    materias = response.json()
    if not materias:
        st.warning("No tienes materias asignadas")
        return
    
    opciones = [f"{m.get('curso')} - {m.get('asignatura')}" for m in materias]
    seleccion = st.selectbox("Seleccionar materia", opciones, key="config_materia")
    curso = seleccion.split(" - ")[0]
    asignatura = seleccion.split(" - ")[1]
    
    st.write(f"**Configurando: {curso} - {asignatura}**")
    
    # Agregar nuevo tipo de nota
    st.write("**Agregar nuevo tipo de nota:**")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        nuevo_tipo = st.text_input("Nombre (Ej: Taller, Quiz, Examen)")
    with col2:
        nuevo_porcentaje = st.number_input("Porcentaje (%)", min_value=0, max_value=100, value=20)
    with col3:
        nuevo_orden = st.number_input("Orden", min_value=1, max_value=20, value=1)
    
    if st.button("➕ Agregar Tipo de Nota", type="primary"):
        if not nuevo_tipo:
            st.error("❌ Ingresa un nombre para el tipo de nota")
        else:
            data = {
                "curso": curso,
                "asignatura": asignatura,
                "tipo_nota": nuevo_tipo,
                "porcentaje": nuevo_porcentaje,
                "orden": nuevo_orden,
                "documento_docente": documento_docente
            }
            response = requests.post(f"{SUPABASE_URL}/rest/v1/config_tipos_nota", headers=headers, json=data)
            if response.status_code == 201:
                st.success(f"✅ Tipo de nota '{nuevo_tipo}' agregado")
                st.rerun()
            else:
                st.error(f"Error: {response.status_code}")
    
    # Ver configuración existente
    url_config = f"{SUPABASE_URL}/rest/v1/config_tipos_nota?curso=eq.{curso}&asignatura=eq.{asignatura}&order=orden.asc"
    response_config = requests.get(url_config, headers=headers)
    
    if response_config.status_code == 200:
        tipos = response_config.json()
        if tipos:
            st.write("**Configuración actual:**")
            df = pd.DataFrame(tipos)
            st.dataframe(df[['tipo_nota', 'porcentaje', 'orden']], use_container_width=True)

# ============================================
# INGRESO DE NOTAS
# ============================================

def mostrar_ingreso_notas(data):
    st.subheader("📝 Ingreso de Calificaciones")
    
    documento_docente = data.get('documento')
    headers = get_headers()
    
    url = f"{SUPABASE_URL}/rest/v1/asignacion_academica?documento_docente=eq.{documento_docente}&asignatura=neq.Dirección de Curso"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        st.error("Error al cargar materias")
        return
    
    materias = response.json()
    if not materias:
        st.warning("No tienes materias asignadas")
        return
    
    opciones = [f"{m.get('curso')} - {m.get('asignatura')}" for m in materias]
    seleccion = st.selectbox("Seleccionar materia", opciones, key="ingreso_materia")
    curso = seleccion.split(" - ")[0]
    asignatura = seleccion.split(" - ")[1]
    
    periodos = ["Período 1", "Período 2", "Período 3", "Período 4"]
    periodo = st.selectbox("Período", periodos)
    periodo_num = int(periodo.split()[1])
    
    url_config = f"{SUPABASE_URL}/rest/v1/config_tipos_nota?curso=eq.{curso}&asignatura=eq.{asignatura}&order=orden.asc"
    response_config = requests.get(url_config, headers=headers)
    
    tipos_nota = []
    if response_config.status_code == 200:
        tipos_nota = response_config.json()
    
    if not tipos_nota:
        st.warning("⚠️ No hay tipos de nota configurados. Ve a 'Configurar Notas' primero.")
        return
    
    url_est = f"{SUPABASE_URL}/rest/v1/estudiantes?curso=eq.{curso}"
    response_est = requests.get(url_est, headers=headers)
    
    if response_est.status_code != 200:
        st.error("Error al cargar estudiantes")
        return
    
    estudiantes = response_est.json()
    if not estudiantes:
        st.warning(f"No hay estudiantes en el curso {curso}")
        return
    
    st.write(f"**Ingreso de notas - {asignatura} - {periodo}**")
    
    for estudiante in estudiantes:
        nombre = estudiante.get('nombre_estudiante')
        doc = estudiante.get('documento_estudiante')
        
        st.write(f"**{nombre}**")
        
        cols = st.columns(len(tipos_nota))
        for idx, tipo in enumerate(tipos_nota):
            tipo_nombre = tipo.get('tipo_nota')
            with cols[idx]:
                st.number_input(
                    f"{tipo_nombre}",
                    min_value=0.0,
                    max_value=5.0,
                    step=0.1,
                    key=f"nota_{doc}_{tipo_nombre}",
                    label_visibility="collapsed"
                )
        st.divider()
    
    if st.button("💾 Guardar Calificaciones", type="primary"):
        st.success("✅ Calificaciones guardadas (demo)")
