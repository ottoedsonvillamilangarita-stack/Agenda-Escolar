import streamlit as st
import requests
import pandas as pd
from utils import SUPABASE_URL, get_headers

# ============================================
# FUNCIONES PARA DOCENTE
# ============================================

def mostrar_configuracion_notas(data):
    st.subheader("⚙️ Configurar Tipos de Nota")
    
    documento_docente = data.get('documento')
    headers = get_headers()
    
    # Obtener materias del docente
    url = f"{SUPABASE_URL}/rest/v1/asignacion_academica?documento_docente=eq.{documento_docente}&asignatura=neq.Dirección de Curso"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        st.error("Error al cargar materias")
        return
    
    materias = response.json()
    if not materias:
        st.warning("No tienes materias asignadas")
        return
    
    # Selección de materia, período y corte
    col1, col2, col3 = st.columns(3)
    with col1:
        opciones = [f"{m.get('curso')} - {m.get('asignatura')}" for m in materias]
        seleccion = st.selectbox("Materia", opciones, key="config_materia_select")
        curso = seleccion.split(" - ")[0]
        asignatura = seleccion.split(" - ")[1]
    
    with col2:
        periodo_opciones = ["1", "2", "3", "4"]
        periodo = st.selectbox("Período", periodo_opciones, key="config_periodo_select")
        periodo_num = int(periodo)
    
    with col3:
        corte_opciones = ["1", "2", "3"]
        corte = st.selectbox("Corte", corte_opciones, key="config_corte_select")
        corte_num = int(corte)
    
    st.success(f"**{curso} - {asignatura} - Período {periodo_num} - Corte {corte_num}**")
    
    # Agregar tipo de nota
    with st.expander("➕ Agregar tipo de nota", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            nuevo_tipo = st.text_input("Nombre", placeholder="Taller, Quiz, Examen", key="nuevo_tipo_input")
        with col2:
            nuevo_porcentaje = st.number_input("%", min_value=0, max_value=100, value=20, step=5, key="nuevo_porcentaje_input")
        
        if st.button("Agregar", use_container_width=True, key="agregar_tipo_btn"):
            if nuevo_tipo:
                data_insert = {
                    "curso": curso,
                    "asignatura": asignatura,
                    "periodo": periodo_num,
                    "corte": corte_num,
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
    
    # Lista de tipos de nota
    url_config = f"{SUPABASE_URL}/rest/v1/config_tipos_nota?curso=eq.{curso}&asignatura=eq.{asignatura}&periodo=eq.{periodo_num}&corte=eq.{corte_num}"
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
                        st.session_state[f"editando_{tipo['id']}"] = True
                with col3:
                    if st.button("🗑️", key=f"del_{tipo['id']}"):
                        requests.delete(f"{SUPABASE_URL}/rest/v1/config_tipos_nota?id=eq.{tipo['id']}", headers=headers)
                        st.success("✅ Eliminado")
                        st.rerun()
                
                if st.session_state.get(f"editando_{tipo['id']}", False):
                    col_a, col_b, col_c = st.columns([2, 1, 1])
                    with col_a:
                        new_nombre = st.text_input("", value=tipo['tipo_nota'], key=f"n_{tipo['id']}", label_visibility="collapsed")
                    with col_b:
                        new_pct = st.number_input("", min_value=0, max_value=100, value=tipo['porcentaje'], key=f"p_{tipo['id']}", label_visibility="collapsed")
                    with col_c:
                        if st.button("💾", key=f"s_{tipo['id']}"):
                            requests.patch(f"{SUPABASE_URL}/rest/v1/config_tipos_nota?id=eq.{tipo['id']}", 
                                         headers=headers, json={"tipo_nota": new_nombre, "porcentaje": new_pct})
                            st.session_state[f"editando_{tipo['id']}"] = False
                            st.success("✅ Guardado")
                            st.rerun()
                    st.divider()
            
            total = sum(t['porcentaje'] for t in tipos)
            if total == 100:
                st.caption(f"✅ Total: {total}%")
            else:
                st.caption(f"⚠️ Total: {total}%")
        else:
            st.info("No hay tipos de nota configurados para este período y corte")
    else:
        st.error("Error al cargar datos")


def mostrar_ingreso_notas(data):
    st.subheader("📝 Ingresar Notas")
    
    documento_docente = data.get('documento')
    headers = get_headers()
    
    # Obtener materias
    url = f"{SUPABASE_URL}/rest/v1/asignacion_academica?documento_docente=eq.{documento_docente}&asignatura=neq.Dirección de Curso"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        st.error("Error al cargar materias")
        return
    
    materias = response.json()
    if not materias:
        st.warning("No tienes materias asignadas")
        return
    
    # Selección de materia, período y corte
    col1, col2, col3 = st.columns(3)
    with col1:
        opciones = [f"{m.get('curso')} - {m.get('asignatura')}" for m in materias]
        seleccion = st.selectbox("Materia", opciones, key="ingreso_materia_select")
        curso = seleccion.split(" - ")[0]
        asignatura = seleccion.split(" - ")[1]
    
    with col2:
        periodos = ["1", "2", "3", "4"]
        periodo = st.selectbox("Período", periodos, key="ingreso_periodo_select")
        periodo_num = int(periodo)
    
    with col3:
        cortes = ["1", "2", "3"]
        corte = st.selectbox("Corte", cortes, key="ingreso_corte_select")
        corte_num = int(corte)
    
    # Obtener tipos de nota (con período y corte)
    url_config = f"{SUPABASE_URL}/rest/v1/config_tipos_nota?curso=eq.{curso}&asignatura=eq.{asignatura}&periodo=eq.{periodo_num}&corte=eq.{corte_num}"
    response_config = requests.get(url_config, headers=headers)
    tipos_nota = response_config.json() if response_config.status_code == 200 else []
    
    if not tipos_nota:
        st.warning(f"No hay tipos de nota configurados para {asignatura} - Período {periodo_num} - Corte {corte_num}")
        if st.button("Ir a Configurar", key="ir_configurar_btn"):
            st.session_state.menu_docente = "⚙️ Configurar Notas"
            st.rerun()
        return
    
    # Obtener estudiantes
    url_est = f"{SUPABASE_URL}/rest/v1/estudiantes?curso=eq.{curso}"
    response_est = requests.get(url_est, headers=headers)
    estudiantes = response_est.json() if response_est.status_code == 200 else []
    
    if not estudiantes:
        st.warning("No hay estudiantes")
        return
    
    # Mostrar leyenda
    st.markdown(f"**{asignatura} - Período {periodo_num} - Corte {corte_num}**")
    st.markdown("---")
    cols_headers = st.columns([2] + [1] * len(tipos_nota) + [1])
    with cols_headers[0]:
        st.markdown("**Estudiante**")
    for idx, tipo in enumerate(tipos_nota):
        with cols_headers[idx + 1]:
            st.markdown(f"**{tipo['tipo_nota'][:8]}**<br><small>({tipo['porcentaje']}%)</small>", unsafe_allow_html=True)
    with cols_headers[-1]:
        st.markdown("**Definitiva**")
    st.markdown("---")
    
    # Obtener notas existentes
    notas_existentes = {}
    url_notas = f"{SUPABASE_URL}/rest/v1/notas?curso=eq.{curso}&asignatura=eq.{asignatura}&periodo=eq.{periodo_num}&corte=eq.{corte_num}"
    response_notas = requests.get(url_notas, headers=headers)
    
    if response_notas.status_code == 200:
        for n in response_notas.json():
            key = f"{n['documento_estudiante']}_{n['tipo_nota']}"
            notas_existentes[key] = n['nota']
    
    # Formulario compacto
    datos_notas = {}
    
    for est in estudiantes:
        doc = est['documento_estudiante']
        nombre = est['nombre_estudiante'][:20]
        
        cols = st.columns([2] + [1] * len(tipos_nota) + [1])
        
        with cols[0]:
            st.write(f"**{nombre}**")
        
        suma_ponderada = 0
        for idx, tipo in enumerate(tipos_nota):
            tipo_nombre = tipo['tipo_nota']
            key = f"{doc}_{tipo_nombre}"
            valor = notas_existentes.get(key, 0.0)
            
            with cols[idx + 1]:
                nota = st.number_input(
                    "",
                    min_value=0.0,
                    max_value=5.0,
                    step=0.1,
                    value=float(valor),
                    key=f"n_{doc}_{tipo_nombre}_{periodo_num}_{corte_num}",
                    label_visibility="collapsed"
                )
                datos_notas[doc] = datos_notas.get(doc, {})
                datos_notas[doc][tipo_nombre] = nota
                
                pct = tipo['porcentaje'] / 100
                suma_ponderada += nota * pct
        
        with cols[-1]:
            st.write(f"**{round(suma_ponderada, 1)}**")
    
    st.markdown("---")
    
    if st.button("💾 Guardar", type="primary", use_container_width=True, key="guardar_notas_btn"):
        for doc, notas in datos_notas.items():
            for tipo in tipos_nota:
                tipo_nombre = tipo['tipo_nota']
                nota = notas.get(tipo_nombre, 0)
                
                check_url = f"{SUPABASE_URL}/rest/v1/notas?documento_estudiante=eq.{doc}&curso=eq.{curso}&asignatura=eq.{asignatura}&periodo=eq.{periodo_num}&corte=eq.{corte_num}&tipo_nota=eq.{tipo_nombre}"
                check = requests.get(check_url, headers=headers)
                
                data_nota = {
                    "documento_estudiante": doc,
                    "curso": curso,
                    "asignatura": asignatura,
                    "periodo": periodo_num,
                    "corte": corte_num,
                    "tipo_nota": tipo_nombre,
                    "nota": nota,
                    "documento_docente": documento_docente
                }
                
                if check.status_code == 200 and check.json():
                    id_nota = check.json()[0]['id']
                    requests.patch(f"{SUPABASE_URL}/rest/v1/notas?id=eq.{id_nota}", headers=headers, json={"nota": nota})
                else:
                    requests.post(f"{SUPABASE_URL}/rest/v1/notas", headers=headers, json=data_nota)
        
        st.success(f"✅ Notas guardadas para {asignatura} - Período {periodo_num} - Corte {corte_num}")
        st.balloons()


# ============================================
# FUNCIONES PARA ESTUDIANTE (actualizado)
# ============================================

def mostrar_notas_estudiante(data):
    st.subheader("📖 Mis Calificaciones")
    
    documento = data.get('documento')
    headers = get_headers()
    
    url = f"{SUPABASE_URL}/rest/v1/notas?documento_estudiante=eq.{documento}"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        st.error("Error al cargar notas")
        return
    
    notas = response.json()
    if not notas:
        st.info("No hay calificaciones registradas")
        return
    
    df = pd.DataFrame(notas)
    
    # Agrupar por asignatura, período y corte
    for asignatura in df['asignatura'].unique():
        df_asig = df[df['asignatura'] == asignatura]
        with st.expander(f"📘 {asignatura}"):
            # Mostrar por período y corte
            for periodo in sorted(df_asig['periodo'].unique()):
                df_periodo = df_asig[df_asig['periodo'] == periodo]
                for corte in sorted(df_periodo['corte'].unique()):
                    df_corte = df_periodo[df_periodo['corte'] == corte]
                    st.markdown(f"**Período {periodo} - Corte {corte}**")
                    st.dataframe(df_corte[['tipo_nota', 'nota']], use_container_width=True)
                    promedio = df_corte['nota'].mean()
                    st.caption(f"📊 Promedio del corte: {promedio:.1f}")
                    st.divider()


# El resto de funciones (mostrar_notas_acudiente, mostrar_notas_curso) 
# también deben actualizarse para incluir 'corte', pero por ahora dejamos igual
