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
    
    opciones = [f"{m.get('curso')} - {m.get('asignatura')}" for m in materias]
    seleccion = st.selectbox("📚 Seleccionar materia", opciones, key="config_materia")
    curso = seleccion.split(" - ")[0]
    asignatura = seleccion.split(" - ")[1]
    
    st.success(f"**Configurando: {curso} - {asignatura}**")
    
    # ============================================
    # AGREGAR NUEVO TIPO DE NOTA
    # ============================================
    with st.expander("➕ Agregar nuevo tipo de nota", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            nuevo_tipo = st.text_input("📝 Nombre", placeholder="Ej: Taller, Quiz, Examen")
        with col2:
            nuevo_porcentaje = st.number_input("📊 Porcentaje (%)", min_value=0, max_value=100, value=20, step=5)
        with col3:
            nuevo_orden = st.number_input("🔢 Orden", min_value=1, max_value=20, value=1, step=1)
        
        if st.button("➕ Agregar", type="primary", use_container_width=True):
            if not nuevo_tipo:
                st.error("❌ Ingresa un nombre")
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
                    st.success(f"✅ '{nuevo_tipo}' agregado")
                    st.rerun()
                else:
                    st.error(f"Error: {response.status_code}")
    
    st.divider()
    
    # ============================================
    # LISTA DE TIPOS DE NOTA
    # ============================================
    url_config = f"{SUPABASE_URL}/rest/v1/config_tipos_nota?curso=eq.{curso}&asignatura=eq.{asignatura}&order=orden.asc"
    response_config = requests.get(url_config, headers=headers)
    
    if response_config.status_code == 200:
        tipos = response_config.json()
        
        if tipos:
            st.write("**📋 Tipos de nota configurados:**")
            
            # Mostrar tabla resumen
            data_tabla = []
            for tipo in tipos:
                data_tabla.append({
                    "Tipo": tipo.get('tipo_nota'),
                    "Porcentaje": f"{tipo.get('porcentaje')}%",
                    "Orden": tipo.get('orden')
                })
            df = pd.DataFrame(data_tabla)
            st.dataframe(df, use_container_width=True)
            
            st.write("**🔧 Gestionar tipos de nota:**")
            
            for tipo in tipos:
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col1:
                    st.write(f"{tipo.get('tipo_nota')} ({tipo.get('porcentaje')}%)")
                with col2:
                    if st.button("✏️", key=f"edit_btn_{tipo.get('id')}"):
                        st.session_state[f"editando_{tipo.get('id')}"] = True
                with col3:
                    if st.button("🗑️", key=f"del_btn_{tipo.get('id')}"):
                        delete_url = f"{SUPABASE_URL}/rest/v1/config_tipos_nota?id=eq.{tipo.get('id')}"
                        response = requests.delete(delete_url, headers=headers)
                        if response.status_code == 204:
                            st.success(f"✅ Eliminado")
                            st.rerun()
                        else:
                            st.error("Error al eliminar")
                with col4:
                    st.write("")
                
                if st.session_state.get(f"editando_{tipo.get('id')}", False):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        nuevo_nombre = st.text_input("Nuevo nombre", value=tipo.get('tipo_nota'), key=f"nombre_{tipo.get('id')}")
                    with col_b:
                        nuevo_pct = st.number_input("Nuevo porcentaje", min_value=0, max_value=100, value=tipo.get('porcentaje', 0), key=f"pct_{tipo.get('id')}")
                    
                    col_x, col_y = st.columns(2)
                    with col_x:
                        if st.button("💾 Guardar", key=f"save_{tipo.get('id')}"):
                            update_data = {"tipo_nota": nuevo_nombre, "porcentaje": nuevo_pct}
                            update_url = f"{SUPABASE_URL}/rest/v1/config_tipos_nota?id=eq.{tipo.get('id')}"
                            response = requests.patch(update_url, headers=headers, json=update_data)
                            if response.status_code == 200:
                                st.success("✅ Guardado")
                                st.session_state[f"editando_{tipo.get('id')}"] = False
                                st.rerun()
                            else:
                                st.error(f"Error: {response.status_code}")
                    with col_y:
                        if st.button("❌ Cancelar", key=f"cancel_{tipo.get('id')}"):
                            st.session_state[f"editando_{tipo.get('id')}"] = False
                            st.rerun()
                    st.divider()
            
            total = sum(t.get('porcentaje', 0) for t in tipos)
            if total == 100:
                st.success(f"✅ Total porcentajes: {total}%")
            else:
                st.warning(f"⚠️ Total porcentajes: {total}% (debe ser 100%)")
        else:
            st.info("📌 No hay tipos de nota configurados para esta materia")
    else:
        st.error("Error al cargar la configuración")


# ============================================
# INGRESO DE NOTAS
# ============================================

def mostrar_ingreso_notas(data):
    st.subheader("📝 Ingreso de Calificaciones")
    
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
    
    opciones = [f"{m.get('curso')} - {m.get('asignatura')}" for m in materias]
    seleccion = st.selectbox("📚 Seleccionar materia", opciones, key="ingreso_materia")
    curso = seleccion.split(" - ")[0]
    asignatura = seleccion.split(" - ")[1]
    
    periodos = ["Período 1", "Período 2", "Período 3", "Período 4"]
    periodo = st.selectbox("📅 Período", periodos)
    periodo_num = int(periodo.split()[1])
    
    # Obtener configuración de tipos de nota
    url_config = f"{SUPABASE_URL}/rest/v1/config_tipos_nota?curso=eq.{curso}&asignatura=eq.{asignatura}&order=orden.asc"
    response_config = requests.get(url_config, headers=headers)
    
    tipos_nota = []
    if response_config.status_code == 200:
        tipos_nota = response_config.json()
    
    if not tipos_nota:
        st.warning("⚠️ No hay tipos de nota configurados. Ve a 'Configurar Notas' primero.")
        if st.button("Ir a Configurar Notas"):
            st.session_state.menu_docente = "⚙️ Configurar Notas"
            st.rerun()
        return
    
    # Obtener estudiantes
    url_est = f"{SUPABASE_URL}/rest/v1/estudiantes?curso=eq.{curso}"
    response_est = requests.get(url_est, headers=headers)
    
    if response_est.status_code != 200:
        st.error("Error al cargar estudiantes")
        return
    
    estudiantes = response_est.json()
    if not estudiantes:
        st.warning(f"No hay estudiantes en el curso {curso}")
        return
    
    # Mostrar configuración
    st.info(f"**{asignatura} - {periodo}**")
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
    
    # Tabla de notas por estudiante
    datos_notas = {}
    
    for estudiante in estudiantes:
        doc = estudiante.get('documento_estudiante')
        nombre = estudiante.get('nombre_estudiante')
        datos_notas[doc] = {"nombre": nombre}
        
        st.write(f"**📘 {nombre}**")
        
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
    
    # Calcular definitivas
    st.write("**📊 Resumen de calificaciones**")
    
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
    
    # Guardar notas
    if st.button("💾 Guardar Calificaciones", type="primary", use_container_width=True):
        with st.spinner("Guardando..."):
            exitos = 0
            errores = 0
            
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
                        response = requests.patch(update_url, headers=headers, json={"nota": nota})
                    else:
                        response = requests.post(f"{SUPABASE_URL}/rest/v1/notas", headers=headers, json=data_nota)
                    
                    if response.status_code in [200, 201, 204]:
                        exitos += 1
                    else:
                        errores += 1
            
            if errores == 0:
                st.success(f"✅ {exitos} calificaciones guardadas")
                st.balloons()
            else:
                st.warning(f"⚠️ {exitos} guardadas, {errores} errores")


# ============================================
# CONSULTA DE NOTAS (ESTUDIANTE)
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
            
            st.subheader("📊 Resumen por Asignatura")
            resumen = df.groupby('asignatura')['nota'].mean().reset_index()
            resumen.columns = ['Asignatura', 'Promedio']
            st.dataframe(resumen, use_container_width=True)
        else:
            st.info("No hay calificaciones registradas")
    else:
        st.error("Error al cargar notas")


# ============================================
# REPORTE DE NOTAS
# ============================================

def mostrar_reporte_notas(data):
    st.subheader("📊 Reporte de Calificaciones")
    
    documento_docente = data.get('documento')
    headers = get_headers()
    
    url = f"{SUPABASE_URL}/rest/v1/asignacion_academica?documento_docente=eq.{documento_docente}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        materias = response.json()
        if not materias:
            st.warning("No tienes materias asignadas")
            return
        
        opciones = [f"{m.get('curso')} - {m.get('asignatura')}" for m in materias if m.get('asignatura') != 'Dirección de Curso']
        if not opciones:
            st.warning("No hay materias para generar reportes")
            return
        
        seleccion = st.selectbox("📚 Seleccionar materia", opciones)
        curso = seleccion.split(" - ")[0]
        asignatura = seleccion.split(" - ")[1]
        
        periodo = st.selectbox("📅 Período", ["Período 1", "Período 2", "Período 3", "Período 4"])
        periodo_num = int(periodo.split()[1])
        
        if st.button("📄 Generar Reporte", type="primary"):
            with st.spinner("Generando..."):
                url_est = f"{SUPABASE_URL}/rest/v1/estudiantes?curso=eq.{curso}"
                response_est = requests.get(url_est, headers=headers)
                
                if response_est.status_code == 200:
                    estudiantes = response_est.json()
                    
                    url_notas = f"{SUPABASE_URL}/rest/v1/notas?curso=eq.{curso}&asignatura=eq.{asignatura}&periodo=eq.{periodo_num}"
                    response_notas = requests.get(url_notas, headers=headers)
                    
                    notas_dict = {}
                    if response_notas.status_code == 200:
                        for n in response_notas.json():
                            doc = n.get('documento_estudiante')
                            tipo = n.get('tipo_nota')
                            nota = n.get('nota', 0)
                            if doc not in notas_dict:
                                notas_dict[doc] = {}
                            notas_dict[doc][tipo] = nota
                    
                    reporte = []
                    for est in estudiantes:
                        doc = est.get('documento_estudiante')
                        fila = {
                            "Estudiante": est.get('nombre_estudiante'),
                            "Documento": doc
                        }
                        for tipo, nota in notas_dict.get(doc, {}).items():
                            fila[tipo] = nota
                        reporte.append(fila)
                    
                    if reporte:
                        df_reporte = pd.DataFrame(reporte)
                        st.dataframe(df_reporte, use_container_width=True)
                        
                        csv = df_reporte.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Descargar Reporte (CSV)",
                            data=csv,
                            file_name=f"reporte_{curso}_{asignatura}_{periodo_num}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.info("No hay datos para el reporte")
