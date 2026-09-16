# ==============================================================================
# modulos/features/horarios.py - GESTIÓN COMPACTA CON BASE DE DATOS ORIGINAL
# ==============================================================================

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, time
from utils import SUPABASE_URL, get_headers

DIAS_SEMANA_MAP = {
    1: "Lunes",
    2: "Martes",
    3: "Miércoles",
    4: "Jueves",
    5: "Viernes",
    6: "Sábado"
}
DIAS_INVERSO = {v: k for k, v in DIAS_SEMANA_MAP.items()}

# ==============================================================================
# FUNCIONES AUXILIARES
# ==============================================================================
def parse_hora(hora_str):
    """Convierte string de hora a objeto time"""
    if isinstance(hora_str, time):
        return hora_str
    if isinstance(hora_str, str):
        partes = hora_str.split(':')
        if len(partes) >= 2:
            return time(int(partes[0]), int(partes[1]))
    return time(7, 0)


# ==============================================================================
# 1. NIVELES EDUCATIVOS
# ==============================================================================
def configurar_niveles(headers):
    st.subheader("📚 Niveles Educativos")
    
    col_tabla, col_form = st.columns([1.3, 1], gap="medium")
    response = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    niveles = response.json() if response.status_code == 200 else []

    with col_tabla:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 9px 12px; margin-bottom: 8px;">
            <b style="color: #0F172A; font-size: 13.5px;">📋 Niveles Registrados</b>
        </div>
        """, unsafe_allow_html=True)
        if niveles:
            df = pd.DataFrame(niveles)[['orden', 'nombre']].rename(columns={'orden': 'Orden', 'nombre': 'Nivel'})
            st.dataframe(df, use_container_width=True, height=250)
        else:
            st.info("No hay niveles creados.")

    with col_form:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 9px 12px; margin-bottom: 8px;">
            <b style="color: #0F172A; font-size: 13.5px;">➕ Nuevo Nivel</b>
        </div>
        """, unsafe_allow_html=True)
        with st.form("form_nuevo_nivel_h", clear_on_submit=True):
            nuevo_nivel = st.text_input("Nombre del nivel *")
            if st.form_submit_button("💾 Guardar Nivel", type="primary", use_container_width=True):
                if nuevo_nivel:
                    data = {"nombre": nuevo_nivel.strip(), "orden": len(niveles) + 1 if niveles else 1}
                    r = requests.post(f"{SUPABASE_URL}/rest/v1/niveles", headers=headers, json=data)
                    if r.status_code == 201:
                        st.success(f"Nivel '{nuevo_nivel}' agregado")
                        st.rerun()


