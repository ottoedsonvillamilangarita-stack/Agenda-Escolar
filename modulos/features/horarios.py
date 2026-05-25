import streamlit as st
import requests
import pandas as pd
from datetime import datetime, time
from utils import SUPABASE_URL, get_headers

# ============================================
# FUNCIONES AUXILIARES
# ============================================

def parse_hora(hora_str):
    """Convierte string de hora a objeto time"""
    if isinstance(hora_str, time):
        return hora_str
    if isinstance(hora_str, str):
        partes = hora_str.split(':')
        if len(partes) >= 2:
            return time(int(partes[0]), int(partes[1]))
    return time(7, 0)


# ============================================
# ADMIN - CONFIGURACIÓN
# ============================================

def configurar_niveles(headers):
    st.subheader("📚 Niveles Educativos")
    
    response = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    
    if response.status_code == 200:
        niveles = response.json()
        if niveles:
            st.write("**Niveles existentes:**")
            for n in niveles:
                st.write(f"- {n['nombre']}")
    
    with st.expander("➕ Agregar nivel"):
        nuevo_nivel = st.text_input("Nombre del nivel")
        if st.button("Agregar nivel"):
            if nuevo_nivel:
                data = {"nombre": nuevo_nivel, "orden": len(niveles) + 1 if niveles else 1}
                r = requests.post(f"{SUPABASE_URL}/rest/v1/niveles", headers=headers, json=data)
                if r.status_code == 201:
                    st.success(f"✅ Nivel '{nuevo_nivel}' agregado")
                    st.rerun()


def configurar_horas_nivel(headers):
    st.subheader("⏰ Configurar Horas por Nivel")
    st.info("Define las franjas horarias (horas de clase) para cada nivel. Serán las mismas para todos los cursos de ese nivel.")
    
    response_niveles = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    
    if response_niveles.status_code != 200:
        st.error("Error al cargar niveles")
        return
    
    niveles = response_niveles.json()
    
    if not niveles:
        st.warning("No hay niveles configurados")
        return
    
    nivel_nombres = [n['nombre'] for n in niveles]
    nivel_seleccionado = st.selectbox("Seleccionar nivel", nivel_nombres)
    nivel_id = next(n['id'] for n in niveles if n['nombre'] == nivel_seleccionado)
    
    # Obtener horas actuales del nivel
    url_horas = f"{SUPABASE_URL}/rest/v1/horas_nivel?nivel_id=eq.{nivel_id}&order=orden.asc"
    response_horas = requests.get(url_horas, headers=headers)
    horas = response_horas.json() if response_horas.status_code == 200 else []
    
    st.write(f"**Horas configuradas para {nivel_seleccionado}:**")
    
    if horas:
        df = pd.DataFrame(horas)
        df['hora_inicio'] = pd.to_datetime(df['hora_inicio']).dt.strftime('%H:%M')
        df['hora_fin'] = pd.to_datetime(df['hora_fin']).dt.strftime('%H:%M')
        st.dataframe(df[['orden', 'hora_inicio', 'hora_fin', 'descripcion']], use_container_width=True)
    
    st.divider()
    
    # Agregar nueva hora
    with st.expander("➕ Agregar hora de clase"):
        col1, col2, col3, col4 = st.columns([1, 2, 2, 2])
        with col1:
            orden = st.number_input("Orden", min_value=1, max_value=20, value=len(horas) + 1, step=1)
        with col2:
            hora_inicio = st.time_input("Hora inicio", value=time(7, 0))
        with col3:
            hora_fin = st.time_input("Hora fin", value=time(7, 50))
        with col4:
            descripcion = st.text_input("Descripción", placeholder="Ej: Primera hora")
        
        if st.button("➕ Agregar hora"):
            data_insert = {
                "nivel_id": nivel_id,
                "orden": orden,
                "hora_inicio": str(hora_inicio),
                "hora_fin": str(hora_fin),
                "descripcion": descripcion
            }
            r = requests.post(f"{SUPABASE_URL}/rest/v1/horas_nivel", headers=headers, json=data_insert)
            if r.status_code == 201:
                st.success("✅ Hora agregada")
                st.rerun()
    
    # Eliminar horas
    if horas:
        st.divider()
        st.write("**🗑️ Eliminar hora de clase:**")
        
        for hora in horas:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"Hora {hora['orden']}: {str(hora['hora_inicio'])[:5]} - {str(hora['hora_fin'])[:5]}")
            with col2:
                if st.button("Eliminar", key=f"del_hora_{hora['id']}"):
                    requests.delete(f"{SUPABASE_URL}/rest/v1/horas_nivel?id=eq.{hora['id']}", headers=headers)
                    st.rerun()


