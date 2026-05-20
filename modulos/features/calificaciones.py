import streamlit as st
import requests
import pandas as pd
from utils import SUPABASE_URL, get_headers

# ============================================
# CONFIGURACIÓN DE TIPOS DE NOTA
# ============================================

def mostrar_configuracion_notas(data):
    """Docente configura tipos de nota para cada materia"""
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
    
    # Seleccionar materia
    opciones = [f"{m.get('curso')} - {m.get('asignatura')}" for m in materias]
    seleccion = st.selectbox("Seleccionar materia", opciones, key="config_materia")
    curso = seleccion.split(" - ")[0]
    asignatura = seleccion.split(" - ")[1]
    
    st.write(f"**Configurando: {curso} - {asignatura}**")
    
    # Ver configuración existente
    url_config = f"{SUPABASE_URL}/rest/v1/config_tipos_nota?curso=eq.{curso}&asignatura=eq.{asignatura}&order=orden.asc"
    response_config = requests.get(url_config, headers=headers)
    
    tipos_existentes = []
    if response_config.status_code == 200:
        tipos_existentes = response_config.json()
    
    # Mostrar configuración actual
    if tipos_existentes:
        st.write("**Configuración actual:**")
        df = pd.DataFrame(tipos_existentes)
        st.dataframe(df[['tipo_nota', 'porcentaje', 'orden']], use_container_width=True)
    
    st.divider()
    
    # Agregar nuevo tipo de nota
    st.write("**Agregar nuevo tipo de nota:**")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        nuevo_tipo = st.text_input("Nombre (Ej: Taller, Quiz, Examen)")
    with col2:
        nuevo_porcentaje = st.number_input("Porcentaje (%)", min_value=0, max_value=100, value=20)
    with col3:
        nuevo_orden = st.number_input("Orden", min_value=1, max_value=20, value=len(tipos_existentes)+1)
    
    if st.button("➕ Agregar Tipo de Nota", type="primary"):
        if not nuevo_tipo:
            st.error("❌ Ingresa un nombre para el tipo de nota")
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
                st.success(f"✅ Tipo de nota '{nuevo_tipo}' agregado")
                st.rerun()
            else:
                st.error(f"Error: {response.status_code}")
    
    # Eliminar tipos de nota
    if tipos_existentes:
        st.divider()
        st.write("**Eliminar tipo de nota:**")
        
        for tipo in tipos_existentes:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"{tipo.get('tipo_nota')} ({tipo.get('porcentaje')}%)")
            with col2:
                if st.button("🗑️", key=f"del_{tipo.get('id')}"):
                    delete_url = f"{SUPABASE_URL}/rest/v1/config_tipos_nota?id=eq.{tipo.get('id')}"
                    response = requests.delete(delete_url, headers=headers)
                    if response.status_code == 204:
                        st.success(f"✅ Tipo '{tipo.get('tipo_nota')}' eliminado")
                        st.rerun()


# ============================================
# INGRESO DE NOTAS
# ============================================

def mostrar_ingreso_notas(data):
    """Docente ingresa notas según configuración"""
    st.subheader("📝 Ingreso de Calificaciones")
    
    documento_docente = data.get('documento')
    headers = get_headers()
    
    # 1. Seleccionar materia
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
    
    # 2. Seleccionar período
    periodos = ["Período 1", "Período 2", "Período 3", "Período 4"]
    periodo = st.selectbox("Período", periodos)
    periodo_num = int(periodo.split()[1])
    
    # 3. Obtener configuración de tipos de nota
    url_config = f"{SUPABASE_URL}/rest/v1/config_tipos_nota?curso=eq.{curso}&asignatura=eq.{asignatura}&order=orden.asc"
    response_config = requests.get(url_config, headers=headers)
    
    tipos_nota = []
    if response_config.status_code == 200:
        tipos_nota = response_config.json()
    
    if not tipos_nota:
        st.warning("⚠️ No hay tipos de nota configurados. Ve a 'Configurar Notas' primero.")
        if st.button("Ir a Configurar Notas", key="ir_configurar"):
    st.session_state.menu_docente = "⚙️ Configurar Notas"
    st.rerun()
        return
    
    # 4. Mostrar configuración actual
    st.info(f"**Configuración de notas para {asignatura} - {periodo}**")
    
    df_tipos = pd.DataFrame(tipos_nota)
    st.dataframe(df_tipos[['tipo_nota', 'porcentaje']], use_container_width=True)
    
    # Verificar que los porcentajes sumen 100%
    suma_porcentajes = sum(t.get('porcentaje', 0) for t in tipos_nota)
    if suma_porcentajes != 100:
        st.warning(f"⚠️ Los porcentajes suman {suma_porcentajes}%. Deben sumar 100%.")
    
    st.divider()
    
    # 5. Obtener estudiantes
    url_est = f"{SUPABASE_URL}/rest/v1/estudiantes?curso=eq.{curso}"
    response_est = requests.get(url_est, headers=headers)
    
    if response_est.status_code != 200:
        st.error("Error al cargar estudiantes")
        return
    
    estudiantes = response_est.json()
    if not estudiantes:
        st.warning(f"No hay estudiantes en el curso {curso}")
        return
    
    # 6. Obtener notas existentes
    notas_existentes = {}
    url_notas = f"{SUPABASE_URL}/rest/v1/notas?curso=eq.{curso}&asignatura=eq.{asignatura}&periodo=eq.{periodo_num}"
    response_notas = requests.get(url_notas, headers=headers)
    
    if response_notas.status_code == 200:
        for n in response_notas.json():
            key = f"{n.get('documento_estudiante')}_{n.get('tipo_nota')}"
            notas_existentes[key] = n.get('nota', 0)
    
    # 7. Tabla de notas por estudiante
    st.write(f"**Ingreso de notas - Curso {curso} - {asignatura}**")
    
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
    
    # 8. Calcular definitivas
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
    
    # 9. Guardar todas las notas
    if st.button("💾 Guardar todas las calificaciones", type="primary"):
        with st.spinner("Guardando calificaciones..."):
            exitos = 0
            errores = 0
            
            for doc, datos in datos_notas.items():
                for tipo in tipos_nota:
                    tipo_nombre = tipo.get('tipo_nota')
                    nota = datos.get(tipo_nombre, 0)
                    
                    # Verificar si ya existe
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
                        # Actualizar
                        id_nota = check_response.json()[0].get('id')
                        update_url = f"{SUPABASE_URL}/rest/v1/notas?id=eq.{id_nota}"
                        response = requests.patch(update_url, headers=headers, json={"nota": nota})
                    else:
                        # Insertar
                        response = requests.post(f"{SUPABASE_URL}/rest/v1/notas", headers=headers, json=data_nota)
                    
                    if response.status_code in [200, 201, 204]:
                        exitos += 1
                    else:
                        errores += 1
            
            if errores == 0:
                st.success(f"✅ {exitos} calificaciones guardadas exitosamente")
                st.balloons()
            else:
                st.warning(f"⚠️ {exitos} guardadas, {errores} errores")