# ==============================================================================
# 2. FRANJAS HORARIAS POR NIVEL (TABLA REAL: horas_nivel)
# ==============================================================================
def configurar_horas_nivel(headers):
    st.subheader("⏰ Configurar Horas por Nivel")
    
    response_niveles = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    niveles = response_niveles.json() if response_niveles.status_code == 200 else []
    
    if not niveles:
        st.warning("⚠️ No hay niveles configurados. Ve a 'Niveles' primero.")
        return

    nivel_nombres = [n['nombre'] for n in niveles]
    dict_niveles = {n['nombre']: n['id'] for n in niveles}

    c_sel, _ = st.columns([1.5, 2.5])
    with c_sel:
        nivel_seleccionado = st.selectbox("Seleccionar nivel a parametrizar:", nivel_nombres, key="horas_nivel_select")
    
    nivel_id = dict_niveles[nivel_seleccionado]

    url_horas = f"{SUPABASE_URL}/rest/v1/horas_nivel?nivel_id=eq.{nivel_id}&order=orden.asc"
    response_horas = requests.get(url_horas, headers=headers)
    horas = response_horas.json() if response_horas.status_code == 200 else []

    col_tabla, col_form = st.columns([1.3, 1], gap="medium")

    # Columna Izquierda: Tabla y eliminación
    with col_tabla:
        st.markdown(f"""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 9px 12px; margin-bottom: 8px;">
            <b style="color: #0F172A; font-size: 13.5px;">📋 Franjas de {nivel_seleccionado}</b>
        </div>
        """, unsafe_allow_html=True)

        if horas:
            data_t = []
            for h in horas:
                ini = str(h.get('hora_inicio', ''))[:5]
                fin = str(h.get('hora_fin', ''))[:5]
                data_t.append({
                    "Orden": h.get('orden'),
                    "Horario": f"{ini} - {fin}",
                    "Descripción": h.get('descripcion') or f"Hora #{h.get('orden')}"
                })
            st.dataframe(pd.DataFrame(data_t), use_container_width=True, height=270)

            c_del1, c_del2 = st.columns([2, 1])
            with c_del1:
                h_del = st.selectbox("Seleccionar para eliminar:", [f"Hora #{h['orden']} ({str(h['hora_inicio'])[:5]}-{str(h['hora_fin'])[:5]})" for h in horas], label_visibility="collapsed")
            with c_del2:
                if st.button("🗑️ Eliminar", use_container_width=True, key="del_h_btn"):
                    idx_del = [f"Hora #{h['orden']} ({str(h['hora_inicio'])[:5]}-{str(h['hora_fin'])[:5]})" for h in horas].index(h_del)
                    id_h_borrar = horas[idx_del]['id']
                    requests.delete(f"{SUPABASE_URL}/rest/v1/horas_nivel?id=eq.{id_h_borrar}", headers=headers)
                    st.success("Hora eliminada")
                    st.rerun()
        else:
            st.info(f"No hay franjas configuradas para {nivel_seleccionado}.")

    # Columna Derecha: Formulario para añadir franja
    with col_form:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 9px 12px; margin-bottom: 8px;">
            <b style="color: #0F172A; font-size: 13.5px;">➕ Agregar Franja Horaria</b>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_add_hora", clear_on_submit=True):
            orden = st.number_input("Orden de la hora:", min_value=1, max_value=20, value=len(horas) + 1, step=1)
            c1, c2 = st.columns(2)
            with c1:
                hora_inicio = st.time_input("Hora inicio:", value=time(7, 0))
            with c2:
                hora_fin = st.time_input("Hora fin:", value=time(7, 50))
            descripcion = st.text_input("Descripción (Ej: Clase 1, Descanso):", value=f"Hora #{orden}")

            if st.form_submit_button("💾 Guardar Hora", type="primary", use_container_width=True):
                data_insert = {
                    "nivel_id": nivel_id,
                    "orden": int(orden),
                    "hora_inicio": str(hora_inicio),
                    "hora_fin": str(hora_fin),
                    "descripcion": descripcion.strip()
                }
                r = requests.post(f"{SUPABASE_URL}/rest/v1/horas_nivel", headers=headers, json=data_insert)
                if r.status_code in [200, 201]:
                    st.success("✅ Franja horaria guardada")
                    st.rerun()
                else:
                    st.error(f"Error ({r.status_code}): {r.text}")


