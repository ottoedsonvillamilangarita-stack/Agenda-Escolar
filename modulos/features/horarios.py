import streamlit as st
import requests
import pandas as pd
from datetime import datetime, time
from utils import SUPABASE_URL, get_headers

# ============================================
# FUNCIONES AUXILIARES
# ============================================

def parse_hora(hora_str):
    """Convierte string de hora a objeto time, manejando diferentes formatos"""
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


def configurar_jornada_nivel(headers):
    st.subheader("⏰ Configurar Jornada por Nivel")
    
    response_niveles = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    
    if response_niveles.status_code != 200:
        st.error("Error al cargar niveles")
        return
    
    niveles = response_niveles.json()
    
    if not niveles:
        st.warning("No hay niveles configurados. Crea uno primero.")
        return
    
    nivel_nombres = [n['nombre'] for n in niveles]
    nivel_seleccionado = st.selectbox("Seleccionar nivel", nivel_nombres)
    nivel_id = next(n['id'] for n in niveles if n['nombre'] == nivel_seleccionado)
    
    url_config = f"{SUPABASE_URL}/rest/v1/config_horario_nivel?nivel_id=eq.{nivel_id}"
    response_config = requests.get(url_config, headers=headers)
    
    if response_config.status_code == 200 and response_config.json():
        config = response_config.json()[0]
        hora_inicio_default = parse_hora(config.get('hora_inicio_jornada', '07:00'))
    else:
        config = {
            "dias_laborales": [1,2,3,4,5],
            "num_clases_por_dia": 6,
            "duracion_clase_minutos": 50,
            "horario_rotativo": False
        }
        hora_inicio_default = time(7, 0)
    
    dias_opciones = {1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves", 5: "Viernes", 6: "Sábado"}
    
    dias_seleccionados = st.multiselect(
        "Días de clase",
        options=list(dias_opciones.keys()),
        format_func=lambda x: dias_opciones[x],
        default=config.get('dias_laborales', [1,2,3,4,5])
    )
    
    col1, col2, col3 = st.columns(3)
    with col1:
        num_clases = st.number_input("Clases por día", min_value=1, max_value=12, 
                                      value=config.get('num_clases_por_dia', 6))
    with col2:
        duracion_clase = st.number_input("Duración (minutos)", min_value=30, max_value=120, 
                                          value=config.get('duracion_clase_minutos', 50), step=5)
    with col3:
        hora_inicio = st.time_input("Hora inicio", value=hora_inicio_default)
    
    horario_rotativo = st.checkbox("Horario rotativo", value=config.get('horario_rotativo', False))
    
    if st.button("💾 Guardar configuración", type="primary"):
        data_config = {
            "nivel_id": nivel_id,
            "dias_laborales": dias_seleccionados,
            "num_clases_por_dia": num_clases,
            "duracion_clase_minutos": duracion_clase,
            "hora_inicio_jornada": str(hora_inicio),
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


def configurar_horario_curso(headers):
    st.subheader("📅 Configurar Horario por Curso")
    
    cursos = ["901", "902", "903", "1001", "1002", "1003", "1101"]
    
    response_niveles = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    niveles = response_niveles.json() if response_niveles.status_code == 200 else []
    
    if not niveles:
        st.warning("No hay niveles configurados")
        return
    
    curso = st.selectbox("Curso", cursos)
    nivel_curso = st.selectbox("Nivel", [n['nombre'] for n in niveles], key="nivel_curso")
    nivel_id = next(n['id'] for n in niveles if n['nombre'] == nivel_curso)
    
    url_config = f"{SUPABASE_URL}/rest/v1/config_horario_nivel?nivel_id=eq.{nivel_id}"
    response_config = requests.get(url_config, headers=headers)
    
    if response_config.status_code == 200 and response_config.json():
        config = response_config.json()[0]
        num_clases = config.get('num_clases_por_dia', 6)
        dias_laborales = config.get('dias_laborales', [1,2,3,4,5])
    else:
        st.warning("Primero configura la jornada para este nivel")
        return
    
    url_horario = f"{SUPABASE_URL}/rest/v1/horario_base?curso=eq.{curso}&order=dia_semana.asc,orden_clase.asc"
    response_horario = requests.get(url_horario, headers=headers)
    horarios = response_horario.json() if response_horario.status_code == 200 else []
    
    response_docentes = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
    docentes = response_docentes.json() if response_docentes.status_code == 200 else []
    docentes_dict = {d['documento_docente']: f"{d['nombre_docente']} {d['apellidos_docente']}" for d in docentes}
    
    dias = {1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves", 5: "Viernes", 6: "Sábado"}
    
    st.info(f"📌 {num_clases} clases por día")
    
    if horarios:
        st.write("**Horario actual:**")
        df = pd.DataFrame(horarios)
        df['dia'] = df['dia_semana'].map(dias)
        st.dataframe(df[['dia', 'orden_clase', 'asignatura', 'salon']], use_container_width=True)
    
    st.divider()
    st.write("**Configurar horario:**")
    
    for dia in dias_laborales:
        with st.expander(f"📅 {dias[dia]}"):
            for orden in range(1, num_clases + 1):
                existente = next((h for h in horarios if h['dia_semana'] == dia and h['orden_clase'] == orden), None)
                
                col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
                with col1:
                    st.write(f"**{orden}**")
                with col2:
                    asignatura = st.text_input("Asignatura", value=existente.get('asignatura', '') if existente else '',
                                               key=f"asig_{curso}_{dia}_{orden}")
                with col3:
                    docente_doc = st.selectbox("Docente", options=[""] + list(docentes_dict.keys()),
                                               format_func=lambda x: docentes_dict.get(x, "Seleccionar") if x else "Ninguno",
                                               key=f"doc_{curso}_{dia}_{orden}")
                with col4:
                    salon = st.text_input("Salón", value=existente.get('salon', '') if existente else '',
                                         key=f"salon_{curso}_{dia}_{orden}")
                
                if asignatura:
                    data_horario = {
                        "curso": curso,
                        "nivel_id": nivel_id,
                        "dia_semana": dia,
                        "orden_clase": orden,
                        "asignatura": asignatura,
                        "documento_docente": docente_doc if docente_doc else None,
                        "salon": salon
                    }
                    
                    if existente:
                        requests.patch(f"{SUPABASE_URL}/rest/v1/horario_base?id=eq.{existente['id']}", 
                                      headers=headers, json=data_horario)
                    else:
                        requests.post(f"{SUPABASE_URL}/rest/v1/horario_base", headers=headers, json=data_horario)
    
    if st.button("💾 Guardar horario", type="primary"):
        st.success("✅ Horario guardado")
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
    
    tabs = st.tabs(["📚 Niveles", "⏰ Jornada por Nivel", "📅 Horario por Curso", "📆 Festivos"])
    
    with tabs[0]:
        configurar_niveles(headers)
    with tabs[1]:
        configurar_jornada_nivel(headers)
    with tabs[2]:
        configurar_horario_curso(headers)
    with tabs[3]:
        gestion_festivos(headers)


# ============================================
# VISUALIZACIÓN DE HORARIO
# ============================================

def obtener_horario_semanal(curso, headers):
    """Obtiene el horario completo de la semana para un curso"""
    
    dias = {1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves", 5: "Viernes", 6: "Sábado"}
    
    url_nivel = f"{SUPABASE_URL}/rest/v1/horario_base?curso=eq.{curso}&select=nivel_id&limit=1"
    response_nivel = requests.get(url_nivel, headers=headers)
    
    if response_nivel.status_code != 200 or not response_nivel.json():
        return {}
    
    nivel_id = response_nivel.json()[0].get('nivel_id')
    
    url_config = f"{SUPABASE_URL}/rest/v1/config_horario_nivel?nivel_id=eq.{nivel_id}"
    response_config = requests.get(url_config, headers=headers)
    
    if response_config.status_code != 200 or not response_config.json():
        return {}
    
    config = response_config.json()[0]
    dias_laborales = config.get('dias_laborales', [1,2,3,4,5])
    hora_inicio = parse_hora(config.get('hora_inicio_jornada', '07:00'))
    duracion = config.get('duracion_clase_minutos', 50)
    
    url_horario = f"{SUPABASE_URL}/rest/v1/horario_base?curso=eq.{curso}&order=dia_semana.asc,orden_clase.asc"
    response_horario = requests.get(url_horario, headers=headers)
    
    if response_horario.status_code != 200:
        return {}
    
    horarios = response_horario.json()
    
    horario_semanal = {}
    hoy = datetime.now().date()
    
    for dia in dias_laborales:
        horario_semanal[dias[dia]] = []
        clases_dia = [h for h in horarios if h['dia_semana'] == dia]
        clases_dia.sort(key=lambda x: x.get('orden_clase', 0))
        
        for clase in clases_dia:
            orden = clase.get('orden_clase', 1)
            minutos_desde_inicio = (orden - 1) * duracion
            hora_inicio_dt = datetime.combine(hoy, hora_inicio) + pd.Timedelta(minutes=minutos_desde_inicio)
            hora_fin_dt = hora_inicio_dt + pd.Timedelta(minutes=duracion)
            
            horario_semanal[dias[dia]].append({
                "orden": orden,
                "hora_inicio": hora_inicio_dt.strftime('%H:%M'),
                "hora_fin": hora_fin_dt.strftime('%H:%M'),
                "asignatura": clase.get('asignatura', 'Sin asignar'),
                "salon": clase.get('salon', 'N/A')
            })
    
    return horario_semanal


def mostrar_horario_semanal_detallado(curso, headers):
    """Muestra el horario semanal en formato expandible por día"""
    
    try:
        horario_semanal = obtener_horario_semanal(curso, headers)
        
        if not horario_semanal:
            st.info("No hay horario configurado para este curso")
            return
        
        for dia, clases in horario_semanal.items():
            if clases:
                with st.expander(f"📅 {dia}"):
                    for clase in clases:
                        col1, col2, col3 = st.columns([2, 3, 1])
                        with col1:
                            st.write(f"**{clase['hora_inicio']} - {clase['hora_fin']}**")
                        with col2:
                            st.write(clase['asignatura'])
                        with col3:
                            st.write(f"📌 {clase['salon']}")
    except Exception as e:
        st.info("No hay horario configurado para este curso")

def mostrar_horario_curso_tabla(curso, headers):
    """Muestra el horario completo de un curso en formato tabla"""
    
    # Obtener nivel del curso
    url_nivel = f"{SUPABASE_URL}/rest/v1/horario_base?curso=eq.{curso}&select=nivel_id&limit=1"
    response_nivel = requests.get(url_nivel, headers=headers)
    
    if response_nivel.status_code != 200 or not response_nivel.json():
        st.info(f"No hay horario configurado para el curso {curso}")
        return
    
    nivel_id = response_nivel.json()[0].get('nivel_id')
    
    # Obtener configuración del nivel
    url_config = f"{SUPABASE_URL}/rest/v1/config_horario_nivel?nivel_id=eq.{nivel_id}"
    response_config = requests.get(url_config, headers=headers)
    
    if response_config.status_code != 200 or not response_config.json():
        st.info("No hay configuración de jornada para este nivel")
        return
    
    config = response_config.json()[0]
    dias_laborales = config.get('dias_laborales', [1,2,3,4,5])
    num_clases = config.get('num_clases_por_dia', 6)
    hora_inicio = parse_hora(config.get('hora_inicio_jornada', '07:00'))
    duracion = config.get('duracion_clase_minutos', 50)
    
    # Calcular todas las horas
    horas = []
    hoy = datetime.now().date()
    for orden in range(1, num_clases + 1):
        minutos_desde_inicio = (orden - 1) * duracion
        hora_inicio_dt = datetime.combine(hoy, hora_inicio) + pd.Timedelta(minutes=minutos_desde_inicio)
        hora_fin_dt = hora_inicio_dt + pd.Timedelta(minutes=duracion)
        horas.append(f"{hora_inicio_dt.strftime('%H:%M')} - {hora_fin_dt.strftime('%H:%M')}")
    
    # Obtener horario base del curso
    url_horario = f"{SUPABASE_URL}/rest/v1/horario_base?curso=eq.{curso}&order=dia_semana.asc,orden_clase.asc"
    response_horario = requests.get(url_horario, headers=headers)
    
    if response_horario.status_code != 200:
        st.info("No hay horario configurado")
        return
    
    horarios = response_horario.json()
    
    # Crear mapa de horario
    dias_map = {1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves", 5: "Viernes", 6: "Sábado"}
    
    # Crear matriz de horario
    matriz = {}
    for dia in dias_laborales:
        matriz[dias_map[dia]] = {}
        for hora in horas:
            matriz[dias_map[dia]][hora] = "—"
    
    # Llenar matriz con datos
    for clase in horarios:
        dia = dias_map.get(clase.get('dia_semana'), "Lunes")
        orden = clase.get('orden_clase', 1)
        if 1 <= orden <= len(horas):
            hora = horas[orden - 1]
            matriz[dia][hora] = f"{clase.get('asignatura', 'Sin asignar')}\n📌 {clase.get('salon', 'N/A')}"
    
    # Crear DataFrame para mostrar
    data = []
    for hora in horas:
        fila = {"Horario": hora}
        for dia in dias_map.values():
            if dia in matriz:
                fila[dia] = matriz[dia].get(hora, "—")
            else:
                fila[dia] = "—"
        data.append(fila)
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
