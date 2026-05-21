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
    # AGREGAR (expandible)
    # ============================================
    with st.expander("➕ Agregar tipo de nota", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            nuevo_tipo = st.text_input("Nombre", placeholder="Ej: Taller, Quiz, Examen")
        with col2:
            nuevo_porcentaje = st.number_input("Porcentaje (%)", min_value=0, max_value=100, value=20, step=5)
        
        if st.button("Agregar", type="primary"):
            if nuevo_tipo:
                data_insert = {
                    "curso": curso,
                    "asignatura": asignatura,
                    "tipo_nota": nuevo_tipo,
                    "porcentaje": nuevo_porcentaje,
                    "orden": 1,
                    "documento_docente": documento_docente
                }
                response_insert = requests.post(f"{SUPABASE_URL}/rest/v1/config_tipos_nota", headers=headers, json=data_insert)
                if response_insert.status_code == 201:
                    st.success(f"✅ Agregado")
                    st.rerun()
    
    st.divider()
    
    # ============================================
    # TABLA PRINCIPAL
    # ============================================
    url_config = f"{SUPABASE_URL}/rest/v1/config_tipos_nota?curso=eq.{curso}&asignatura=eq.{asignatura}&order=orden.asc"
    response_config = requests.get(url_config, headers=headers)
    
    if response_config.status_code == 200:
        tipos = response_config.json()
        
        if tipos:
            # Convertir a DataFrame
            df = pd.DataFrame(tipos)
            
            # Mostrar tabla con formato simple
            st.table(df[['tipo_nota', 'porcentaje']].rename(columns={'tipo_nota': 'Tipo de nota', 'porcentaje': '%'}))
            
            # Total
            total = df['porcentaje'].sum()
            if total == 100:
                st.success(f"✅ Total: {total}%")
            else:
                st.warning(f"⚠️ Total: {total}% (debe ser 100%)")
            
            st.divider()
            
            # ============================================
            # EDITAR (selector simple)
            # ============================================
            st.write("**✏️ Editar tipo de nota**")
            
            opciones_edit = [f"{row['tipo_nota']} ({row['porcentaje']}%)" for _, row in df.iterrows()]
            seleccion_edit = st.selectbox("Seleccionar", opciones_edit, key="editar_select")
            
            idx_seleccionado = opciones_edit.index(seleccion_edit)
            tipo_seleccionado = tipos[idx_seleccionado]
            
            col1, col2 = st.columns(2)
            with col1:
                nuevo_nombre = st.text_input("Nuevo nombre", value=tipo_seleccionado['tipo_nota'], key="edit_nombre")
            with col2:
                nuevo_pct = st.number_input("Nuevo %", min_value=0, max_value=100, value=tipo_seleccionado['porcentaje'], key="edit_pct")
            
            if st.button("💾 Guardar cambios"):
                update_data = {"tipo_nota": nuevo_nombre, "porcentaje": nuevo_pct}
                update_url = f"{SUPABASE_URL}/rest/v1/config_tipos_nota?id=eq.{tipo_seleccionado['id']}"
                requests.patch(update_url, headers=headers, json=update_data)
                st.success("✅ Guardado")
                st.rerun()
            
            st.divider()
            
            # ============================================
            # ELIMINAR
            # ============================================
            st.write("**🗑️ Eliminar tipo de nota**")
            
            opciones_del = [f"{row['tipo_nota']} ({row['porcentaje']}%)" for _, row in df.iterrows()]
            seleccion_del = st.selectbox("Seleccionar", opciones_del, key="eliminar_select")
            
            idx_eliminar = opciones_del.index(seleccion_del)
            tipo_eliminar = tipos[idx_eliminar]
            
            if st.button("Eliminar", type="primary"):
                delete_url = f"{SUPABASE_URL}/rest/v1/config_tipos_nota?id=eq.{tipo_eliminar['id']}"
                requests.delete(delete_url, headers=headers)
                st.success("✅ Eliminado")
                st.rerun()
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
    
    # Mostrar tipos de nota
    df_tipos = pd.DataFrame(tipos_nota)
    st.dataframe(df_tipos[['tipo_nota', 'porcentaje']], use_container_width=True)
    
    st.divider()
    
    # Obtener notas existentes
    notas_existentes = {}
    url_notas = f"{SUPABASE_URL}/rest/v1/notas?curso=eq.{curso}&asignatura=eq.{asignatura}&periodo=eq.{periodo_num}"
    response_notas = requests.get(url_notas, headers=headers)
    
    if response_notas.status_code == 200:
        for n in response_notas.json():
            key = f"{n.get('documento_estudiante')}_{n.get('tipo_nota')}"
            notas_existentes[key] = n.get('nota', 0)
    
    # Tabla de notas
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
                    tipo_nombre,
                    min_value=0.0,
                    max_value=5.0,
                    step=0.1,
                    value=float(valor_existente),
                    key=f"nota_{doc}_{tipo_nombre}",
                    label_visibility="collapsed"
                )
                datos_notas[doc][tipo_nombre] = nota
        st.divider()
    
    # Resumen
    st.write("**Resumen**")
    
    resumen = []
    for doc, datos in datos_notas.items():
        suma = 0
        for tipo in tipos_nota:
            tipo_nombre = tipo.get('tipo_nota')
            porcentaje = tipo.get('porcentaje', 0) / 100
            nota = datos.get(tipo_nombre, 0)
            suma += nota * porcentaje
        
        resumen.append({
            "Estudiante": datos["nombre"],
            "Definitiva": round(suma, 1)
        })
    
    st.dataframe(pd.DataFrame(resumen), use_container_width=True)
    
    if st.button("💾 Guardar", type="primary", use_container_width=True):
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
        
        st.success("✅ Notas guardadas")
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
            st.table(df[['asignatura', 'periodo', 'tipo_nota', 'nota']].rename(columns={
                'asignatura': 'Asignatura', 'periodo': 'Período', 'tipo_nota': 'Tipo', 'nota': 'Nota'
            }))
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
