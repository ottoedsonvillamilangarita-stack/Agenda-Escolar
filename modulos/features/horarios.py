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
        nuevo_nivel = st.text_input("Nombre del nivel", key="nuevo_nivel_input")
        if st.button("Agregar nivel", key="agregar_nivel_btn"):
            if nuevo_nivel:
                data = {"nombre": nuevo_nivel, "orden": len(niveles) + 1 if niveles else 1}
                r = requests.post(f"{SUPABASE_URL}/rest/v1/niveles", headers=headers, json=data)
                if r.status_code == 201:
                    st.success(f"✅ Nivel '{nuevo_nivel}' agregado")
                    st.rerun()


def configurar_horas_nivel(headers):
    st.subheader("⏰ Configurar Horas por Nivel")
    st.info("Define las franjas horarias (horas de clase) para cada nivel.")
    
    response_niveles = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    
    if response_niveles.status_code != 200:
        st.error("Error al cargar niveles")
        return
    
    niveles = response_niveles.json()
    
    if not niveles:
        st.warning("No hay niveles configurados")
        return
    
    nivel_nombres = [n['nombre'] for n in niveles]
    nivel_seleccionado = st.selectbox("Seleccionar nivel", nivel_nombres, key="horas_nivel_select")
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
            orden = st.number_input("Orden", min_value=1, max_value=20, value=len(horas) + 1, step=1, key="nueva_hora_orden")
        with col2:
            hora_inicio = st.time_input("Hora inicio", value=time(7, 0), key="nueva_hora_inicio")
        with col3:
            hora_fin = st.time_input("Hora fin", value=time(7, 50), key="nueva_hora_fin")
        with col4:
            descripcion = st.text_input("Descripción", placeholder="Ej: Primera hora", key="nueva_hora_desc")
        
        if st.button("➕ Agregar hora", key="agregar_hora_btn"):
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
    nivel_seleccionado = st.selectbox("Seleccionar nivel", nivel_nombres, key="jornada_nivel_select")
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
        default=dias_laborales_default,
        key="dias_laborales_select"
    )
    
    horario_rotativo = st.checkbox("Horario rotativo", value=horario_rotativo_default, key="horario_rotativo_check")
    
    if st.button("💾 Guardar configuración", type="primary", key="guardar_jornada_btn"):
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


