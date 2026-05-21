import streamlit as st
import requests
import pandas as pd
from utils import SUPABASE_URL, get_headers

# ============================================
# CONFIGURACIÓN DE TIPOS DE NOTA (VERSIÓN COMPACTA)
# ============================================

def mostrar_configuracion_notas(data):
    st.subheader("⚙️ Configurar Notas")
    
    documento_docente = data.get('documento')
    headers = get_headers()
    
    url = f"{SUPABASE_URL}/rest/v1/asignacion_academica?documento_docente=eq.{documento_docente}&asignatura=neq.Dirección de Curso"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        st.error("Error")
        return
    
    materias = response.json()
    if not materias:
        st.warning("Sin materias")
        return
    
    opciones = [f"{m.get('curso')} - {m.get('asignatura')}" for m in materias]
    seleccion = st.selectbox("Materia", opciones, key="config_materia")
    curso = seleccion.split(" - ")[0]
    asignatura = seleccion.split(" - ")[1]
    
    # ============================================
    # AGREGAR (compacto)
    # ============================================
    with st.expander("➕ Nueva", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            nuevo_tipo = st.text_input("Nombre", placeholder="Taller")
        with col2:
            nuevo_pct = st.number_input("%", min_value=0, max_value=100, value=20, step=10)
        
        if st.button("Agregar", use_container_width=True):
            if nuevo_tipo:
                data_insert = {
                    "curso": curso,
                    "asignatura": asignatura,
                    "tipo_nota": nuevo_tipo,
                    "porcentaje": nuevo_pct,
                    "orden": 1,
                    "documento_docente": documento_docente
                }
                r = requests.post(f"{SUPABASE_URL}/rest/v1/config_tipos_nota", headers=headers, json=data_insert)
                if r.status_code == 201:
                    st.success("OK")
                    st.rerun()
    
    # ============================================
    # LISTA COMPACTA
    # ============================================
    url_config = f"{SUPABASE_URL}/rest/v1/config_tipos_nota?curso=eq.{curso}&asignatura=eq.{asignatura}"
    response_config = requests.get(url_config, headers=headers)
    
    if response_config.status_code == 200:
        tipos = response_config.json()
        
        if tipos:
            # Mostrar cada tipo con botones en la misma línea
            for tipo in tipos:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{tipo['tipo_nota']}** {tipo['porcentaje']}%")
                with col2:
                    if st.button("✏️", key=f"e_{tipo['id']}"):
                        st.session_state[f"edit_{tipo['id']}"] = tipo
                with col3:
                    if st.button("🗑️", key=f"d_{tipo['id']}"):
                        requests.delete(f"{SUPABASE_URL}/rest/v1/config_tipos_nota?id=eq.{tipo['id']}", headers=headers)
                        st.success("✅")
                        st.rerun()
                
                # Edición en línea (solo cuando se activa)
                if st.session_state.get(f"edit_{tipo['id']}"):
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
                            st.success("✅")
                            st.rerun()
                    st.divider()
            
            # Total
            total = sum(t['porcentaje'] for t in tipos)
            if total == 100:
                st.caption(f"✅ Total: {total}%")
            else:
                st.caption(f"⚠️ Total: {total}%")
        else:
            st.info("Sin tipos")
    else:
        st.error("Error")


# ============================================
# INGRESO DE NOTAS (VERSIÓN COMPACTA)
# ============================================

def mostrar_ingreso_notas(data):
    st.subheader("📝 Ingresar Notas")
    
    documento_docente = data.get('documento')
    headers = get_headers()
    
    url = f"{SUPABASE_URL}/rest/v1/asignacion_academica?documento_docente=eq.{documento_docente}&asignatura=neq.Dirección de Curso"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        st.error("Error")
        return
    
    materias = response.json()
    if not materias:
        st.warning("Sin materias")
        return
    
    opciones = [f"{m.get('curso')} - {m.get('asignatura')}" for m in materias]
    seleccion = st.selectbox("Materia", opciones, key="ingreso_materia")
    curso = seleccion.split(" - ")[0]
    asignatura = seleccion.split(" - ")[1]
    
    periodo = st.selectbox("Período", ["1", "2", "3", "4"])
    periodo_num = int(periodo)
    
    # Obtener tipos de nota
    url_config = f"{SUPABASE_URL}/rest/v1/config_tipos_nota?curso=eq.{curso}&asignatura=eq.{asignatura}"
    response_config = requests.get(url_config, headers=headers)
    
    tipos_nota = response_config.json() if response_config.status_code == 200 else []
    
    if not tipos_nota:
        st.warning("Configure notas primero")
        if st.button("Configurar"):
            st.session_state.menu_docente = "⚙️ Configurar Notas"
            st.rerun()
        return
    
    # Obtener estudiantes
    url_est = f"{SUPABASE_URL}/rest/v1/estudiantes?curso=eq.{curso}"
    response_est = requests.get(url_est, headers=headers)
    estudiantes = response_est.json() if response_est.status_code == 200 else []
    
    if not estudiantes:
        st.warning("Sin estudiantes")
        return
    
    # Mostrar tipos
    st.caption(f"**{asignatura}** - Tipos: " + ", ".join([f"{t['tipo_nota']}({t['porcentaje']}%)" for t in tipos_nota]))
    st.divider()
    
    # Obtener notas existentes
    notas_existentes = {}
    url_notas = f"{SUPABASE_URL}/rest/v1/notas?curso=eq.{curso}&asignatura=eq.{asignatura}&periodo=eq.{periodo_num}"
    response_notas = requests.get(url_notas, headers=headers)
    
    if response_notas.status_code == 200:
        for n in response_notas.json():
            key = f"{n['documento_estudiante']}_{n['tipo_nota']}"
            notas_existentes[key] = n['nota']
    
    # Formulario compacto
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
    
    # Resumen rápido
    if st.button("💾 Guardar", type="primary", use_container_width=True):
        for doc, datos in datos_notas.items():
            for tipo in tipos_nota:
                tipo_nombre = tipo['tipo_nota']
                nota = datos.get(tipo_nombre, 0)
                
                check_url = f"{SUPABASE_URL}/rest/v1/notas?documento_estudiante=eq.{doc}&curso=eq.{curso}&asignatura=eq.{asignatura}&periodo=eq.{periodo_num}&tipo_nota=eq.{tipo_nombre}"
                check = requests.get(check_url, headers=headers)
                
                data_nota = {
                    "documento_estudiante": doc,
                    "curso": curso,
                    "asignatura": asignatura,
                    "periodo": periodo_num,
                    "tipo_nota": tipo_nombre,
                    "nota": nota,
                    "documento_docente": documento_docente
                }
                
                if check.status_code == 200 and check.json():
                    id_nota = check.json()[0]['id']
                    requests.patch(f"{SUPABASE_URL}/rest/v1/notas?id=eq.{id_nota}", headers=headers, json={"nota": nota})
                else:
                    requests.post(f"{SUPABASE_URL}/rest/v1/notas", headers=headers, json=data_nota)
        
        st.success("✅ Guardado")
        st.balloons()


# ============================================
# CONSULTA DE NOTAS
# ============================================

def mostrar_consulta_notas_estudiante(data):
    st.subheader("📖 Mis Notas")
    
    documento = data.get('documento')
    headers = get_headers()
    
    url = f"{SUPABASE_URL}/rest/v1/notas?documento_estudiante=eq.{documento}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        notas = response.json()
        if notas:
            df = pd.DataFrame(notas)
            for _, row in df.iterrows():
                st.write(f"**{row['asignatura']}** - {row['tipo_nota']}: {row['nota']}")
        else:
            st.info("Sin notas")
    else:
        st.error("Error")


# ============================================
# REPORTE
# ============================================

def mostrar_reporte_notas(data):
    st.subheader("📊 Reportes")
    st.info("Próximamente")
