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
    
    # Selección con 3 columnas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        opciones = [f"{m.get('curso')} - {m.get('asignatura')}" for m in materias]
        seleccion = st.selectbox("Materia", opciones, key="config_materia")
        curso = seleccion.split(" - ")[0]
        asignatura = seleccion.split(" - ")[1]
    
    with col2:
        periodo = st.selectbox("Período", ["1", "2", "3", "4"], key="config_periodo")
        periodo_num = int(periodo)
    
    with col3:
        corte = st.selectbox("Corte", ["1", "2", "3"], key="config_corte")
        corte_num = int(corte)
    
    st.success(f"**{curso} - {asignatura} - Período {periodo_num} - Corte {corte_num}**")
    
    # Mostrar tipos existentes
    url_config = f"{SUPABASE_URL}/rest/v1/config_tipos_nota?curso=eq.{curso}&asignatura=eq.{asignatura}&periodo=eq.{periodo_num}&corte=eq.{corte_num}"
    response_config = requests.get(url_config, headers=headers)
    
    if response_config.status_code == 200:
        tipos = response_config.json()
        if tipos:
            st.write("**Tipos de nota configurados:**")
            for t in tipos:
                st.write(f"- {t['tipo_nota']}: {t['porcentaje']}%")
        else:
            st.info("No hay tipos de nota para este período y corte")
    
    # Agregar nuevo tipo
    st.divider()
    st.write("**Agregar nuevo tipo de nota:**")
    
    col1, col2 = st.columns(2)
    with col1:
        nuevo_tipo = st.text_input("Nombre", placeholder="Taller, Quiz, Examen")
    with col2:
        nuevo_porcentaje = st.number_input("Porcentaje (%)", min_value=0, max_value=100, value=20, step=5)
    
    if st.button("Agregar"):
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
    
    # Selección con 3 columnas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        opciones = [f"{m.get('curso')} - {m.get('asignatura')}" for m in materias]
        seleccion = st.selectbox("Materia", opciones, key="ingreso_materia")
        curso = seleccion.split(" - ")[0]
        asignatura = seleccion.split(" - ")[1]
    
    with col2:
        periodo = st.selectbox("Período", ["1", "2", "3", "4"], key="ingreso_periodo")
        periodo_num = int(periodo)
    
    with col3:
        corte = st.selectbox("Corte", ["1", "2", "3"], key="ingreso_corte")
        corte_num = int(corte)
    
    st.success(f"**{asignatura} - Período {periodo_num} - Corte {corte_num}**")
    
    # Obtener configuración de tipos de nota
    url_config = f"{SUPABASE_URL}/rest/v1/config_tipos_nota?curso=eq.{curso}&asignatura=eq.{asignatura}&periodo=eq.{periodo_num}&corte=eq.{corte_num}"
    response_config = requests.get(url_config, headers=headers)
    tipos_nota = response_config.json() if response_config.status_code == 200 else []
    
    if not tipos_nota:
        st.warning(f"No hay tipos de nota configurados para este período y corte")
        # Botón para ir a configuración de notas (siempre visible)
if st.button("⚙️ Configurar Notas", type="primary"):
    # Mostrar la configuración directamente aquí
    st.session_state.mostrar_configuracion = not st.session_state.get('mostrar_configuracion', False)

# Si el usuario activó la configuración, mostrarla
if st.session_state.get('mostrar_configuracion', False):
    st.divider()
    st.subheader("⚙️ Configuración de Notas")
    
    # Aquí va el código de configuración de notas
    mostrar_configuracion_notas(data)
    
    if st.button("🔙 Volver a Ingresar Notas"):
        st.session_state.mostrar_configuracion = False
        st.rerun()
        return
    
    # Obtener estudiantes
    url_est = f"{SUPABASE_URL}/rest/v1/estudiantes?curso=eq.{curso}"
    response_est = requests.get(url_est, headers=headers)
    estudiantes = response_est.json() if response_est.status_code == 200 else []
    
    if not estudiantes:
        st.warning("No hay estudiantes")
        return
    
    # Mostrar cabecera
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
    
    # Formulario de notas
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
                if doc not in datos_notas:
                    datos_notas[doc] = {}
                datos_notas[doc][tipo_nombre] = nota
                
                pct = tipo['porcentaje'] / 100
                suma_ponderada += nota * pct
        
        with cols[-1]:
            st.write(f"**{round(suma_ponderada, 1)}**")
    
    st.markdown("---")
    
    # Guardar notas
    if st.button("💾 Guardar", type="primary", use_container_width=True):
        guardados = 0
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
                guardados += 1
        
        st.success(f"✅ {guardados} notas guardadas para {asignatura} - Período {periodo_num} - Corte {corte_num}")
        st.balloons()


