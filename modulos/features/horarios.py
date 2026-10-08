# ==============================================================================
# modulos/features/horarios.py - GESTION DE HORARIOS COMPLETA
# ==============================================================================

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, time
from utils import SUPABASE_URL, get_headers

DIAS_SEMANA_MAP = {
    1: "Lunes",
    2: "Martes",
    3: "Miercoles",
    4: "Jueves",
    5: "Viernes",
    6: "Sabado"
}
DIAS_INVERSO = {v: k for k, v in DIAS_SEMANA_MAP.items()}

# ==============================================================================
# FUNCIONES AUXILIARES
# ==============================================================================
def parse_hora(hora_str):
    if isinstance(hora_str, time):
        return hora_str
    if isinstance(hora_str, str):
        partes = hora_str.split(':')
        if len(partes) >= 2:
            return time(int(partes[0]), int(partes[1]))
    return time(7, 0)

def formatear_nombre_corto(nombre_completo):
    if not nombre_completo:
        return ""
    partes = str(nombre_completo).strip().split()
    if len(partes) >= 2:
        return f"{partes[0].capitalize()} {partes[1].capitalize()}"
    return partes[0].capitalize() if partes else ""


# ==============================================================================
# 1. NIVELES EDUCATIVOS
# ==============================================================================
def configurar_niveles(headers=None):
    if headers is None:
        headers = get_headers()

    st.subheader("Niveles Educativos")
    col_tabla, col_form = st.columns([1.3, 1], gap="medium")
    
    r_niveles = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    niveles = r_niveles.json() if r_niveles.status_code == 200 else []

    with col_tabla:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 9px 12px; margin-bottom: 8px;">
            <b style="color: #0F172A; font-size: 13.5px;">Niveles Registrados</b>
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
            <b style="color: #0F172A; font-size: 13.5px;">Nuevo Nivel</b>
        </div>
        """, unsafe_allow_html=True)
        with st.form("form_nuevo_nivel_h", clear_on_submit=True):
            nuevo_nivel = st.text_input("Nombre del nivel *")
            if st.form_submit_button("Guardar Nivel", type="primary", use_container_width=True):
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

    st.subheader("Franjas Horarias por Nivel")
    
    r_niveles = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    niveles = r_niveles.json() if r_niveles.status_code == 200 else []
    
    if not niveles:
        st.warning("Registra los niveles educativos primero.")
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
            <b style="color: #0F172A; font-size: 13.5px;">Franjas de {nivel_sel}</b>
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
                    "Descripcion": h.get('descripcion') or f"Hora #{h.get('orden')}"
                })
            st.dataframe(pd.DataFrame(data_t), use_container_width=True, height=260)

            c_del1, c_del2 = st.columns([2, 1])
            with c_del1:
                h_del = st.selectbox("Hora a eliminar:", [f"Hora #{h['orden']} ({str(h['hora_inicio'])[:5]}-{str(h['hora_fin'])[:5]})" for h in horas], label_visibility="collapsed")
            with c_del2:
                if st.button("Eliminar", use_container_width=True, key="del_h_btn"):
                    idx_del = [f"Hora #{h['orden']} ({str(h['hora_inicio'])[:5]}-{str(h['hora_fin'])[:5]})" for h in horas].index(h_del)
                    requests.delete(f"{SUPABASE_URL}/rest/v1/horas_nivel?id=eq.{horas[idx_del]['id']}", headers=headers)
                    st.success("Hora eliminada")
                    st.rerun()
        else:
            st.info(f"Sin franjas registradas para {nivel_sel}.")

    with col_form:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 9px 12px; margin-bottom: 8px;">
            <b style="color: #0F172A; font-size: 13.5px;">Agregar Franja</b>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_add_hora", clear_on_submit=True):
            orden = st.number_input("Orden de la hora:", min_value=1, max_value=20, value=len(horas) + 1, step=1)
            c1, c2 = st.columns(2)
            with c1:
                hora_inicio = st.time_input("Hora inicio:", value=time(7, 0))
            with c2:
                hora_fin = st.time_input("Hora fin:", value=time(7, 50))
            descripcion = st.text_input("Descripcion:", value=f"Hora #{orden}")

            if st.form_submit_button("Guardar Franja", type="primary", use_container_width=True):
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
# 3. DIAS LABORALES (config_horario_nivel)
# ==============================================================================
def configurar_jornada_nivel(headers=None):
    if headers is None:
        headers = get_headers()

    st.subheader("Dias Laborales y Jornada por Nivel")
    
    r_niveles = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    niveles = r_niveles.json() if r_niveles.status_code == 200 else []
    
    if not niveles:
        st.warning("No hay niveles configurados.")
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
            <b style="color: #0F172A; font-size: 13.5px;">Panorama de Jornadas</b>
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
                rot_str = "Si" if c_item.get('horario_rotativo') else "No"
            else:
                d_str = "Lun, Mar, Mie, Jue, Vie"
                rot_str = "No"
            tabla_resumen.append({"Nivel": n['nombre'], "Dias de Clase": d_str, "Rotativo": rot_str})
        st.dataframe(pd.DataFrame(tabla_resumen), use_container_width=True, height=250)

    with col_der:
        st.markdown(f"""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 9px 12px; margin-bottom: 8px;">
            <b style="color: #0F172A; font-size: 13.5px;">Parametrizar {nivel_sel}</b>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_jornada_conf"):
            dias_seleccionados = st.multiselect(
                "Dias de clase activos:",
                options=list(DIAS_SEMANA_MAP.keys()),
                format_func=lambda x: DIAS_SEMANA_MAP[x],
                default=dias_default
            )
            horario_rotativo = st.checkbox("Horario rotativo", value=rotativo_default)

            if st.form_submit_button("Guardar Configuracion", type="primary", use_container_width=True):
                payload = {
                    "nivel_id": nivel_id,
                    "dias_laborales": dias_seleccionados,
                    "horario_rotativo": horario_rotativo
                }
                if config_id:
                    requests.patch(f"{SUPABASE_URL}/rest/v1/config_horario_nivel?id=eq.{config_id}", headers=headers, json=payload)
                else:
                    requests.post(f"{SUPABASE_URL}/rest/v1/config_horario_nivel", headers=headers, json=payload)
                st.success("Configuracion guardada")
                st.rerun()