# ============================================
# CONSULTA DE NOTAS (ESTUDIANTE/ACUDIENTE)
# ============================================

def mostrar_consulta_notas(data, rol="estudiante"):
    """Muestra notas para estudiantes o acudientes"""
    st.subheader("📖 Mis Calificaciones")
    
    headers = get_headers()
    
    if rol == "estudiante":
        documento = data.get('documento')
        url = f"{SUPABASE_URL}/rest/v1/notas?documento_estudiante=eq.{documento}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            notas = response.json()
            if notas:
                df = pd.DataFrame(notas)
                st.dataframe(df[['asignatura', 'periodo', 'tipo_nota', 'nota']], use_container_width=True)
                
                # Resumen por asignatura
                st.subheader("📊 Resumen por Asignatura")
                resumen = df.groupby('asignatura')['nota'].mean().reset_index()
                resumen.columns = ['Asignatura', 'Promedio']
                st.dataframe(resumen, use_container_width=True)
            else:
                st.info("No hay calificaciones registradas")
        else:
            st.error("Error al cargar notas")
    
    elif rol == "acudiente":
        documento_acudiente = data.get('documento')
        url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_acudiente=eq.{documento_acudiente}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            hijos = response.json()
            if hijos:
                for hijo in hijos:
                    doc_hijo = hijo.get('documento_estudiante')
                    nombre_hijo = hijo.get('nombre_estudiante')
                    
                    with st.expander(f"📘 {nombre_hijo}"):
                        url_notas = f"{SUPABASE_URL}/rest/v1/notas?documento_estudiante=eq.{doc_hijo}"
                        response_notas = requests.get(url_notas, headers=headers)
                        
                        if response_notas.status_code == 200:
                            notas = response_notas.json()
                            if notas:
                                df = pd.DataFrame(notas)
                                st.dataframe(df[['asignatura', 'periodo', 'tipo_nota', 'nota']], use_container_width=True)
                            else:
                                st.info("Sin calificaciones")
            else:
                st.info("No hay hijos asociados")


# ============================================
# REPORTE DE NOTAS
# ============================================

def mostrar_reporte_notas(data):
    """Genera reporte de notas para docentes"""
    st.subheader("📊 Reporte de Calificaciones")
    
    documento_docente = data.get('documento')
    headers = get_headers()
    
    # Obtener materias
    url = f"{SUPABASE_URL}/rest/v1/asignacion_academica?documento_docente=eq.{documento_docente}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        materias = response.json()
        if not materias:
            st.warning("No tienes materias asignadas")
            return
        
        opciones = [f"{m.get('curso')} - {m.get('asignatura')}" for m in materias]
        seleccion = st.selectbox("Seleccionar materia", opciones)
        curso = seleccion.split(" - ")[0]
        asignatura = seleccion.split(" - ")[1]
        
        periodo = st.selectbox("Período", ["Período 1", "Período 2", "Período 3", "Período 4"])
        periodo_num = int(periodo.split()[1])
        
        if st.button("📄 Generar Reporte", type="primary"):
            with st.spinner("Generando reporte..."):
                # Obtener estudiantes
                url_est = f"{SUPABASE_URL}/rest/v1/estudiantes?curso=eq.{curso}"
                response_est = requests.get(url_est, headers=headers)
                
                if response_est.status_code == 200:
                    estudiantes = response_est.json()
                    
                    # Obtener notas
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
                    
                    # Construir reporte
                    reporte = []
                    for est in estudiantes:
                        doc = est.get('documento_estudiante')
                        fila = {
                            "Estudiante": est.get('nombre_estudiante'),
                            "Documento": doc
                        }
                        # Agregar notas por tipo
                        for tipo in notas_dict.get(doc, {}):
                            fila[tipo] = notas_dict[doc][tipo]
                        reporte.append(fila)
                    
                    if reporte:
                        df_reporte = pd.DataFrame(reporte)
                        st.dataframe(df_reporte, use_container_width=True)
                        
                        # Descargar CSV
                        csv = df_reporte.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Descargar Reporte (CSV)",
                            data=csv,
                            file_name=f"reporte_{curso}_{asignatura}_{periodo_num}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.info("No hay datos para generar el reporte")