# ============================================
# FUNCIONES PARA ESTUDIANTE
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
    
    for asignatura in df['asignatura'].unique():
        df_asig = df[df['asignatura'] == asignatura]
        with st.expander(f"📘 {asignatura}"):
            
            promedios_periodo = {}
            
            for periodo in sorted(df_asig['periodo'].unique()):
                df_periodo = df_asig[df_asig['periodo'] == periodo]
                promedios_corte = {}
                
                for corte in sorted(df_periodo['corte'].unique()):
                    df_corte = df_periodo[df_periodo['corte'] == corte]
                    
                    st.markdown(f"**Período {periodo} - Corte {corte}**")
                    
                    for _, row in df_corte.iterrows():
                        st.write(f"- {row['tipo_nota']}: {row['nota']}")
                    
                    promedio_corte = df_corte['nota'].mean()
                    st.caption(f"📊 Promedio del corte: {promedio_corte:.1f}")
                    promedios_corte[corte] = promedio_corte
                    st.divider()
                
                if promedios_corte:
                    promedio_periodo = sum(promedios_corte.values()) / len(promedios_corte)
                    st.info(f"**Promedio del Período {periodo}: {promedio_periodo:.1f}**")
                    promedios_periodo[periodo] = promedio_periodo
                    st.divider()
            
            if promedios_periodo:
                nota_final = sum(promedios_periodo.values()) / len(promedios_periodo)
                st.success(f"🎯 **NOTA FINAL: {nota_final:.1f}**")


# ============================================
# FUNCIONES PARA ACUDIENTE
# ============================================

def mostrar_notas_acudiente(data):
    st.subheader("👨‍👩‍👧 Calificaciones de mis hijos")
    
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
        
        with st.expander(f"📘 {nombre_hijo} - Curso {hijo.get('curso')}"):
            url_notas = f"{SUPABASE_URL}/rest/v1/notas?documento_estudiante=eq.{doc_hijo}"
            response_notas = requests.get(url_notas, headers=headers)
            
            if response_notas.status_code == 200:
                notas = response_notas.json()
                if notas:
                    df = pd.DataFrame(notas)
                    
                    for asignatura in df['asignatura'].unique():
                        st.write(f"**{asignatura}**")
                        df_asig = df[df['asignatura'] == asignatura]
                        for periodo in sorted(df_asig['periodo'].unique()):
                            for corte in sorted(df_asig['corte'].unique()):
                                df_corte = df_asig[(df_asig['periodo'] == periodo) & (df_asig['corte'] == corte)]
                                st.write(f"  Período {periodo} - Corte {corte}:")
                                for _, row in df_corte.iterrows():
                                    st.write(f"    - {row['tipo_nota']}: {row['nota']}")
                                promedio = df_corte['nota'].mean()
                                st.write(f"    Promedio: {promedio:.1f}")
                        st.divider()
                else:
                    st.info("Sin calificaciones")


# ============================================
# FUNCIONES PARA DIRECTOR
# ============================================

def mostrar_notas_curso(data):
    st.subheader("📊 Calificaciones del Curso")
    
    documento_docente = data.get('documento')
    headers = get_headers()
    
    url_dir = f"{SUPABASE_URL}/rest/v1/asignacion_academica?documento_docente=eq.{documento_docente}&asignatura=eq.Dirección de Curso"
    response_dir = requests.get(url_dir, headers=headers)
    
    if response_dir.status_code != 200 or not response_dir.json():
        st.warning("No eres director de ningún curso")
        return
    
    curso = response_dir.json()[0].get('curso')
    st.success(f"📌 Curso: {curso}")
    
    url_est = f"{SUPABASE_URL}/rest/v1/estudiantes?curso=eq.{curso}"
    response_est = requests.get(url_est, headers=headers)
    
    if response_est.status_code != 200:
        st.error("Error al cargar estudiantes")
        return
    
    estudiantes = response_est.json()
    
    if not estudiantes:
        st.info("No hay estudiantes en el curso")
        return
    
    for estudiante in estudiantes:
        nombre = estudiante.get('nombre_estudiante')
        doc = estudiante.get('documento_estudiante')
        
        url_notas = f"{SUPABASE_URL}/rest/v1/notas?documento_estudiante=eq.{doc}&curso=eq.{curso}"
        response_notas = requests.get(url_notas, headers=headers)
        
        if response_notas.status_code == 200:
            notas = response_notas.json()
            if notas:
                df = pd.DataFrame(notas)
                with st.expander(f"📘 {nombre}"):
                    st.dataframe(df[['asignatura', 'periodo', 'corte', 'tipo_nota', 'nota']], use_container_width=True)
            else:
                st.write(f"**{nombre}** - Sin notas")