def configurar_horario_curso(headers):
    st.subheader("📅 Asignar Materias por Curso")
    st.info("Primero configura las horas del nivel, luego asigna las materias en cada franja horaria.")
    
    cursos = ["901", "902", "903", "1001", "1002", "1003", "1101"]
    
    response_niveles = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    niveles = response_niveles.json() if response_niveles.status_code == 200 else []
    
    if not niveles:
        st.warning("No hay niveles configurados")
        return
    
    curso = st.selectbox("Curso", cursos)
    nivel_curso = st.selectbox("Nivel del curso", [n['nombre'] for n in niveles], key="nivel_curso")
    nivel_id = next(n['id'] for n in niveles if n['nombre'] == nivel_curso)
    
    # Obtener horas del nivel
    url_horas = f"{SUPABASE_URL}/rest/v1/horas_nivel?nivel_id=eq.{nivel_id}&order=orden.asc"
    response_horas = requests.get(url_horas, headers=headers)
    horas = response_horas.json() if response_horas.status_code == 200 else []
    
    if not horas:
        st.warning(f"No hay horas configuradas para el nivel {nivel_curso}. Ve a 'Configurar Horas por Nivel' primero.")
        return
    
    # Obtener horario actual del curso
    url_horario = f"{SUPABASE_URL}/rest/v1/horario_base?curso=eq.{curso}&order=dia_semana.asc,orden_clase.asc"
    response_horario = requests.get(url_horario, headers=headers)
    horarios = response_horario.json() if response_horario.status_code == 200 else []
    
    # Obtener docentes
    response_docentes = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
    docentes = response_docentes.json() if response_docentes.status_code == 200 else []
    docentes_dict = {d['documento_docente']: f"{d['nombre_docente']} {d['apellidos_docente']}" for d in docentes}
    
    # Días
    dias = {1: "Lunes", 2: "Martes", 3: "Miérças", 4: "Jueves", 5: "Viernes", 6: "Sábado"}
    
    # Crear matriz de horario
    st.write(f"**Asignación de materias para curso {curso} - Nivel {nivel_curso}**")
    st.info(f"Horas del nivel: {len(horas)} clases por día")
    
    # Mostrar tabla de asignación
    for hora in horas:
        st.write(f"**Hora {hora['orden']}: {str(hora['hora_inicio'])[:5]} - {str(hora['hora_fin'])[:5]}**")
        
        cols = st.columns(len(dias))
        for idx, (dia_num, dia_nombre) in enumerate(dias.items()):
            with cols[idx]:
                st.write(f"📅 {dia_nombre}")
                
                # Buscar si ya existe asignación
                existente = next((h for h in horarios if h['dia_semana'] == dia_num and h['orden_clase'] == hora['orden']), None)
                
                asignatura = st.text_input("Asignatura", value=existente.get('asignatura', '') if existente else '',
                                          key=f"asig_{curso}_{dia_num}_{hora['orden']}")
                
                docente = st.selectbox("Docente", options=[""] + list(docentes_dict.keys()),
                                      format_func=lambda x: docentes_dict.get(x, "Seleccionar") if x else "Ninguno",
                                      key=f"doc_{curso}_{dia_num}_{hora['orden']}")
                
                salon = st.text_input("Salón", value=existente.get('salon', '') if existente else '',
                                     key=f"salon_{curso}_{dia_num}_{hora['orden']}")
                
                if asignatura:
                    data_horario = {
                        "curso": curso,
                        "nivel_id": nivel_id,
                        "dia_semana": dia_num,
                        "orden_clase": hora['orden'],
                        "hora_inicio": str(hora['hora_inicio']),
                        "hora_fin": str(hora['hora_fin']),
                        "asignatura": asignatura,
                        "documento_docente": docente if docente else None,
                        "salon": salon
                    }
                    
                    if existente:
                        requests.patch(f"{SUPABASE_URL}/rest/v1/horario_base?id=eq.{existente['id']}", 
                                      headers=headers, json=data_horario)
                    else:
                        requests.post(f"{SUPABASE_URL}/rest/v1/horario_base", headers=headers, json=data_horario)
                elif existente:
                    # Si no hay asignatura pero existía, eliminar
                    requests.delete(f"{SUPABASE_URL}/rest/v1/horario_base?id=eq.{existente['id']}", headers=headers)
        
        st.divider()
    
    if st.button("💾 Guardar todas las asignaciones", type="primary"):
        st.success("✅ Horario guardado")
        st.rerun()