# ==============================================================================
# 4. HORARIO POR CURSO
# ==============================================================================
def configurar_horario_curso(headers=None):
    if headers is None:
        headers = get_headers()

    st.subheader("Malla Curricular por Curso")

    r_grados = requests.get(f"{SUPABASE_URL}/rest/v1/grados?order=curso.asc", headers=headers)
    grados_data = r_grados.json() if r_grados.status_code == 200 else []
    
    if grados_data:
        cursos = [g['curso'] for g in grados_data if g.get('curso')]
        map_curso_nivel = {g['curso']: g.get('nivel_id') for g in grados_data}
    else:
        cursos = ["901", "902", "903", "1001", "1002", "1003", "1101"]
        map_curso_nivel = {}

    col_sel_curso, col_sync = st.columns([1.5, 1.5])
    with col_sel_curso:
        curso_sel = st.selectbox("Selecciona el curso a gestionar:", cursos, key="curso_select_real")

    nivel_id_curso = map_curso_nivel.get(curso_sel, 1)

    r_asig = requests.get(f"{SUPABASE_URL}/rest/v1/asignacion_academica?curso=eq.{curso_sel}", headers=headers)
    asignaciones_raw = r_asig.json() if r_asig.status_code == 200 else []
    
    mapa_carga_docente = {}
    materias_disponibles = []
    for a in asignaciones_raw:
        asig_nom = str(a.get('asignatura', '')).strip().upper()
        if asig_nom and "DIRECCION" not in asig_nom:
            mapa_carga_docente[asig_nom] = str(a.get('documento_docente') or '')
            if asig_nom not in materias_disponibles:
                materias_disponibles.append(asig_nom)
    materias_disponibles.sort()

    with col_sync:
        st.write("")
        if st.button("Sincronizar Docentes de Carga Academica", use_container_width=True):
            r_clases_exist = requests.get(f"{SUPABASE_URL}/rest/v1/horario_base?curso=eq.{curso_sel}", headers=headers)
            clases_exist = r_clases_exist.json() if r_clases_exist.status_code == 200 else []
            actualizadas = 0
            for cl in clases_exist:
                asig_limpia = str(cl.get('asignatura', '')).strip().upper()
                doc_correspondiente = mapa_carga_docente.get(asig_limpia)
                if doc_correspondiente and str(cl.get('documento_docente')) != doc_correspondiente:
                    requests.patch(f"{SUPABASE_URL}/rest/v1/horario_base?id=eq.{cl['id']}", headers=headers, json={"documento_docente": doc_correspondiente})
                    actualizadas += 1
            if actualizadas > 0:
                st.success(f"Se sincronizaron {actualizadas} clases con sus docentes.")
            else:
                st.info("Todas las clases ya estaban correctamente sincronizadas.")
            st.rerun()

    url_horario = f"{SUPABASE_URL}/rest/v1/horario_base?curso=eq.{curso_sel}&order=orden_clase.asc,dia_semana.asc"
    r_horario = requests.get(url_horario, headers=headers)
    horarios_curso = r_horario.json() if r_horario.status_code == 200 else []

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

    r_docentes = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
    docentes = r_docentes.json() if r_docentes.status_code == 200 else []
    docentes_dict = {str(d['documento_docente']): f"{d.get('nombre_docente', '')} {d.get('apellidos_docente', '')}".strip() for d in docentes}

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
            min-height: 56px;
            height: auto;
            background-color: white;
            border-radius: 6px;
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
            font-size: 9.5px;
            color: #475569;
            line-height: 1.1;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 95%;
        }
        .celda-malla .sal {
            font-size: 8px;
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
            min-height: 56px;
            height: auto;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            box-sizing: border-box;
            margin-bottom: 3px;
            line-height: 1.15;
        }
    </style>
    """, unsafe_allow_html=True)

    col_malla, col_editor = st.columns([1.8, 1.1], gap="medium")

    with col_malla:
        st.markdown(f"""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 7px 12px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center;">
            <b style="color: #0F172A; font-size: 13px;">Horario Semanal: Grado {curso_sel}</b>
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
                st.markdown(f'<div class="hdr-hora"><b>#{o_num}</b><br><span style="color:#64748B;">{h_info["inicio"]}<br>{h_info["fin"]}</span></div>', unsafe_allow_html=True)
            
            for i_d, d_num in enumerate(dias_cols):
                with c_row[i_d + 1]:
                    clase = matriz_clases.get((d_num, o_num))
                    if clase:
                        doc_id = str(clase.get('documento_docente') or '')
                        doc_nom = docentes_dict.get(doc_id, '')
                        doc_corto = formatear_nombre_corto(doc_nom)
                        doc_label = f"Doc: {doc_corto}" if doc_corto else "<span style='color:#EF4444;'>Sin docente</span>"
                        salon_badge = f'<div class="sal">{clase.get("salon")}</div>' if clase.get("salon") else ''

                        st.markdown(f'''
                        <div class="celda-malla">
                            <span class="asig">{clase.get("asignatura", "?")}</span>
                            <span class="prof">{doc_label}</span>
                            {salon_badge}
                        </div>
                        ''', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="celda-malla vacia"><span style="color:#94A3B8;">-</span></div>', unsafe_allow_html=True)

    with col_editor:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 7px 12px; margin-bottom: 6px;">
            <b style="color: #0F172A; font-size: 13px;">Asignar o Editar Casilla</b>
        </div>
        """, unsafe_allow_html=True)

        c_d, c_h = st.columns(2)
        with c_d:
            dia_sel_nom = st.selectbox("Dia:", ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado"], key="dia_asignar_slot")
        with c_h:
            hora_sel_orden = st.selectbox("Hora:", [h['orden'] for h in lista_horas], format_func=lambda x: f"Hora #{x}", key="hora_asignar_slot")

        dia_num = DIAS_INVERSO[dia_sel_nom]
        h_actual = next((h for h in lista_horas if h['orden'] == hora_sel_orden), lista_horas[0])
        existente = matriz_clases.get((dia_num, hora_sel_orden))

        asig_actual = existente.get('asignatura', '') if existente else ''
        
        if materias_disponibles:
            opciones_mat = [""] + materias_disponibles + ["OTRA..."]
            idx_mat = opciones_mat.index(asig_actual) if asig_actual in opciones_mat else 0
            materia_elegida = st.selectbox("Asignatura del curso *:", opciones_mat, index=idx_mat, key="mat_select_carga")
            if materia_elegida == "OTRA...":
                asignatura_final = st.text_input("Escribe el nombre de la materia:", value=asig_actual).strip().upper()
            else:
                asignatura_final = materia_elegida
        else:
            asignatura_final = st.text_input("Asignatura *:", value=asig_actual, placeholder="Ej: FISICA, SOCIALES").strip().upper()

        docente_sugerido = mapa_carga_docente.get(asignatura_final, '')
        doc_actual = str(existente.get('documento_docente') or '') if existente else docente_sugerido
        salon_actual = existente.get('salon', '') if existente else ''

        lista_docs = [""] + list(docentes_dict.keys())
        idx_doc = lista_docs.index(doc_actual) if doc_actual in lista_docs else 0
        docente_in = st.selectbox(
            "Docente asignado:",
            options=lista_docs,
            index=idx_doc,
            format_func=lambda x: docentes_dict.get(x, "Sin docente") if x else "Ninguno",
            key="doc_select_final"
        )

        salon_in = st.text_input("Salon / Aula:", value=salon_actual, placeholder="Ej: Aula 101, Lab", key="salon_input_final")

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            btn_guardar = st.button("Guardar Casilla", type="primary", use_container_width=True)
        with col_b2:
            btn_vaciar = st.button("Vaciar Casilla", use_container_width=True)

        if btn_guardar:
            if not asignatura_final:
                st.error("Selecciona o escribe una asignatura")
            else:
                payload = {
                    "curso": curso_sel,
                    "nivel_id": nivel_id_curso,
                    "dia_semana": dia_num,
                    "orden_clase": hora_sel_orden,
                    "hora_inicio": f"{h_actual['inicio']}:00",
                    "hora_fin": f"{h_actual['fin']}:00",
                    "asignatura": asignatura_final,
                    "documento_docente": docente_in if docente_in else None,
                    "salon": salon_in.strip().upper() if salon_in else ""
                }
                if existente and existente.get('id'):
                    requests.patch(f"{SUPABASE_URL}/rest/v1/horario_base?id=eq.{existente['id']}", headers=headers, json=payload)
                else:
                    requests.post(f"{SUPABASE_URL}/rest/v1/horario_base", headers=headers, json=payload)
                
                st.success("Casilla guardada correctamente")
                st.rerun()

        if btn_vaciar:
            if existente and existente.get('id'):
                requests.delete(f"{SUPABASE_URL}/rest/v1/horario_base?id=eq.{existente['id']}", headers=headers)
                st.info("Casilla vaciada")
                st.rerun()


# ==============================================================================
# 5. GESTION DE FESTIVOS (festivos)
# ==============================================================================
def gestion_festivos(headers=None):
    if headers is None:
        headers = get_headers()

    st.subheader("Calendario Escolar y Festivos")
    
    col_sel_y, _ = st.columns([1.5, 2.5])
    with col_sel_y:
        year = st.selectbox("Ano Lectivo:", [2025, 2026, 2027], index=1, key="festivos_year")

    url_festivos = f"{SUPABASE_URL}/rest/v1/festivos?year=eq.{year}&order=fecha.asc"
    res_f = requests.get(url_festivos, headers=headers)
    festivos = res_f.json() if res_f.status_code == 200 else []

    col_izq, col_der = st.columns([1.3, 1], gap="medium")

    with col_izq:
        st.markdown(f"""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 9px 12px; margin-bottom: 8px;">
            <b style="color: #0F172A; font-size: 13.5px;">Dias No Lectivos de {year}</b>
        </div>
        """, unsafe_allow_html=True)

        if festivos:
            df = pd.DataFrame(festivos)[['fecha', 'descripcion']].rename(columns={'fecha': 'Fecha', 'descripcion': 'Motivo'})
            st.dataframe(df, use_container_width=True, height=270)

            c_del1, c_del2 = st.columns([2, 1])
            with c_del1:
                f_del_item = st.selectbox("Festivo a eliminar:", [f"{f['fecha']} ({f.get('descripcion')})" for f in festivos], label_visibility="collapsed")
            with c_del2:
                if st.button("Quitar", use_container_width=True):
                    idx_f = [f"{f['fecha']} ({f.get('descripcion')})" for f in festivos].index(f_del_item)
                    requests.delete(f"{SUPABASE_URL}/rest/v1/festivos?id=eq.{festivos[idx_f]['id']}", headers=headers)
                    st.success("Festivo eliminado")
                    st.rerun()
        else:
            st.info(f"No hay festivos registrados para {year}.")

    with col_der:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 9px 12px; margin-bottom: 8px;">
            <b style="color: #0F172A; font-size: 13.5px;">Registrar Festivo</b>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_add_festivo", clear_on_submit=True):
            fecha = st.date_input("Fecha:", key="festivo_fecha")
            descripcion = st.text_input("Motivo (Ej: Dia Civico, Semana Santa):", key="festivo_desc")

            if st.form_submit_button("Guardar Festivo", type="primary", use_container_width=True):
                if descripcion.strip():
                    data = {"fecha": str(fecha), "descripcion": descripcion.strip(), "year": fecha.year}
                    requests.post(f"{SUPABASE_URL}/rest/v1/festivos", headers=headers, json=data)
                    st.success("Festivo agregado")
                    st.rerun()


# ==============================================================================
# 6. MENU COMPLETO ADMIN HORARIOS
# ==============================================================================
def gestion_horarios_admin(data):
    st.title("Configuracion de Horarios")
    headers = get_headers()
    tabs = st.tabs(["Niveles", "Horas por Nivel", "Dias Laborales", "Asignar Materias", "Festivos"])
    
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
# 7. VISUALIZACION UNIFICADA (DOCENTE / ESTUDIANTE / ACUDIENTE)
# ==============================================================================
def mostrar_horario_unificado(horarios, titulo="Mi Horario Semanal", tipo_vista="estudiante"):
    if not horarios:
        st.info("No hay horario disponible")
        return

    headers = get_headers()
    dias = {1: "Lunes", 2: "Martes", 3: "Miercoles", 4: "Jueves", 5: "Viernes", 6: "Sabado"}

    try:
        r_docs = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
        docentes_db = r_docs.json() if r_docs.status_code == 200 else []
        map_docentes = {str(d['documento_docente']): f"{d.get('nombre_docente', '')} {d.get('apellidos_docente', '')}".strip() for d in docentes_db}
    except Exception:
        map_docentes = {}

    horas_dict = {}
    horas_orden_map = {}

    for clase in horarios:
        o_clase = clase.get('orden_clase') or 1
        h_ini = str(clase.get('hora_inicio', ''))[:5]
        h_fin = str(clase.get('hora_fin', ''))[:5]
        
        if h_ini and h_fin:
            hora_label = f"#{o_clase}<br><span style='font-size:9.5px; color:#64748B;'>{h_ini}-{h_fin}</span>"
        else:
            hora_label = f"#{o_clase}"

        if o_clase not in horas_dict:
            horas_dict[o_clase] = {dia: None for dia in dias.values()}
            horas_orden_map[o_clase] = hora_label

        try:
            dia_num = int(clase.get('dia_semana'))
        except Exception:
            dia_num = 1
        dia_nom = dias.get(dia_num, "Lunes")

        doc_doc = str(clase.get('documento_docente') or '')
        doc_nom_largo = map_docentes.get(doc_doc, '')
        doc_corto = formatear_nombre_corto(doc_nom_largo)

        horas_dict[o_clase][dia_nom] = {
            "asignatura": str(clase.get('asignatura', '?')).upper(),
            "curso": str(clase.get('curso', '')),
            "salon": str(clase.get('salon', '')).strip(),
            "docente": doc_corto
        }

    ordenes_ordenados = sorted(horas_dict.keys())
    if not ordenes_ordenados:
        st.info("No hay horario configurado")
        return

    st.markdown("""
    <style>
        .horario-celda {
            border: 1px solid #CBD5E1;
            padding: 5px 3px;
            text-align: center;
            min-height: 56px;
            height: auto;
            background-color: white;
            border-radius: 6px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            width: 100%;
            box-sizing: border-box;
            overflow: hidden;
            margin-bottom: 3px;
        }
        .horario-celda.vacia {
            background-color: #F8FAFC;
            border: 1px dashed #E2E8F0;
        }
        .