def configurar_horario_curso(headers):
    st.subheader("📅 Asignar Materias por Curso")
    
    cursos = ["901", "902", "903", "1001", "1002", "1003", "1101"]
    
    response_niveles = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    niveles = response_niveles.json() if response_niveles.status_code == 200 else []
    
    if not niveles:
        st.warning("No hay niveles configurados")
        return
    
    curso = st.selectbox("Curso", cursos, key="curso_select")
    nivel_curso = st.selectbox("Nivel del curso", [n['nombre'] for n in niveles], key="nivel_curso_select")
    nivel_id = next(n['id'] for n in niveles if n['nombre'] == nivel_curso)
    
    # Obtener horas del nivel
    url_horas = f"{SUPABASE_URL}/rest/v1/horas_nivel?nivel_id=eq.{nivel_id}&order=orden.asc"
    response_horas = requests.get(url_horas, headers=headers)
    horas = response_horas.json() if response_horas.status_code == 200 else []
    
    if not horas:
        st.warning(f"No hay horas configuradas para el nivel {nivel_curso}. Ve a 'Horas por Nivel' primero.")
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
    dias = {1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves", 5: "Viernes", 6: "Sábado"}
    
    st.write(f"**Asignación de materias para curso {curso} - Nivel {nivel_curso}**")
    st.info(f"Horas del nivel: {len(horas)} clases por día")
    
    # Mostrar tabla de asignación
    for hora in horas:
        st.write(f"**Hora {hora['orden']}: {str(hora['hora_inicio'])[:5]} - {str(hora['hora_fin'])[:5]}**")
        
        cols = st.columns(len(dias))
        for idx, (dia_num, dia_nombre) in enumerate(dias.items()):
            with cols[idx]:
                st.write(f"📅 {dia_nombre}")
                
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
                    requests.delete(f"{SUPABASE_URL}/rest/v1/horario_base?id=eq.{existente['id']}", headers=headers)
        
        st.divider()
    
    if st.button("💾 Guardar todas las asignaciones", type="primary", key="guardar_asignaciones_btn"):
        st.success("✅ Horario guardado")
        st.rerun()


def gestion_festivos(headers):
    st.subheader("📆 Festivos")
    
    year = st.selectbox("Año", [2024, 2025, 2026], key="festivos_year")
    
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
                    if st.button("🗑️", key=f"del_festivo_{f['id']}"):
                        requests.delete(f"{SUPABASE_URL}/rest/v1/festivos?id=eq.{f['id']}", headers=headers)
                        st.rerun()
    
    with st.expander("➕ Agregar festivo"):
        col1, col2 = st.columns(2)
        with col1:
            fecha = st.date_input("Fecha", key="festivo_fecha")
        with col2:
            descripcion = st.text_input("Descripción", key="festivo_desc")
        
        if st.button("Agregar", key="agregar_festivo_btn"):
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
# VISUALIZACIÓN DE HORARIO
# ============================================

def mostrar_horario_tabla(curso, headers):
    """Muestra el horario de un curso en formato tabla"""
    
    url_horario = f"{SUPABASE_URL}/rest/v1/horario_base?curso=eq.{curso}&order=dia_semana.asc,orden_clase.asc"
    response_horario = requests.get(url_horario, headers=headers)
    
    if response_horario.status_code != 200:
        st.info("No hay horario configurado")
        return
    
    horarios = response_horario.json()
    
    if not horarios:
        st.info("No hay horario configurado para este curso")
        return
    
    dias = {1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves", 5: "Viernes", 6: "Sábado"}
    
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
    
    st.markdown("---")
    
    cols = st.columns(len(dias))
    for idx, dia in enumerate(dias.values()):
        with cols[idx]:
            st.markdown(f"**{dia}**")
    
    max_clases = max([len(horario_por_dia[dia]) for dia in dias.values()]) if horarios else 0
    
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
    """Muestra el horario del docente usando la función unificada"""
    
    # Obtener horarios del docente
    url = f"{SUPABASE_URL}/rest/v1/horario_base?documento_docente=eq.{documento_docente}&order=dia_semana.asc,orden_clase.asc"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        st.info("No hay horario configurado para este docente")
        return
    
    horarios = response.json()
    
    if not horarios:
        st.info("No hay horario configurado para este docente")
        return
    
    # Usar la función unificada
    mostrar_horario_unificado(horarios, "📅 Mi Horario Semanal")
def mostrar_horario_unificado(horarios, titulo="📅 Mi Horario Semanal", tipo_vista="docente"):
    """
    Muestra un horario en formato tabla con st.columns
    
    Parámetros:
    - horarios: lista de horarios (diccionarios)
    - titulo: título a mostrar
    - tipo_vista: "docente" (muestra curso) o "estudiante" (muestra docente)
    """
    
    if not horarios:
        st.info("No hay horario disponible")
        return
    
    # Días
    dias = {1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves", 5: "Viernes", 6: "Sábado"}
    
    # Agrupar por hora
    horas_dict = {}
    for clase in horarios:
        hora_inicio = clase.get('hora_inicio', '')[:5] if clase.get('hora_inicio') else ''
        hora_fin = clase.get('hora_fin', '')[:5] if clase.get('hora_fin') else ''
        hora_key = f"{hora_inicio} - {hora_fin}"
        
        if hora_key not in horas_dict:
            horas_dict[hora_key] = {}
            for dia in dias.values():
                horas_dict[hora_key][dia] = None
        
        dia = dias.get(clase.get('dia_semana'), "Lunes")
        
        # Obtener nombre del docente si es vista de estudiante
        docente_nombre = ""
        if tipo_vista == "estudiante":
            doc_documento = clase.get('documento_docente')
            if doc_documento:
                # Buscar el nombre del docente en la sesión o hacer consulta
                # Por ahora usamos una consulta simple
                try:
                    url_doc = f"{SUPABASE_URL}/rest/v1/docentes?documento_docente=eq.{doc_documento}"
                    response_doc = requests.get(url_doc, headers=get_headers())
                    if response_doc.status_code == 200 and response_doc.json():
                        d = response_doc.json()[0]
                        docente_nombre = f"{d.get('nombre_docente', '')} {d.get('apellidos_docente', '')}".strip()
                except:
                    docente_nombre = doc_documento
        
        horas_dict[hora_key][dia] = {
            "asignatura": clase.get('asignatura', '?'),
            "curso": clase.get('curso'),
            "salon": clase.get('salon', ''),
            "docente": docente_nombre if docente_nombre else clase.get('documento_docente', '')
        }
    
    # Ordenar horas
    horas_ordenadas = sorted(horas_dict.keys())
    
    if not horas_ordenadas:
        st.info("No hay horario configurado")
        return
    
    # CSS para estilos
    st.markdown("""
    <style>
        .horario-celda {
            border: 1px solid #ddd;
            padding: 4px 2px;
            text-align: center;
            min-height: 52px;
            height: 52px;
            max-height: 52px;
            background-color: white;
            border-radius: 4px;
            font-size: 11px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            width: 100%;
            box-sizing: border-box;
            overflow: hidden;
        }
        .horario-celda.vacia {
            background-color: #f9f9f9;
            min-height: 52px;
            height: 52px;
            max-height: 52px;
        }
        .horario-celda .asignatura {
            font-weight: 600;
            font-size: 12px;
            line-height: 1.2;
            color: #1a237e;
        }
        .horario-celda .curso {
            font-size: 10px;
            color: #444;
            line-height: 1.2;
        }
        .horario-celda .docente {
            font-size: 9px;
            color: #666;
            line-height: 1.2;
        }
        .horario-celda .salon {
            font-size: 8px;
            color: #777;
        }
        .horario-header {
            background-color: #1a237e;
            color: white;
            padding: 6px 2px;
            text-align: center;
            font-weight: 700;
            font-size: 11px;
            border-radius: 4px;
            width: 100%;
            min-height: 52px;
            height: 52px;
            max-height: 52px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .horario-hora {
            background-color: #f0f0f0;
            padding: 6px 2px;
            text-align: center;
            font-weight: 600;
            font-size: 10px;
            border-radius: 4px;
            border: 1px solid #ddd;
            color: #333;
            width: 100%;
            min-height: 52px;
            height: 52px;
            max-height: 52px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-sizing: border-box;
        }
        .stColumn {
            padding: 0 2px !important;
        }
        .row-widget.stColumns {
            gap: 2px !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Mostrar título
    st.subheader(titulo)
    
    # Cabecera: Hora + Días
    cols = st.columns(len(dias) + 1, gap="small")
    with cols[0]:
        st.markdown('<div class="horario-header">Hora</div>', unsafe_allow_html=True)
    for idx, dia in enumerate(dias.values()):
        with cols[idx + 1]:
            st.markdown(f'<div class="horario-header">{dia[:3]}</div>', unsafe_allow_html=True)
    
    # Filas
    for hora in horas_ordenadas:
        cols = st.columns(len(dias) + 1, gap="small")
        
        with cols[0]:
            st.markdown(f'<div class="horario-hora">{hora}</div>', unsafe_allow_html=True)
        
        for idx, dia in enumerate(dias.values()):
            with cols[idx + 1]:
                clase = horas_dict[hora].get(dia)
                if clase:
                    salon = f'<div class="salon">📌 {clase["salon"]}</div>' if clase.get('salon') else ''
                    
                    if tipo_vista == "docente":
                        # Docente ve: Asignatura + Curso
                        st.markdown(f'''
                        <div class="horario-celda">
                            <span class="asignatura">{clase["asignatura"]}</span>
                            <span class="curso">({clase["curso"]})</span>
                            {salon}
                        </div>
                        ''', unsafe_allow_html=True)
                    else:
                        # Estudiante/Acudiente ve: Asignatura + Docente
                        st.markdown(f'''
                        <div class="horario-celda">
                            <span class="asignatura">{clase["asignatura"]}</span>
                            <span class="docente">👨‍🏫 {clase["docente"]}</span>
                            {salon}
                        </div>
                        ''', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="horario-celda vacia"></div>', unsafe_allow_html=True)