def configurar_jornada_nivel(headers):
    st.subheader("📅 Configurar Días Laborales por Nivel")
    
    response_niveles = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    
    if response_niveles.status_code != 200:
        st.error("Error al cargar niveles")
        return
    
    niveles = response_niveles.json()
    
    if not niveles:
        st.warning("No hay niveles configurados")
        return
    
    nivel_nombres = [n['nombre'] for n in niveles]
    nivel_seleccionado = st.selectbox("Seleccionar nivel", nivel_nombres)
    nivel_id = next(n['id'] for n in niveles if n['nombre'] == nivel_seleccionado)
    
    url_config = f"{SUPABASE_URL}/rest/v1/config_horario_nivel?nivel_id=eq.{nivel_id}"
    response_config = requests.get(url_config, headers=headers)
    
    if response_config.status_code == 200 and response_config.json():
        config = response_config.json()[0]
        dias_laborales_default = config.get('dias_laborales', [1,2,3,4,5])
        horario_rotativo_default = config.get('horario_rotativo', False)
    else:
        dias_laborales_default = [1,2,3,4,5]
        horario_rotativo_default = False
    
    dias_opciones = {1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves", 5: "Viernes", 6: "Sábado"}
    
    dias_seleccionados = st.multiselect(
        "Días de clase",
        options=list(dias_opciones.keys()),
        format_func=lambda x: dias_opciones[x],
        default=dias_laborales_default
    )
    
    horario_rotativo = st.checkbox("Horario rotativo", value=horario_rotativo_default)
    
    if st.button("💾 Guardar configuración", type="primary"):
        data_config = {
            "nivel_id": nivel_id,
            "dias_laborales": dias_seleccionados,
            "horario_rotativo": horario_rotativo
        }
        
        if response_config.status_code == 200 and response_config.json():
            config_id = response_config.json()[0]['id']
            requests.patch(f"{SUPABASE_URL}/rest/v1/config_horario_nivel?id=eq.{config_id}", 
                          headers=headers, json=data_config)
        else:
            requests.post(f"{SUPABASE_URL}/rest/v1/config_horario_nivel", headers=headers, json=data_config)
        
        st.success("✅ Configuración guardada")
        st.rerun()


def gestion_festivos(headers):
    st.subheader("📆 Festivos")
    
    year = st.selectbox("Año", [2024, 2025, 2026])
    
    url_festivos = f"{SUPABASE_URL}/rest/v1/festivos?year=eq.{year}&order=fecha.asc"
    response_festivos = requests.get(url_festivos, headers=headers)
    
    if response_festivos.status_code == 200:
        festivos = response_festivos.json()
        if festivos:
            st.write("**Festivos registrados:**")
            for f in festivos:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"{f['fecha']} - {f.get('descripcion', 'Sin descripción')}")
                with col2:
                    if st.button("🗑️", key=f"del_{f['id']}"):
                        requests.delete(f"{SUPABASE_URL}/rest/v1/festivos?id=eq.{f['id']}", headers=headers)
                        st.rerun()
    
    with st.expander("➕ Agregar festivo"):
        col1, col2 = st.columns(2)
        with col1:
            fecha = st.date_input("Fecha")
        with col2:
            descripcion = st.text_input("Descripción")
        
        if st.button("Agregar"):
            data = {"fecha": str(fecha), "descripcion": descripcion, "year": fecha.year}
            requests.post(f"{SUPABASE_URL}/rest/v1/festivos", headers=headers, json=data)
            st.success("✅ Festivo agregado")
            st.rerun()


def gestion_horarios_admin(data):
    st.title("📅 Configuración de Horarios")
    
    headers = get_headers()
    
    tabs = st.tabs(["📚 Niveles", "⏰ Horas por Nivel", "📅 Días Laborales", "📖 Asignar Materias", "📆 Festivos"])
    
    with tabs[0]:
        configurar_niveles(headers)
    with tabs[1]:
        configurar_horas_nivel(headers)
    with tabs[2]:
        configurar_jornada_nivel(headers)
    with tabs[3]:
        configurar_horario_curso(headers)
    with tabs[4]:
        gestion_festivos(headers)


# ============================================
# VISUALIZACIÓN DE HORARIO - PARA TODOS LOS PERFILES
# ============================================

