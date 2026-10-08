# ==============================================================================
# modulos/paneles/admin.py - PANEL ADMINISTRADOR
# ==============================================================================

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from utils import SUPABASE_URL, get_headers

# Importación directa y segura
import modulos.features.horarios as horarios_feature

# ============================================
# CONSTANTES
# ============================================
CURSOS = ["901", "902", "903", "1001", "1002", "1003", "1101"]
DIAS_SEMANA = {1: "Lunes", 2: "Martes", 3: "Miercoles", 4: "Jueves", 5: "Viernes", 6: "Sabado"}
PARENTESCOS = ["Padre", "Madre", "Tio", "Tia", "Abuelo", "Abuela", "Tutor Legal", "Otro"]
SEXOS = ["", "Masculino", "Femenino"]
TIPOS_CONTRATO = ["", "Planta", "Contrato", "Catedra", "Ocasional"]

# ============================================
# VISTA PRINCIPAL: DASHBOARD ADMIN
# ============================================
def mostrar(data):
    headers = get_headers()
    
    st.markdown("""
    <div style="background: white; padding: 18px 22px; border-radius: 12px; border: 1px solid #E2E8F0; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <div>
            <h2 style="margin: 0; font-size: 19px; font-weight: 700; color: #0F172A;">COLEGIO DE PRUEBA</h2>
            <p style="margin: 2px 0 0 0; font-size: 12.5px; color: #64748B; font-style: italic;">"Preparando gente para el futuro"</p>
        </div>
        <div style="text-align: right;">
            <span style="background: #DCFCE7; color: #166534; font-size: 11.5px; font-weight: 600; padding: 4px 9px; border-radius: 16px;">Sistema Activo</span>
            <span style="background: #EEF2F6; color: #334155; font-size: 11.5px; font-weight: 600; padding: 4px 9px; border-radius: 16px; margin-left: 6px;">Año 2026</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    try:
        r_est = requests.get(f"{SUPABASE_URL}/rest/v1/estudiantes?select=id", headers=headers)
        total_estudiantes = len(r_est.json()) if r_est.status_code == 200 else 0
    except Exception:
        total_estudiantes = 0

    try:
        r_doc = requests.get(f"{SUPABASE_URL}/rest/v1/docentes?select=documento_docente", headers=headers)
        total_docentes = len(r_doc.json()) if r_doc.status_code == 200 else 0
    except Exception:
        total_docentes = 0

    try:
        r_cur = requests.get(f"{SUPABASE_URL}/rest/v1/grados?select=id_grado", headers=headers)
        total_cursos = len(r_cur.json()) if r_cur.status_code == 200 and r_cur.json() else len(CURSOS)
    except Exception:
        total_cursos = len(CURSOS)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Estudiantes", total_estudiantes)
    with col2:
        st.metric("Docentes", total_docentes)
    with col3:
        st.metric("Cursos", total_cursos)
    with col4:
        st.metric("Acudientes", "180+")

    st.write("")
    st.subheader("Acceso Rapido")
    st.info("Gestiona la institucion a traves de las pestañas superiores del menu.")


# ============================================
# GESTION DE ESTUDIANTES
# ============================================
def gestion_estudiantes():
    st.subheader("Gestion de Estudiantes")
    headers = get_headers()
    
    tab1, tab2 = st.tabs(["Directorio de Alumnos", "Matricular Estudiante"])
    
    with tab1:
        try:
            response = requests.get(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers)
            if response.status_code == 200:
                estudiantes = response.json()
                if estudiantes:
                    df = pd.DataFrame(estudiantes)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No hay estudiantes registrados.")
        except Exception as e:
            st.error(f"Error: {e}")
            
    with tab2:
        with st.form("nuevo_estudiante", clear_on_submit=True):
            nombre = st.text_input("Nombre *")
            apellidos = st.text_input("Apellidos *")
            documento = st.text_input("Documento *")
            curso = st.selectbox("Curso *", CURSOS)
            if st.form_submit_button("Guardar Estudiante"):
                if nombre and apellidos and documento:
                    data = {"nombre_estudiante": nombre, "apellidos_estudiante": apellidos, "documento_estudiante": documento, "curso": curso, "estado": "Activo"}
                    r = requests.post(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers, json=data)
                    if r.status_code == 201:
                        st.success("Estudiante matriculado")
                        st.rerun()


# ============================================
# GESTION DE DOCENTES
# ============================================
def gestion_docentes():
    st.subheader("Gestion de Docentes")
    headers = get_headers()
    
    r = requests.get(f"{SUPABASE_URL}/rest/v1/docentes?order=apellidos_docente.asc", headers=headers)
    if r.status_code == 200 and r.json():
        st.dataframe(pd.DataFrame(r.json()), use_container_width=True)
    else:
        st.info("No hay docentes registrados.")


# ============================================
# GESTION ACADEMICA
# ============================================
def configurar_niveles():
    horarios_feature.configurar_niveles(get_headers())

def gestionar_asignaturas():
    st.subheader("Asignaturas y Pensum")
    st.info("Configuracion de asignaturas.")

def gestionar_grados():
    st.subheader("Cursos y Salones")
    headers = get_headers()
    r = requests.get(f"{SUPABASE_URL}/rest/v1/grados?order=curso.asc", headers=headers)
    if r.status_code == 200 and r.json():
        st.dataframe(pd.DataFrame(r.json()), use_container_width=True)

def gestion_directores_grupo():
    st.subheader("Directores de Grupo")
    st.info("Asignacion de directores de grupo.")

def asignar_docentes_curso():
    st.subheader("Carga Academica Docente")
    st.info("Asignacion de materias a docentes.")


# ============================================
# HORARIOS Y JORNADAS
# ============================================
def configurar_horas_nivel():
    horarios_feature.configurar_horas_nivel(get_headers())

def configurar_jornada_nivel():
    horarios_feature.configurar_jornada_nivel(get_headers())

def configurar_horario_curso():
    horarios_feature.configurar_horario_curso(get_headers())

def gestion_festivos():
    horarios_feature.gestion_festivos(get_headers())

def mostrar_sistema():
    st.subheader("Configuracion Institucional")
    st.info("Parametros generales de la institucion.")

def reportes_academicos():
    st.subheader("Reportes Academicos")
    st.info("Reportes y consolidados.")
