# ==============================================================================
# modulos/features/horarios.py - GESTIÓN COMPACTA CON BASE SANEADA
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
def configurar_niveles(headers=None):
    if headers is None:
        headers = get_headers()

    st.subheader("📚 Niveles Educativos")
    col_tabla, col_form = st.columns([1.3, 1], gap="medium")
    
    r_niveles = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    niveles = r_niveles.json() if r_niveles.status_code == 200 else []

    with col_tabla:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 9px 12px; margin-bottom: 8px;">
            <b style="color: #0F172A; font-size: 13.5px;">📋 Niveles Registrados</b>
        </div>
        """, unsafe_allow_html=True)
        if niveles:
            df = pd.DataFrame(niveles)[['orden', 'nombre']].rename(columns={'orden': 'Orden', 'nombre': 'Nivel'})
            st.dataframe(df, use_container_width=True, height=240)
        else:
            st.info("No hay niveles registrados.")

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
# 2. FRANJAS HORARIAS POR NIVEL (horas_nivel)
# ==============================================================================
def configurar_horas_nivel(headers=None):
    if headers is None:
        headers = get_headers()

    st.subheader("⏰ Franjas Horarias por Nivel")
    
    r_niveles = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    niveles = r_niveles.json() if r_niveles.status_code == 200 else []
    
    if not niveles:
        st.warning("⚠️ Registra los niveles educativos primero.")
        return

    nombres_niveles = [n['nombre'] for n in niveles]
    dict_niveles = {n['nombre']: n['id'] for n in niveles}

    c_sel, _ = st.columns([1.5, 2.5])
    with c_sel:
        nivel_sel = st.selectbox("Seleccionar nivel:", nombres_niveles, key="horas_nivel_select")
    
    nivel_id = dict_niveles[nivel_sel]

    url_horas = f"{SUPABASE_URL}/rest/v1/horas_nivel?nivel_id=eq.{nivel_id}&order=orden.asc"
    r_horas = requests.get(url_horas, headers=headers)
    horas = r_horas.json() if r_horas.status_code == 200 else []

    col_tabla, col_form = st.columns([1.3, 1], gap="medium")

    with col_tabla:
        st.markdown(f"""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 9px 12px; margin-bottom: 8px;">
            <b style="color: #0F172A; font-size: 13.5px;">📋 Franjas de {nivel_sel}</b>
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
            st.dataframe(pd.DataFrame(data_t), use_container_width=True, height=260)

            c_del1, c_del2 = st.columns([2, 1])
            with c_del1:
                h_del = st.selectbox("Hora a eliminar:", [f"Hora #{h['orden']} ({str(h['hora_inicio'])[:5]}-{str(h['hora_fin'])[:5]})" for h in horas], label_visibility="collapsed")
            with c_del2:
                if st.button("🗑️ Eliminar", use_container_width=True, key="del_h_btn"):
                    idx_del = [f"Hora #{h['orden']} ({str(h['hora_inicio'])[:5]}-{str(h['hora_fin'])[:5]})" for h in horas].index(h_del)
                    requests.delete(f"{SUPABASE_URL}/rest/v1/horas_nivel?id=eq.{horas[idx_del]['id']}", headers=headers)
                    st.success("Hora eliminada")
                    st.rerun()
        else:
            st.info(f"Sin franjas registradas para {nivel_sel}.")

    with col_form:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 9px 12px; margin-bottom: 8px;">
            <b style="color: #0F172A; font-size: 13.5px;">➕ Agregar Franja</b>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_add_hora", clear_on_submit=True):
            orden = st.number_input("Orden de la hora:", min_value=1, max_value=20, value=len(horas) + 1, step=1)
            c1, c2 = st.columns(2)
            with c1:
                hora_inicio = st.time_input("Hora inicio:", value=time(7, 0))
            with c2:
                hora_fin = st.time_input("Hora fin:", value=time(7, 50))
            descripcion = st.text_input("Descripción:", value=f"Hora #{orden}")

            if st.form_submit_button("💾 Guardar Franja", type="primary", use_container_width=True):
                data_insert = {
                    "nivel_id": nivel_id,
                    "orden": int(orden),
                    "hora_inicio": str(hora_inicio),
                    "hora_fin": str(hora_fin),
                    "descripcion": descripcion.strip()
                }
                requests.post(f"{SUPABASE_URL}/rest/v1/horas_nivel", headers=headers, json=data_insert)
                st.success("Franja guardada")
                st.rerun()