def mostrar_horario_tabla(curso, headers):
    """Muestra el horario de un curso en formato tabla"""
    
    # Obtener horario del curso
    url_horario = f"{SUPABASE_URL}/rest/v1/horario_base?curso=eq.{curso}&order=dia_semana.asc,orden_clase.asc"
    response_horario = requests.get(url_horario, headers=headers)
    
    if response_horario.status_code != 200:
        st.info("No hay horario configurado")
        return
    
    horarios = response_horario.json()
    
    if not horarios:
        st.info("No hay horario configurado para este curso")
        return
    
    # Días
    dias = {1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves", 5: "Viernes", 6: "Sábado"}
    
    # Organizar por día
    horario_por_dia = {}
    for dia in dias.values():
        horario_por_dia[dia] = []
    
    for clase in horarios:
        dia = dias.get(clase.get('dia_semana'), "Lunes")
        horario_por_dia[dia].append({
            "hora_inicio": clase.get('hora_inicio', '')[:5] if clase.get('hora_inicio') else '',
            "hora_fin": clase.get('hora_fin', '')[:5] if clase.get('hora_fin') else '',
            "asignatura": clase.get('asignatura', '?'),
            "salon": clase.get('salon', 'N/A')
        })
    
    # Crear tabla
    st.markdown("---")
    
    # Encabezados
    cols = st.columns(len(dias))
    for idx, dia in enumerate(dias.values()):
        with cols[idx]:
            st.markdown(f"**{dia}**")
    
    # Encontrar el número máximo de clases por día
    max_clases = max([len(horario_por_dia[dia]) for dia in dias.values()]) if horarios else 0
    
    # Mostrar filas
    for fila in range(max_clases):
        cols = st.columns(len(dias))
        for idx, dia in enumerate(dias.values()):
            with cols[idx]:
                if fila < len(horario_por_dia[dia]):
                    clase = horario_por_dia[dia][fila]
                    st.write(f"**{clase['hora_inicio']} - {clase['hora_fin']}**")
                    st.write(clase['asignatura'])
                    st.caption(f"📌 {clase['salon']}")
                else:
                    st.write("")
                    st.write("")
                    st.write("")
    
    st.markdown("---")


def mostrar_horario_docente_tabla(documento_docente, headers):
    """Muestra el horario personal del docente en formato tabla"""
    
    # Obtener horario del docente directamente
    url_horario = f"{SUPABASE_URL}/rest/v1/horario_base?documento_docente=eq.{documento_docente}&order=dia_semana.asc,hora_inicio.asc"
    response_horario = requests.get(url_horario, headers=headers)
    
    if response_horario.status_code != 200:
        st.info("No hay horario asignado")
        return
    
    horarios = response_horario.json()
    
    if not horarios:
        st.info("No hay horario asignado para este docente")
        return
    
    # Días
    dias = {1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves", 5: "Viernes", 6: "Sábado"}
    
    # Organizar por día
    horario_por_dia = {}
    for dia in dias.values():
        horario_por_dia[dia] = []
    
    for clase in horarios:
        dia = dias.get(clase.get('dia_semana'), "Lunes")
        horario_por_dia[dia].append({
            "hora_inicio": clase.get('hora_inicio', '')[:5] if clase.get('hora_inicio') else '',
            "hora_fin": clase.get('hora_fin', '')[:5] if clase.get('hora_fin') else '',
            "asignatura": clase.get('asignatura', '?'),
            "curso": clase.get('curso'),
            "salon": clase.get('salon', 'N/A')
        })
    
    # Crear tabla
    st.markdown("---")
    
    # Encabezados
    cols = st.columns(len(dias))
    for idx, dia in enumerate(dias.values()):
        with cols[idx]:
            st.markdown(f"**{dia}**")
    
    # Encontrar el número máximo de clases por día
    max_clases = max([len(horario_por_dia[dia]) for dia in dias.values()]) if horarios else 0
    
    # Mostrar filas
    for fila in range(max_clases):
        cols = st.columns(len(dias))
        for idx, dia in enumerate(dias.values()):
            with cols[idx]:
                if fila < len(horario_por_dia[dia]):
                    clase = horario_por_dia[dia][fila]
                    st.write(f"**{clase['hora_inicio']} - {clase['hora_fin']}**")
                    st.write(f"{clase['asignatura']} ({clase['curso']})")
                    st.caption(f"📌 {clase['salon']}")
                else:
                    st.write("")
                    st.write("")
                    st.write("")
    
    st.markdown("---")
