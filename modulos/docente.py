import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from utils import get_headers, SUPABASE_URL

def mostrar(data):
    st.title(f"🍎 Panel del Docente")
    st.write(f"Bienvenido, {data['nombre']}")
    
    # ========== DEPURACIÓN ==========
    st.subheader("🔍 Información de depuración")
    st.write(f"**ID del docente:** {data.get('id_persona', 'No encontrado')}")
    
    headers = get_headers()
    
    # URL de consulta
    id_docente = data.get('id_persona', 0)
    url_cursos = f"{SUPABASE_URL}/rest/v1/asignacion_academica?id_docente=eq.{id_docente}"
    st.write(f"**Consultando URL:** {url_cursos}")
    
    # Hacer la consulta
    response_cursos = requests.get(url_cursos, headers=headers)
    st.write(f"**Código de respuesta:** {response_cursos.status_code}")
    
    if response_cursos.status_code == 200:
        datos = response_cursos.json()
        st.write(f"**Datos encontrados:** {datos}")
        st.write(f"**Cantidad de registros:** {len(datos)}")
        
        if not datos:
            st.warning("⚠️ No se encontraron cursos para este docente en la tabla 'asignacion_academica'")
            st.info("Consejo: Verifica que la tabla 'asignacion_academica' tenga registros con id_docente = " + str(id_docente))
            return
    else:
        st.error(f"❌ Error al consultar Supabase: {response_cursos.text}")
        return
    
    # ========== PROCESAR CURSOS ==========
    cursos = []
    for curso in response_cursos.json():
        grado_id = curso.get("id_grado")
        materia_id = curso.get("id_materia")
        
        # Obtener nombre del grado
        url_grado = f"{SUPABASE_URL}/rest/v1/grados?id_grado=eq.{grado_id}"
        resp_grado = requests.get(url_grado, headers=headers)
        grado_nombre = resp_grado.json()[0]["nombre"] if resp_grado.json() else f"Grado {grado_id}"
        
        # Obtener nombre de la materia
        url_materia = f"{SUPABASE_URL}/rest/v1/materias?id_materia=eq.{materia_id}"
        resp_materia = requests.get(url_materia, headers=headers)
        materia_nombre = resp_materia.json()[0]["nombre"] if resp_materia.json() else f"Materia {materia_id}"
        
        cursos.append({
            "id_grado": grado_id,
            "grado_nombre": grado_nombre,
            "id_materia": materia_id,
            "materia_nombre": materia_nombre
        })
    
    st.success(f"✅ Se encontraron {len(cursos)} cursos asignados")
    
    # Selector de curso
    curso_seleccionado = st.selectbox(
        "Seleccionar curso",
        cursos,
        format_func=lambda x: f"{x['materia_nombre']} - {x['grado_nombre']}"
    )
    
    if curso_seleccionado:
        grado_id = curso_seleccionado["id_grado"]
        materia_id = curso_seleccionado["id_materia"]
        materia_nombre = curso_seleccionado["materia_nombre"]
        
        st.success(f"📚 Trabajando con: **{materia_nombre}**")
        
        # Obtener estudiantes del grado
        url_estudiantes = f"{SUPABASE_URL}/rest/v1/estudiantes_grados?id_grado=eq.{grado_id}"
        response_estudiantes = requests.get(url_estudiantes, headers=headers)
        
        if response_estudiantes.status_code != 200 or not response_estudiantes.json():
            st.info("No hay estudiantes en este curso")
            return
        
        # Lista de estudiantes
        estudiantes = []
        for est_rel in response_estudiantes.json():
            id_estudiante = est_rel["id_estudiante"]
            url_est = f"{SUPABASE_URL}/rest/v1/personas?id_persona=eq.{id_estudiante}"
            resp_est = requests.get(url_est, headers=headers)
            if resp_est.status_code == 200 and resp_est.json():
                estudiantes.append({
                    "id": id_estudiante,
                    "nombre": resp_est.json()[0]["nombre"]
                })
        
        # Mostrar estudiantes
        st.subheader(f"👥 Estudiantes del curso ({len(estudiantes)})")
        for est in estudiantes:
            st.write(f"• {est['nombre']}")
