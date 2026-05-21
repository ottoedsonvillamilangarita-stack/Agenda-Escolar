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