# ==============================================================================
# 3. DÍAS LABORALES (config_horario_nivel)
# ==============================================================================
def configurar_jornada_nivel(headers=None):
    if headers is None:
        headers = get_headers()

    st.subheader("📅 Días Laborales y Jornada por Nivel")
    
    r_niveles = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    niveles = r_niveles.json() if r_niveles.status_code == 200 else []
    
    if not niveles:
        st.warning("⚠️ No hay niveles configurados.")
        return

    nombres_niveles = [n['nombre'] for n in niveles]
    dict_niveles = {n['nombre']: n['id'] for n in niveles}

    c_sel, _ = st.columns([1.5, 2.5])
    with c_sel:
        nivel_sel = st.selectbox("Seleccionar nivel:", nombres_niveles, key="jornada_nivel_select")
    
    nivel_id = dict_niveles[nivel_sel]

    url_config = f"{SUPABASE_URL}/rest/v1/config_horario_nivel?nivel_id=eq.{nivel_id}"
    res_conf = requests.get(url_config, headers=headers)
    conf_data = res_conf.json()[0] if res_conf.status_code == 200 and res_conf.json() else {}
    
    dias_default = conf_data.get('dias_laborales', [1, 2, 3, 4, 5])
    rotativo_default = conf_data.get('horario_rotativo', False)
    config_id = conf_data.get('id')

    col_izq, col_der = st.columns([1.3, 1], gap="medium")

    with col_izq:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 9px 12px; margin-bottom: 8px;">
            <b style="color: #0F172A; font-size: 13.5px;">📋 Panorama de Jornadas</b>
        </div>
        """, unsafe_allow_html=True)
        
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
            <b style="color: #0F172A; font-size: 13.5px;">✏️ Parametrizar {nivel_sel}</b>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_jornada_conf"):
            dias_seleccionados = st.multiselect(
                "Días de clase activos:",
                options=list(DIAS_SEMANA_MAP.keys()),
                format_func=lambda x: DIAS_SEMANA_MAP[x],
                default=dias_default
            )
            horario_rotativo = st.checkbox("Horario rotativo", value=rotativo_default)

            if st.form_submit_button("💾 Guardar Configuración", type="primary", use_container_width=True):
                payload = {
                    "nivel_id": nivel_id,
                    "dias_laborales": dias_seleccionados,
                    "horario_rotativo": horario_rotativo
                }
                if config_id:
                    requests.patch(f"{SUPABASE_URL}/rest/v1/config_horario_nivel?id=eq.{config_id}", headers=headers, json=payload)
                else:
                    requests.post(f"{SUPABASE_URL}/rest/v1/config_horario_nivel", headers=headers, json=payload)
                st.success("Configuración guardada")
                st.rerun()


# ==============================================================================
# 4. HORARIO POR CURSO (horario_base - LECTURA DIRECTA Y EDICIÓN COMPACTA)
# ==============================================================================
def configurar_horario_curso(headers=None):
    if headers is None:
        headers = get_headers()

    st.subheader("📅 Malla Curricular por Curso")

    # 1. Obtener cursos y niveles desde grados
    r_grados = requests.get(f"{SUPABASE_URL}/rest/v1/grados?order=curso.asc", headers=headers)
    grados_data = r_grados.json() if r_grados.status_code == 200 else []
    
    if grados_data:
        cursos = [g['curso'] for g in grados_data if g.get('curso')]
        map_curso_nivel = {g['curso']: g.get('nivel_id') for g in grados_data}
    else:
        cursos = ["901", "902", "903", "1001", "1002", "1003", "1101"]
        map_curso_nivel = {}

    col_sel_curso, _ = st.columns([1.5, 2.5])
    with col_sel_curso:
        curso_sel = st.selectbox("Selecciona el curso a gestionar:", cursos, key="curso_select_real")

    nivel_id_curso = map_curso_nivel.get(curso_sel, 1)

    # 2. Cargar clases existentes desde horario_base
    url_horario = f"{SUPABASE_URL}/rest/v1/horario_base?curso=eq.{curso_sel}&order=orden_clase.asc,dia_semana.asc"
    r_horario = requests.get(url_horario, headers=headers)
    horarios_curso = r_horario.json() if r_horario.status_code == 200 else []

    # 3. Franjas horarias: buscar en horas_nivel y asegurar las presentes en horario_base
    url_horas = f"{SUPABASE_URL}/rest/v1/horas_nivel?nivel_id=eq.{nivel_id_curso}&order=orden.asc"
    r_horas = requests.get(url_horas, headers=headers)
    horas_db = r_horas.json() if r_horas.status_code == 200 else []

    horas_map = {}
    for h in horas_db:
        o = int(h['orden'])
        horas_map[o] = {
            "orden": o,
            "inicio": str(h.get('hora_inicio', '07:00'))[:5],
            "fin": str(h.get('hora_fin', '07:50'))[:5]
        }
    
    for item in horarios_curso:
        o = item.get('orden_clase')
        if o is not None:
            o_int = int(o)
            if o_int not in horas_map:
                horas_map[o_int] = {
                    "orden": o_int,
                    "inicio": str(item.get('hora_inicio', '07:00'))[:5],
                    "fin": str(item.get('hora_fin', '07:50'))[:5]
                }

    if not horas_map:
        for idx_def in range(1, 7):
            horas_map[idx_def] = {"orden": idx_def, "inicio": f"{6+idx_def:02d}:00", "fin": f"{6+idx_def:02d}:50"}

    lista_horas = [horas_map[k] for k in sorted(horas_map.keys())]

    # 4. Diccionario de docentes
    r_docentes = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
    docentes = r_docentes.json() if r_docentes.status_code == 200 else []
    docentes_dict = {str(d['documento_docente']): f"{d['nombre_docente']} {d['apellidos_docente']}" for d in docentes}

    # Indexar clases por (dia_semana, orden_clase)
    matriz_clases = {}
    for cl in horarios_curso:
        try:
            d = int(cl.get('dia_semana'))
            o = int(cl.get('orden_clase'))
            matriz_clases[(d, o)] = cl
        except (ValueError, TypeError):
            continue

    st.markdown("""
    <style>
        .celda-malla {
            border: 1px solid #CBD5E1;
            padding: 4px 2px;
            text-align: center;
            height: 52px;
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
            margin-bottom: 3px;
        }
        .celda-malla.vacia {
            background-color: #F8FAFC;
            border: 1px dashed #E2E8F0;
        }
        .celda-malla .asig {
            font-weight: 700;
            font-size: 11px;
            line-height: 1.1;
            color: #1E3A8A;
        }
        .celda-malla .prof {
            font-size: 9px;
            color: #475569;
            line-height: 1.1;
        }
        .celda-malla .sal {
            font-size: 8.5px;
            color: #64748B;
        }
        .hdr-col {
            background-color: #1E293B;
            color: white;
            padding: 4px 2px;
            text-align: center;
            font-weight: 700;
            font-size: 11px;
            border-radius: 6px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 3px;
        }
        .hdr-hora {
            background-color: #F1F5F9;
            border: 1px solid #CBD5E1;
            padding: 4px 2px;
            text-align: center;
            font-weight: 600;
            font-size: 9.5px;
            border-radius: 6px;
            color: #334155;
            height: 52px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            box-sizing: border-box;
            margin-bottom: 3px;
        }
    </style>
    """, unsafe_allow_html=True)

    col_malla, col_editor = st.columns([1.8, 1.1], gap="medium")

    # === COLUMNA IZQUIERDA: MALLA SEMANAL COMPLETA ===
    with col_malla:
        st.markdown(f"""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 7px 12px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center;">
            <b style="color: #0F172A; font-size: 13px;">🗓️ Horario Semanal: Grado {curso_sel}</b>
            <span style="font-size: 11px; color: #166534; background: #DCFCE7; padding: 2px 8px; border-radius: 12px; font-weight: 600;">
                {len(horarios_curso)} clases cargadas
            </span>
        </div>
        """, unsafe_allow_html=True)

        dias_cols = [1, 2, 3, 4, 5]
        if any(int(h.get('dia_semana', 0)) == 6 for h in horarios_curso):
            dias_cols.append(6)

        c_hdr = st.columns(len(dias_cols) + 1, gap="small")
        with c_hdr[0]:
            st.markdown('<div class="hdr-col">Hora</div>', unsafe_allow_html=True)
        for i_d, d_num in enumerate(dias_cols):
            with c_hdr[i_d + 1]:
                st.markdown(f'<div class="hdr-col">{DIAS_SEMANA_MAP[d_num][:3]}</div>', unsafe_allow_html=True)

        for h_info in lista_horas:
            o_num = h_info['orden']
            c_row = st.columns(len(dias_cols) + 1, gap="small")
            with c_row[0]:
                st.markdown(f'<div class="hdr-hora"><b>#{o_num}</b><br>{h_info["inicio"]}-{h_info["fin"]}</div>', unsafe_allow_html=True)
            
            for i_d, d_num in enumerate(dias_cols):
                with c_row[i_d + 1]:
                    clase = matriz_clases.get((d_num, o_num))
                    if clase:
                        doc_id = str(clase.get('documento_docente') or '')
                        doc_nom = docentes_dict.get(doc_id, doc_id) if doc_id else ""
                        partes = doc_nom.split()
                        doc_corto = f"{partes[0]} {partes[1]}" if len(partes) >= 2 else doc_nom
                        salon_badge = f'<div class="sal">📌 {clase.get("salon")}</div>' if clase.get("salon") else ''

                        st.markdown(f'''
                        <div class="celda-malla">
                            <span class="asig">{clase.get("asignatura", "?")}</span>
                            <span class="prof">👨‍🏫 {doc_corto}</span>
                            {salon_badge}
                        </div>
                        ''', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="celda-malla vacia"><span style="color:#94A3B8;">—</span></div>', unsafe_allow_html=True)

    # === COLUMNA DERECHA: ASIGNADOR RÁPIDO DIRECTO A horario_base ===
    with col_editor:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 7px 12px; margin-bottom: 6px;">
            <b style="color: #0F172A; font-size: 13px;">✏️ Asignar o Editar Casilla</b>
        </div>
        """, unsafe_allow_html=True)

        c_d, c_h = st.columns(2)
        with c_d:
            dia_sel_nom = st.selectbox("Día:", ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"], key="dia_asignar_slot")
        with c_h:
            hora_sel_orden = st.selectbox("Hora:", [h['orden'] for h in lista_horas], format_func=lambda x: f"Hora #{x}", key="hora_asignar_slot")

        dia_num = DIAS_INVERSO[dia_sel_nom]
        h_actual = next((h for h in lista_horas if h['orden'] == hora_sel_orden), lista_horas[0])
        existente = matriz_clases.get((dia_num, hora_sel_orden))

        with st.form("form_asignar_casilla_real"):
            asig_val = existente.get('asignatura', '') if existente else ''
            doc_val = str(existente.get('documento_docente') or '') if existente else ''
            salon_val = existente.get('salon', '') if existente else ''

            asignatura_in = st.text_input("Asignatura *:", value=asig_val, placeholder="Ej: FISICA, SOCIALES")

            lista_docs = [""] + list(docentes_dict.keys())
            idx_doc = lista_docs.index(doc_val) if doc_val in lista_docs else 0
            docente_in = st.selectbox(
                "Docente:",
                options=lista_docs,
                index=idx_doc,
                format_func=lambda x: docentes_dict.get(x, "Sin docente") if x else "Ninguno"
            )

            salon_in = st.text_input("Salón / Aula:", value=salon_val, placeholder="Ej: Aula 101, Lab")

            col_b1, col_b2 = st.columns(2)
            with col_b1:
                btn_guardar = st.form_submit_button("💾 Guardar", type="primary", use_container_width=True)
            with col_b2:
                btn_vaciar = st.form_submit_button("🗑️ Vaciar", use_container_width=True)

            if btn_guardar:
                if not asignatura_in.strip():
                    st.error("Escribe la asignatura")
                else:
                    payload = {
                        "curso": curso_sel,
                        "nivel_id": nivel_id_curso,
                        "dia_semana": dia_num,
                        "orden_clase": hora_sel_orden,
                        "hora_inicio": f"{h_actual['inicio']}:00",
                        "hora_fin": f"{h_actual['fin']}:00",
                        "asignatura": asignatura_in.strip().upper(),
                        "documento_docente": docente_in if docente_in else None,
                        "salon": salon_in.strip().upper() if salon_in else ""
                    }
                    if existente and existente.get('id'):
                        requests.patch(f"{SUPABASE_URL}/rest/v1/horario_base?id=eq.{existente['id']}", headers=headers, json=payload)
                    else:
                        requests.post(f"{SUPABASE_URL}/rest/v1/horario_base", headers=headers, json=payload)
                    
                    st.success("Casilla guardada")
                    st.rerun()

            if btn_vaciar:
                if existente and existente.get('id'):
                    requests.delete(f"{SUPABASE_URL}/rest/v1/horario_base?id=eq.{existente['id']}", headers=headers)
                    st.info("Casilla vaciada")
                    st.rerun()


# ==============================================================================
# 5. GESTIÓN DE FESTIVOS (festivos)
# ==============================================================================
def gestion_festivos(headers=None):
    if headers is None:
        headers = get_headers()

    st.subheader("📆 Calendario Escolar y Festivos")
    
    col_sel_y, _ = st.columns([1.5, 2.5])
    with col_sel_y:
        year = st.selectbox("Año Lectivo:", [2025, 2026, 2027], index=1, key="festivos_year")

    url_festivos = f"{SUPABASE_URL}/rest/v1/festivos?year=eq.{year}&order=fecha.asc"
    res_f = requests.get(url_festivos, headers=headers)
    festivos = res_f.json() if res_f.status_code == 200 else []

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
                    requests.delete(f"{SUPABASE_URL}/rest/v1/festivos?id=eq.{festivos[idx_f]['id']}", headers=headers)
                    st.success("Festivo eliminado")
                    st.rerun()
        else:
            st.info(f"No hay festivos registrados para {year}.")

    with col_der:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 9px 12px; margin-bottom: 8px;">
            <b style="color: #0F172A; font-size: 13.5px;">➕ Registrar Festivo</b>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_add_festivo", clear_on_submit=True):
            fecha = st.date_input("Fecha:", key="festivo_