# ==============================================================================
# 3. JORNADAS Y DÍAS LABORALES (TABLA REAL: config_horario_nivel)
# ==============================================================================
def configurar_jornada_nivel(headers):
    st.subheader("📅 Días Laborales y Rotación por Nivel")
    
    response_niveles = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    niveles = response_niveles.json() if response_niveles.status_code == 200 else []
    
    if not niveles:
        st.warning("⚠️ No hay niveles configurados.")
        return

    nivel_nombres = [n['nombre'] for n in niveles]
    dict_niveles = {n['nombre']: n['id'] for n in niveles}

    c_sel, _ = st.columns([1.5, 2.5])
    with c_sel:
        nivel_seleccionado = st.selectbox("Seleccionar nivel:", nivel_nombres, key="jornada_nivel_select")
    
    nivel_id = dict_niveles[nivel_seleccionado]

    url_config = f"{SUPABASE_URL}/rest/v1/config_horario_nivel?nivel_id=eq.{nivel_id}"
    response_config = requests.get(url_config, headers=headers)
    
    if response_config.status_code == 200 and response_config.json():
        config = response_config.json()[0]
        dias_laborales_default = config.get('dias_laborales', [1, 2, 3, 4, 5])
        horario_rotativo_default = config.get('horario_rotativo', False)
        config_id = config.get('id')
    else:
        dias_laborales_default = [1, 2, 3, 4, 5]
        horario_rotativo_default = False
        config_id = None

    col_izq, col_der = st.columns([1.3, 1], gap="medium")

    with col_izq:
        st.markdown(f"""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 9px 12px; margin-bottom: 8px;">
            <b style="color: #0F172A; font-size: 13.5px;">📋 Resumen Institucional</b>
        </div>
        """, unsafe_allow_html=True)
        
        # Consultar todas las configs
        r_all_conf = requests.get(f"{SUPABASE_URL}/rest/v1/config_horario_nivel", headers=headers)
        all_conf = r_all_conf.json() if r_all_conf.status_code == 200 else []
        conf_map = {c['nivel_id']: c for c in all_conf if c.get('nivel_id')}

        tabla_resumen = []
        for n in niveles:
            c_item = conf_map.get(n['id'])
            if c_item:
                d_str = ", ".join([DIAS_SEMANA_MAP.get(d, str(d))[:3] for d in c_item.get('dias_laborales', [])])
                rot_str = "Sí" if c_item.get('horario_rotativo') else "No"
            else:
                d_str = "Lun, Mar, Mié, Jue, Vie"
                rot_str = "No"
            tabla_resumen.append({"Nivel": n['nombre'], "Días de Clase": d_str, "Rotativo": rot_str})
        st.dataframe(pd.DataFrame(tabla_resumen), use_container_width=True, height=250)

    with col_der:
        st.markdown(f"""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 9px 12px; margin-bottom: 8px;">
            <b style="color: #0F172A; font-size: 13.5px;">✏️ Ajustar {nivel_seleccionado}</b>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_jornada_conf"):
            dias_seleccionados = st.multiselect(
                "Días lectivos activos:",
                options=list(DIAS_SEMANA_MAP.keys()),
                format_func=lambda x: DIAS_SEMANA_MAP[x],
                default=dias_laborales_default
            )
            horario_rotativo = st.checkbox("Activar horario rotativo", value=horario_rotativo_default)

            if st.form_submit_button("💾 Guardar Ajustes", type="primary", use_container_width=True):
                data_config = {
                    "nivel_id": nivel_id,
                    "dias_laborales": dias_seleccionados,
                    "horario_rotativo": horario_rotativo
                }
                if config_id:
                    requests.patch(f"{SUPABASE_URL}/rest/v1/config_horario_nivel?id=eq.{config_id}", headers=headers, json=data_config)
                else:
                    requests.post(f"{SUPABASE_URL}/rest/v1/config_horario_nivel", headers=headers, json=data_config)
                st.success("✅ Configuración actualizada")
                st.rerun()


# ==============================================================================
# 4. HORARIO POR CURSO (TABLA REAL: horario_base - MALLA COMPACTA)
# ==============================================================================
def configurar_horario_curso(headers):
    st.subheader("📅 Asignación de Horario por Curso")
    
    # 1. Obtener cursos y niveles
    r_grados = requests.get(f"{SUPABASE_URL}/rest/v1/grados?order=curso.asc", headers=headers)
    grados = r_grados.json() if r_grados.status_code == 200 else []
    
    r_niveles = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    niveles = r_niveles.json() if r_niveles.status_code == 200 else []
    
    if not niveles:
        st.warning("⚠️ No hay niveles configurados.")
        return

    nombres_niveles = [n['nombre'] for n in niveles]
    dict_niveles = {n['nombre']: n['id'] for n in niveles}
    id_a_nivel = {n['id']: n['nombre'] for n in niveles}

    # Cursos disponibles
    if grados:
        cursos_disp = [g['curso'] for g in grados if g.get('curso')]
        map_curso_nivel = {g['curso']: g.get('nivel_id') for g in grados}
    else:
        cursos_disp = ["901", "902", "903", "1001", "1002", "1003", "1101"]
        map_curso_nivel = {}

    c1, c2 = st.columns([1.5, 1.5])
    with c1:
        curso = st.selectbox("Seleccionar Curso:", cursos_disp, key="curso_select")
    with c2:
        # Nivel predeterminado según el curso
        niv_id_sug = map_curso_nivel.get(curso)
        nom_niv_sug = id_a_nivel.get(niv_id_sug, nombres_niveles[0]) if niv_id_sug else nombres_niveles[0]
        idx_niv = nombres_niveles.index(nom_niv_sug) if nom_niv_sug in nombres_niveles else 0
        nivel_curso = st.selectbox("Nivel del Curso:", nombres_niveles, index=idx_niv, key="nivel_curso_select")
        nivel_id = dict_niveles[nivel_curso]

    # 2. Obtener franjas horarias reales del nivel (horas_nivel)
    url_horas = f"{SUPABASE_URL}/rest/v1/horas_nivel?nivel_id=eq.{nivel_id}&order=orden.asc"
    response_horas = requests.get(url_horas, headers=headers)
    horas = response_horas.json() if response_horas.status_code == 200 else []

    if not horas:
        st.warning(f"⚠️ No hay horas configuradas para el nivel {nivel_curso}. Ve a '⏰ Horas y Franjas por Nivel' primero.")
        return

    # 3. Obtener el horario real cargado en horario_base
    url_horario = f"{SUPABASE_URL}/rest/v1/horario_base?curso=eq.{curso}&order=dia_semana.asc,orden_clase.asc"
    response_horario = requests.get(url_horario, headers=headers)
    horarios_cargados = response_horario.json() if response_horario.status_code == 200 else []

    # 4. Obtener docentes para resolver nombres
    response_docentes = requests.get(f"{SUPABASE_URL}/rest/v1/docentes?order=apellidos_docente.asc", headers=headers)
    docentes = response_docentes.json() if response_docentes.status_code == 200 else []
    docentes_dict = {d['documento_docente']: f"{d['nombre_docente']} {d['apellidos_docente']}" for d in docentes}

    # 5. Obtener materias registradas para sugerencias rápidas
    response_materias = requests.get(f"{SUPABASE_URL}/rest/v1/materias?order=nombre.asc", headers=headers)
    materias_existentes = [m['nombre'] for m in response_materias.json()] if response_materias.status_code == 200 else []

    # Mapear horarios en matriz indexada por (dia_semana, orden_clase)
    matriz_celdas = {}
    for h_item in horarios_cargados:
        d = h_item.get('dia_semana')
        o = h_item.get('orden_clase')
        asig = h_item.get('asignatura', '')
        doc_id = h_item.get('documento_docente')
        sal = h_item.get('salon')
        
        prof_nombre = docentes_dict.get(doc_id, doc_id) if doc_id else ""
        prof_corto = f"({prof_nombre.split()[0]} {prof_nombre.split()[1]})" if len(prof_nombre.split()) >= 2 else (f"({prof_nombre})" if prof_nombre else "")
        sal_tag = f"[{sal}]" if sal else ""
        
        texto_completo = f"{asig}\n{prof_corto} {sal_tag}".strip()
        matriz_celdas[(d, o)] = texto_completo

    # LAYOUT EN 2 COLUMNAS (PANORAMA 70% | EDITOR 30%)
    col_grilla, col_panel = st.columns([1.8, 1.1], gap="medium")

    # === COLUMNA IZQUIERDA: MALLA SEMANAL COMPLETA (Muestra datos reales) ===
    with col_grilla:
        st.markdown(f"""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 8px 12px; margin-bottom: 8px;">
            <b style="color: #0F172A; font-size: 13.5px;">🗓️ Horario Semanal de Clases: {curso} ({len(horarios_cargados)} clases activas)</b>
        </div>
        """, unsafe_allow_html=True)

        filas = []
        for h in horas:
            o_num = h['orden']
            ini = str(h.get('hora_inicio', ''))[:5]
            fin = str(h.get('hora_fin', ''))[:5]
            desc = h.get('descripcion') or f"Hora #{o_num}"
            etiqueta_hora = f"#{o_num} ({ini}-{fin})"

            filas.append({
                "Bloque": etiqueta_hora,
                "Lunes": matriz_celdas.get((1, o_num), "—"),
                "Martes": matriz_celdas.get((2, o_num), "—"),
                "Miércoles": matriz_celdas.get((3, o_num), "—"),
                "Jueves": matriz_celdas.get((4, o_num), "—"),
                "Viernes": matriz_celdas.get((5, o_num), "—"),
                "Sábado": matriz_celdas.get((6, o_num), "—")
            })

        st.dataframe(pd.DataFrame(filas).set_index("Bloque"), use_container_width=True, height=340)

    # === COLUMNA DERECHA: ASIGNADOR RÁPIDO A PRUEBA DE SCROLL ===
    with col_panel:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 8px 12px; margin-bottom: 8px;">
            <b style="color: #0F172A; font-size: 13.5px;">✏️ Asignar o Editar Casilla</b>
        </div>
        """, unsafe_allow_html=True)

        c_dia, c_hora = st.columns(2)
        with c_dia:
            dia_sel_nom = st.selectbox("Día:", ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"], key="dia_asignar_slot")
        with c_hora:
            hora_sel_orden = st.selectbox("Hora / Bloque:", [h['orden'] for h in horas], format_func=lambda x: f"Hora #{x}", key="hora_asignar_slot")

        dia_num = DIAS_INVERSO[dia_sel_nom]
        obj_hora = next(h for h in horas if h['orden'] == hora_sel_orden)
        h_inicio_val = str(obj_hora.get('hora_inicio'))
        h_fin_val = str(obj_hora.get('hora_fin'))

        # Buscar si ya existe asignación previa en esa casilla
        existente = next((item for item in horarios_cargados if item.get('dia_semana') == dia_num and item.get('orden_clase') == hora_sel_orden), None)

        with st.form("form_asignar_casilla_real"):
            asig_actual = existente.get('asignatura', '') if existente else ''
            doc_actual = existente.get('documento_docente', '') if existente else ''
            salon_actual = existente.get('salon', '') if existente else ''

            asignatura_in = st.text_input("Asignatura *:", value=asig_actual, placeholder="Ej: MATEMÁTICAS, BIOLOGÍA")
            
            # Selector de docente
            lista_docs = [""] + list(docentes_dict.keys())
            idx_doc = lista_docs.index(doc_actual) if doc_actual in lista_docs else 0
            docente_in = st.selectbox(
                "Docente encargado:",
                options=lista_docs,
                index=idx_doc,
                format_func=lambda x: docentes_dict.get(x, "Sin docente") if x else "Ninguno"
            )

            salon_in = st.text_input("Salón / Aula:", value=salon_actual, placeholder="Ej: Aula 201, Lab Quim")

            col_b1, col_b2 = st.columns(2)
            with col_b1:
                btn_guardar = st.form_submit_button("💾 Guardar", type="primary", use_container_width=True)
            with col_b2:
                btn_vaciar = st.form_submit_button("🗑️ Vaciar", use_container_width=True)

            if btn_guardar:
                if not asignatura_in.strip():
                    st.error("Ingresa el nombre de la asignatura")
                else:
                    data_horario = {
                        "curso": curso,
                        "nivel_id": nivel_id,
                        "dia_semana": dia_num,
                        "orden_clase": hora_sel_orden,
                        "hora_inicio": h_inicio_val,
                        "hora_fin": h_fin_val,
                        "asignatura": asignatura_in.strip().upper(),
                        "documento_docente": docente_in if docente_in else None,
                        "salon": salon_in.strip().upper() if salon_in else ""
                    }
                    if existente:
                        requests.patch(f"{SUPABASE_URL}/rest/v1/horario_base?id=eq.{existente['id']}", headers=headers, json=data_horario)
                    else:
                        requests.post(f"{SUPABASE_URL}/rest/v1/horario_base", headers=headers, json=data_horario)
                    
                    st.success(f"Casilla de {dia_sel_nom} actualizada")
                    st.rerun()

            if btn_vaciar:
                if existente:
                    requests.delete(f"{SUPABASE_URL}/rest/v1/horario_base?id=eq.{existente['id']}", headers=headers)
                    st.info(f"Casilla de {dia_sel_nom} vaciada")
                    st.rerun()


# ==============================================================================
# 5. GESTIÓN DE FESTIVOS (TABLA REAL: festivos)
# ==============================================================================
def gestion_festivos(headers):
    st.subheader("📆 Calendario Escolar y Festivos")
    
    col_sel_y, _ = st.columns([1.5, 2.5])
    with col_sel_y:
        year = st.selectbox("Año Lectivo:", [2025, 2026, 2027], index=1, key="festivos_year")

    url_festivos = f"{SUPABASE_URL}/rest/v1/festivos?year=eq.{year}&order=fecha.asc"
    response_festivos = requests.get(url_festivos, headers=headers)
    festivos = response_festivos.json() if response_festivos.status_code == 200 else []

    col_izq, col_der = st.columns([1.3, 1], gap="medium")

    with col_izq:
        st.markdown(f"""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 9px 12px; margin-bottom: 8px;">
            <b style="color: #0F172A; font-size: 13.5px;">📋 Días No Lectivos de {year}</b>
        </div>
        """, unsafe_allow_html=True)

        if festivos:
            df = pd.DataFrame(festivos)[['fecha', 'descripcion']].rename(columns={'fecha': 'Fecha', 'descripcion': 'Motivo'})
            st.dataframe(df, use_container_width=True, height=270)

            c_del1, c_del2 = st.columns([2, 1])
            with c_del1:
                f_del_item = st.selectbox("Festivo a eliminar:", [f"{f['fecha']} ({f.get('descripcion')})" for f in festivos], label_visibility="collapsed")
            with c_del2:
                if st.button("🗑️ Quitar", use_container_width=True):
                    idx_f = [f"{f['fecha']} ({f.get('descripcion')})" for f in festivos].index(f_del_item)
                    id_borrar = festivos[idx_f]['id']
                    requests.delete(f"{SUPABASE_URL}/rest/v1/festivos?id=eq.{id_borrar}", headers=headers)
                    st.success("Festivo eliminado")
                    st.rerun()
        else:
            st.info(f"No hay festivos registrados para {year}.")

    with col_der:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 9px 12px; margin-bottom: 8px;">
            <b style="color: #0F172A; font-size: 13.5px;">➕ Agregar Festivo / Receso</b>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_add_festivo", clear_on_submit=True):
            fecha = st.date_input("Fecha:", key="festivo_fecha")
            descripcion = st.text_input("Motivo (Ej: Día Cívico, Semana Santa):", key="festivo_desc")

            if st.form_submit_button("💾 Guardar Festivo", type="primary", use_container_width=True):
                if descripcion.strip():
                    data = {"fecha": str(fecha), "descripcion": descripcion.strip(), "year": fecha.year}
                    r = requests.post(f"{SUPABASE_URL}/rest/v1/festivos", headers=headers, json=data)
                    if r.status_code in [200, 201]:
                        st.success("✅ Festivo agregado")
                        st.rerun()
                    else:
                        st.error(f"Error: {r.text}")


# ==============================================================================
# 6. MENÚ COMPLETO ADMIN HORARIOS
# ==============================================================================
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


# ==============================================================================
# 7. VISUALIZACIÓN UNIFICADA (DOCENTE / ESTUDIANTE / ACUDIENTE)
# ==============================================================================
def mostrar_horario_unificado(horarios, titulo="📅 Mi Horario Semanal", tipo_vista="docente"):
    """Muestra el horario en tarjetas estilizadas para docente o alumno."""
    if not horarios:
        st.info("No hay horario disponible")
        return

    dias = {1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves", 5: "Viernes", 6: "Sábado"}
    
    horas_dict = {}
    for clase in horarios:
        hora_inicio = clase.get('hora_inicio', '')[:5] if clase.get('hora_inicio') else ''
        hora_fin = clase.get('hora_fin', '')[:5] if clase.get('hora_fin') else ''
        hora_key = f"{hora_inicio} - {hora_fin}" if (hora_inicio and hora_fin) else f"Bloque #{clase.get('orden_clase', '?')}"
        
        if hora_key not in horas_dict:
            horas_dict[hora_key] = {dia: None for dia in dias.values()}
        
        dia = dias.get(clase.get('dia_semana'), "Lunes")
        
        docente_nombre = ""
        if tipo_vista == "estudiante":
            doc_documento = clase.get('documento_docente')
            if doc_documento:
                try:
                    url_doc = f"{SUPABASE_URL}/rest/v1/docentes?documento_docente=eq.{doc_documento}"
                    response_doc = requests.get(url_doc, headers=get_headers())
                    if response_doc.status_code == 200 and response_doc.json():
                        d = response_doc.json()[0]
                        docente_nombre = f"{d.get('nombre_docente', '')} {d.get('apellidos_docente', '')}".strip()
                except Exception:
                    docente_nombre = doc_documento
        
        horas_dict[hora_key][dia] = {
            "asignatura": clase.get('asignatura', '?'),
            "curso": clase.get('curso'),
            "salon": clase.get('salon', ''),
            "docente": docente_nombre if docente_nombre else clase.get('documento_docente', '')
        }
    
    horas_ordenadas = sorted(horas_dict.keys())
    if not horas_ordenadas:
        st.info("No hay horario configurado")
        return

    st.markdown("""
    <style>
        .horario-celda {
            border: 1px solid #E2E8F0;
            padding: 4px 2px;
            text-align: center;
            min-height: 48px;
            height: 48px;
            max-height: 48px;
            background-color: white;
            border-radius: 6px;
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
            background-color: #F8FAFC;
        }
        .horario-celda .asignatura {
            font-weight: 700;
            font-size: 11.5px;
            line-height: 1.15;
            color: #1E3A8A;
        }
        .horario-celda .curso {
            font-size: 10px;
            color: #475569;
        }
        .horario-celda .docente {
            font-size: 9.5px;
            color: #334155;
        }
        .horario-celda .salon {
            font-size: 8.5px;
            color: #64748B;
        }
        .horario-header {
            background-color: #1E293B;
            color: white;
            padding: 6px 2px;
            text-align: center;
            font-weight: 700;
            font-size: 11px;
            border-radius: 6px;
            width: 100%;
            min-height: 38px;
            height: 38px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .horario-hora {
            background-color: #F1F5F9;
            padding: 6px 2px;
            text-align: center;
            font-weight: 600;
            font-size: 10.5px;
            border-radius: 6px;
            border: 1px solid #CBD5E1;
            color: #334155;
            width: 100%;
            min-height: 48px;
            height: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f"#### {titulo}")
    
    cols = st.columns(len(dias) + 1, gap="small")
    with cols[0]:
        st.markdown('<div class="horario-header">Hora</div>', unsafe_allow_html=True)
    for idx, dia in enumerate(dias.values()):
        with cols[idx + 1]:
            st.markdown(f'<div class="horario-header">{dia[:3]}</div>', unsafe_allow_html=True)
    
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
                        st.markdown(f'''
                        <div class="horario-celda">
                            <span class="asignatura">{clase["asignatura"]}</span>
                            <span class="curso">({clase["curso"]})</span>
                            {salon}
                        </div>
                        ''', unsafe_allow_html=True)
                    else:
                        st.markdown(f'''
                        <div class="horario-celda">
                            <span class="asignatura">{clase["asignatura"]}</span>
                            <span class="docente">👨‍🏫 {clase["docente"]}</span>
                            {salon}
                        </div>
                        ''', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="horario-celda vacia"></div>', unsafe_allow_html=True)


def mostrar_horario_docente_tabla(documento_docente, headers):
    """Muestra el horario del docente desde horario_base"""
    url = f"{SUPABASE_URL}/rest/v1/horario_base?documento_docente=eq.{documento_docente}&order=dia_semana.asc,orden_clase.asc"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        st.info("No hay horario configurado para este docente")
        return
    
    horarios = response.json()
    if not horarios:
        st.info("No hay horario configurado para este docente")
        return
    
    mostrar_horario_unificado(horarios, "📅 Mi Horario Semanal", "docente")
