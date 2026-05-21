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
    seleccion = st.selectbox("📚 Seleccionar materia", opciones, key="config_materia")
    curso = seleccion.split(" - ")[0]
    asignatura = seleccion.split(" - ")[1]
    
    st.success(f"**{curso} - {asignatura}**")
    
    # ============================================
    # AGREGAR NUEVO TIPO DE NOTA
    # ============================================
    with st.expander("➕ Agregar", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            nuevo_tipo = st.text_input("Nombre", placeholder="Taller, Quiz, Examen")
        with col2:
            nuevo_porcentaje = st.number_input("%", min_value=0, max_value=100, value=20, step=5)
        with col3:
            nuevo_orden = st.number_input("Orden", min_value=1, max_value=20, value=1, step=1)
        
        if st.button("Agregar", type="primary"):
            if nuevo_tipo:
                data_insert = {
                    "curso": curso,
                    "asignatura": asignatura,
                    "tipo_nota": nuevo_tipo,
                    "porcentaje": nuevo_porcentaje,
                    "orden": nuevo_orden,
                    "documento_docente": documento_docente
                }
                response_insert = requests.post(f"{SUPABASE_URL}/rest/v1/config_tipos_nota", headers=headers, json=data_insert)
                if response_insert.status_code == 201:
                    st.success(f"✅ '{nuevo_tipo}' agregado")
                    st.rerun()
                else:
                    st.error("Error")
    
    st.divider()
    
    # ============================================
    # TABLA CON ICONOS
    # ============================================
    url_config = f"{SUPABASE_URL}/rest/v1/config_tipos_nota?curso=eq.{curso}&asignatura=eq.{asignatura}&order=orden.asc"
    response_config = requests.get(url_config, headers=headers)
    
    if response_config.status_code == 200:
        tipos = response_config.json()
        
        if tipos:
            # Estado de edición
            if f"editando_{curso}_{asignatura}" not in st.session_state:
                st.session_state[f"editando_{curso}_{asignatura}"] = None
            
            # Cabecera de la tabla
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                st.markdown("**Tipo de nota**")
            with col2:
                st.markdown("**%**")
            with col3:
                st.markdown("**Editar**")
            with col4:
                st.markdown("**Eliminar**")
            st.divider()
            
            # Mostrar filas
            for tipo in tipos:
                tipo_id = tipo.get('id')
                tipo_nombre = tipo.get('tipo_nota')
                tipo_pct = tipo.get('porcentaje')
                
                # Si este tipo está en modo edición
                if st.session_state[f"editando_{curso}_{asignatura}"] == tipo_id:
                    col1, col2, col3 = st.columns([2, 2, 1])
                    with col1:
                        nuevo_nombre = st.text_input("Nombre", value=tipo_nombre, key=f"nombre_{tipo_id}", label_visibility="collapsed")
                    with col2:
                        nuevo_pct = st.number_input("%", min_value=0, max_value=100, value=tipo_pct, key=f"pct_{tipo_id}", label_visibility="collapsed")
                    with col3:
                        if st.button("💾", key=f"save_{tipo_id}"):
                            update_data = {"tipo_nota": nuevo_nombre, "porcentaje": nuevo_pct}
                            update_url = f"{SUPABASE_URL}/rest/v1/config_tipos_nota?id=eq.{tipo_id}"
                            response_upd = requests.patch(update_url, headers=headers, json=update_data)
                            if response_upd.status_code == 200:
                                st.session_state[f"editando_{curso}_{asignatura}"] = None
                                st.success("✅ Guardado")
                                st.rerun()
                            else:
                                st.error("Error")
                        if st.button("❌", key=f"cancel_{tipo_id}"):
                            st.session_state[f"editando_{curso}_{asignatura}"] = None
                            st.rerun()
                else:
                    # Vista normal con iconos
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    with col1:
                        st.write(tipo_nombre)
                    with col2:
                        st.write(f"{tipo_pct}%")
                    with col3:
                        if st.button("✏️", key=f"edit_{tipo_id}", help="Editar"):
                            st.session_state[f"editando_{curso}_{asignatura}"] = tipo_id
                            st.rerun()
                    with col4:
                        if st.button("🗑️", key=f"del_{tipo_id}", help="Eliminar"):
                            delete_url = f"{SUPABASE_URL}/rest/v1/config_tipos_nota?id=eq.{tipo_id}"
                            response_del = requests.delete(delete_url, headers=headers)
                            if response_del.status_code == 204:
                                st.success(f"✅ Eliminado")
                                st.rerun()
                            else:
                                st.error("Error")
            
            # Total
            st.divider()
            total = sum(t.get('porcentaje', 0) for t in tipos)
            if total == 100:
                st.success(f"✅ Total: {total}%")
            else:
                st.warning(f"⚠️ Total: {total}% (debe ser 100%)")
        else:
            st.info("No hay tipos de nota configurados")
    else:
        st.error("Error al cargar datos")


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
        st.warning("No hay tipos de nota configurados. Ve a 'Configurar Notas' primero.")
        if st.button("Ir a Configurar Notas"):
            st.session_state.menu_docente = "⚙️ Configurar Notas"
            st.rerun()
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
    
    st.info(f"**{asignatura} - {periodo}**")
    df_tipos = pd.DataFrame(tipos_nota)
    st.dataframe(df_tipos[['tipo_nota', 'porcentaje']], use_container_width=True)
    
    st.divider()
    
    notas_existentes = {}
    url_notas = f"{SUPABASE_URL}/rest/v1/notas?curso=eq.{curso}&asignatura=eq.{asignatura}&periodo=eq.{periodo_num}"
    response_notas = requests.get(url_notas, headers=headers)
    
    if response_notas.status_code == 200:
        for n in response_notas.json():
            key = f"{n.get('documento_estudiante')}_{n.get('tipo_nota')}"
            notas_existentes[key] = n.get('nota', 0)
    
    datos_notas = {}
    
    for estudiante in estudiantes:
        doc = estudiante.get('documento_estudiante')
        nombre = estudiante.get('nombre_estudiante')
        datos_notas[doc] = {"nombre": nombre}
        
        st.write(f"**{nombre}**")
        
        cols = st.columns(len(tipos_nota))
        for idx, tipo in enumerate(tipos_nota):
            tipo_nombre = tipo.get('tipo_nota')
            key = f"{doc}_{tipo_nombre}"
            valor_existente = notas_existentes.get(key, 0.0)
            
            with cols[idx]:
                nota = st.number_input(
                    f"{tipo_nombre}",
                    min_value=0.0,
                    max_value=5.0,
                    step=0.1,
                    value=float(valor_existente),
                    key=f"nota_{doc}_{tipo_nombre}",
                    label_visibility="collapsed"
                )
                datos_notas[doc][tipo_nombre] = nota
        st.divider()
    
    st.write("**Resumen**")
    
    resumen = []
    for doc, datos in datos_notas.items():
        suma_ponderada = 0
        for tipo in tipos_nota:
            tipo_nombre = tipo.get('tipo_nota')
            porcentaje = tipo.get('porcentaje', 0) / 100
            nota = datos.get(tipo_nombre, 0)
            suma_ponderada += nota * porcentaje
        
        resumen.append({
            "Estudiante": datos["nombre"],
            "Definitiva": round(suma_ponderada, 1)
        })
    
    df_resumen = pd.DataFrame(resumen)
    st.dataframe(df_resumen, use_container_width=True)
    
    if st.button("Guardar Calificaciones", type="primary", use_container_width=True):
        with st.spinner("Guardando..."):
            exitos = 0
            
            for doc, datos in datos_notas.items():
                for tipo in tipos_nota:
                    tipo_nombre = tipo.get('tipo_nota')
                    nota = datos.get(tipo_nombre, 0)
                    
                    check_url = f"{SUPABASE_URL}/rest/v1/notas?documento_estudiante=eq.{doc}&curso=eq.{curso}&asignatura=eq.{asignatura}&periodo=eq.{periodo_num}&tipo_nota=eq.{tipo_nombre}"
                    check_response = requests.get(check_url, headers=headers)
                    
                    data_nota = {
                        "documento_estudiante": doc,
                        "curso": curso,
                        "asignatura": asignatura,
                        "periodo": periodo_num,
                        "tipo_nota": tipo_nombre,
                        "nota": nota,
                        "documento_docente": documento_docente
                    }
                    
                    if check_response.status_code == 200 and check_response.json():
                        id_nota = check_response.json()[0].get('id')
                        update_url = f"{SUPABASE_URL}/rest/v1/notas?id=eq.{id_nota}"
                        requests.patch(update_url, headers=headers, json={"nota": nota})
                    else:
                        requests.post(f"{SUPABASE_URL}/rest/v1/notas", headers=headers, json=data_nota)
                    
                    exitos += 1
            
            st.success(f"✅ {exitos} notas guardadas")
            st.balloons()


# ============================================
# CONSULTA DE NOTAS
# ============================================

def mostrar_consulta_notas_estudiante(data):
    st.subheader("📖 Mis Calificaciones")
    
    documento = data.get('documento')
    headers = get_headers()
    
    url = f"{SUPABASE_URL}/rest/v1/notas?documento_estudiante=eq.{documento}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        notas = response.json()
        if notas:
            df = pd.DataFrame(notas)
            st.dataframe(df[['asignatura', 'periodo', 'tipo_nota', 'nota']], use_container_width=True)
        else:
            st.info("No hay calificaciones")
    else:
        st.error("Error al cargar")


# ============================================
# REPORTE DE NOTAS
# ============================================

def mostrar_reporte_notas(data):
    st.subheader("📊 Reporte de Calificaciones")
    st.info("Módulo en desarrollo")
