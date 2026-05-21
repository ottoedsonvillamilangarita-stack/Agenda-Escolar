import streamlit as st
import requests
import pandas as pd
from utils import SUPABASE_URL, get_headers

# ============================================
# CONFIGURACIÓN DE TIPOS DE NOTA
# ============================================

def mostrar_configuracion_notas(data):
    st.subheader("⚙️ Configurar Notas")
    
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
    seleccion = st.selectbox("Materia", opciones, key="config_materia")
    curso = seleccion.split(" - ")[0]
    asignatura = seleccion.split(" - ")[1]
    
    st.success(f"**{curso} - {asignatura}**")
    
    # ============================================
    # AGREGAR
    # ============================================
    with st.expander("➕ Agregar tipo de nota", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            nuevo_tipo = st.text_input("Nombre", placeholder="Taller, Quiz, Examen")
        with col2:
            nuevo_porcentaje = st.number_input("%", min_value=0, max_value=100, value=20, step=5)
        
        if st.button("Agregar", use_container_width=True):
            if nuevo_tipo:
                data_insert = {
                    "curso": curso,
                    "asignatura": asignatura,
                    "tipo_nota": nuevo_tipo,
                    "porcentaje": nuevo_porcentaje,
                    "orden": 1,
                    "documento_docente": documento_docente
                }
                r = requests.post(f"{SUPABASE_URL}/rest/v1/config_tipos_nota", headers=headers, json=data_insert)
                if r.status_code == 201:
                    st.success("✅ Agregado")
                    st.rerun()
    
    st.divider()
    
    # ============================================
    # LISTA
    # ============================================
    url_config = f"{SUPABASE_URL}/rest/v1/config_tipos_nota?curso=eq.{curso}&asignatura=eq.{asignatura}"
    response_config = requests.get(url_config, headers=headers)
    
    if response_config.status_code == 200:
        tipos = response_config.json()
        
        if tipos:
            for tipo in tipos:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{tipo['tipo_nota']}** - {tipo['porcentaje']}%")
                with col2:
                    if st.button("✏️", key=f"edit_{tipo['id']}"):
                        st.session_state[f"edit_{tipo['id']}"] = True
                with col3:
                    if st.button("🗑️", key=f"del_{tipo['id']}"):
                        requests.delete(f"{SUPABASE_URL}/rest/v1/config_tipos_nota?id=eq.{tipo['id']}", headers=headers)
                        st.success("✅ Eliminado")
                        st.rerun()
                
                if st.session_state.get(f"edit_{tipo['id']}", False):
                    col_a, col_b, col_c = st.columns([2, 1, 1])
                    with col_a:
                        new_nombre = st.text_input("", value=tipo['tipo_nota'], key=f"n_{tipo['id']}", label_visibility="collapsed")
                    with col_b:
                        new_pct = st.number_input("", min_value=0, max_value=100, value=tipo['porcentaje'], key=f"p_{tipo['id']}", label_visibility="collapsed")
                    with col_c:
                        if st.button("💾", key=f"s_{tipo['id']}"):
                            requests.patch(f"{SUPABASE_URL}/rest/v1/config_tipos_nota?id=eq.{tipo['id']}", 
                                         headers=headers, json={"tipo_nota": new_nombre, "porcentaje": new_pct})
                            st.session_state[f"edit_{tipo['id']}"] = False
                            st.success("✅ Guardado")
                            st.rerun()
                    st.divider()
            
            total = sum(t['porcentaje'] for t in tipos)
            if total == 100:
                st.caption(f"✅ Total: {total}%")
            else:
                st.caption(f"⚠️ Total: {total}%")
        else:
            st.info("No hay tipos de nota")
    else:
        st.error("Error al cargar")


# ============================================
# INGRESO DE NOTAS
# ============================================

def mostrar_ingreso_notas(data):
    st.subheader("📝 Ingresar Notas")
    
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
    seleccion = st.selectbox("Materia", opciones, key="ingreso_materia")
    curso = seleccion.split(" - ")[0]
    asignatura = seleccion.split(" - ")[1]
    
    periodos = ["1", "2", "3", "4"]
    periodo = st.selectbox("Período", periodos)
    periodo_num = int(periodo)
    
    url_config = f"{SUPABASE_URL}/rest/v1/config_tipos_nota?curso=eq.{curso}&asignatura=eq.{asignatura}"
    response_config = requests.get(url_config, headers=headers)
    
    tipos_nota = response_config.json() if response_config.status_code == 200 else []
    
    if not tipos_nota:
        st.warning("Configura tipos de nota primero")
        if st.button("Ir a Configurar"):
            st.session_state.menu_docente = "⚙️ Configurar Notas"
            st.rerun()
        return
    
    url_est = f"{SUPABASE_URL}/rest/v1/estudiantes?curso=eq.{curso}"
    response_est = requests.get(url_est, headers=headers)
    estudiantes = response_est.json() if response_est.status_code == 200 else []
    
    if not estudiantes:
        st.warning("No hay estudiantes")
        return
    
    st.caption(f"**{asignatura}** - " + ", ".join([f"{t['tipo_nota']}({t['porcentaje']}%)" for t in tipos_nota]))
    st.divider()
    
    notas_existentes = {}
    url_notas = f"{SUPABASE_URL}/rest/v1/notas?curso=eq.{curso}&asignatura=eq.{asignatura}&periodo=eq.{periodo_num}"
    response_notas = requests.get(url_notas, headers=headers)
    
    if response_notas.status_code == 200:
        for n in response_notas.json():
            key = f"{n['documento_estudiante']}_{n['tipo_nota']}"
            notas_existentes[key] = n['nota']
    
    datos_notas = {}
    
    for est in estudiantes:
        doc = est['documento_estudiante']
        nombre = est['nombre_estudiante']
        datos_notas[doc] = {"nombre": nombre}
        
        cols = st.columns([2] + [1] * len(tipos_nota))
        with cols[0]:
            st.write(f"**{nombre[:20]}**")
        
        for idx, tipo in enumerate(tipos_nota):
            tipo_nombre = tipo['tipo_nota']
            key = f"{doc}_{tipo_nombre}"
            valor = notas_existentes.get(key, 0.0)
            with cols[idx + 1]:
                nota = st.number_input("", min_value=0.0, max_value=5.0, step=0.1, value=float(valor), 
                                      key=f"n_{doc}_{tipo_nombre}", label_visibility="collapsed")
                datos_notas[doc][tipo_nombre] = nota
        st.divider()
    
    resumen = []
    for doc, datos in datos_notas.items():
       
