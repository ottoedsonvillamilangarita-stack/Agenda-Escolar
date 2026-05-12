import streamlit as st
import pandas as pd
import requests
from utils import SUPABASE_URL, get_headers

def mostrar(data):
    st.title("⚙️ Administración")
    st.write(f"Bienvenido, {data['nombre']}")
    
    # ========== CREAR LAS 3 PESTAÑAS ==========
    tab1, tab2, tab3 = st.tabs(["👥 Usuarios", "📤 Carga Masiva", "⚙️ Configuración"])
    
    # ========== TAB 1: USUARIOS ==========
    with tab1:
        st.subheader("Usuarios del Sistema")
        headers = get_headers()
        url = f"{SUPABASE_URL}/rest/v1/usuarios_login"
        response = requests.get(url, headers=headers)
        if response.status_code == 200 and response.json():
            for user in response.json():
                st.write(f"• **{user['username']}** - {user['rol']} - {user['nombre']}")
        else:
            st.info("No hay usuarios registrados")
    
    # ========== TAB 2: CARGA MASIVA ==========
    with tab2:
        st.subheader("📤 Carga Masiva de Datos")
        st.info("Sube archivos Excel para cargar estudiantes, acudientes, docentes y asignaciones.")
        
        with st.expander("📋 Ver formato esperado de los archivos"):
            st.markdown("""
            **Archivo de estudiantes (Excel):**
            - Columnas obligatorias: `nombre_estudiante`, `apellidos_estudiante`, `documento_estudiante`, `curso`, `nombre_acudiente`, `documento_acudiente`, `parentesco`, `telefono_acudiente`
            - Opcional: `email_acudiente`, `sexo_estudiante`
            
            **Archivo de asignación académica (Excel):**
            - Columnas obligatorias: `curso`, `asignatura`, `intensidad_semanal`, `nombre_docente`, `apellidos_docente`, `documento_docente`
            - Opcional: `telefono_docente`, `email_docente`
            """)
        
        col1, col2 = st.columns(2)
        
        # ===== SUBIR ESTUDIANTES =====
        with col1:
            st.subheader("📚 Estudiantes")
            archivo_est = st.file_uploader(
                "Seleccionar archivo de estudiantes (Excel)",
                type=["xlsx", "xls"],
                key="estudiantes_upload"
            )
            if archivo_est is not None:
                try:
                    df = pd.read_excel(archivo_est)
                    st.success(f"✅ {len(df)} estudiantes encontrados")
                    if st.button("🚀 Subir estudiantes", key="btn_est"):
                        with st.spinner("Procesando..."):
                            resultado = procesar_estudiantes(df)
                            st.success(resultado)
                except Exception as e:
                    st.error(f"Error: {e}")
        
        # ===== SUBIR DOCENTES Y ASIGNACIONES =====
        with col2:
            st.subheader("📚 Docentes y Asignaciones")
            archivo_doc = st.file_uploader(
                "Seleccionar archivo de docentes (Excel)",
                type=["xlsx", "xls"],
                key="docentes_upload"
            )
            if archivo_doc is not None:
                try:
                    df = pd.read_excel(archivo_doc)
                    st.success(f"✅ {len(df)} asignaciones encontradas")
                    if st.button("🚀 Subir docentes", key="btn_doc"):
                        with st.spinner("Procesando..."):
                            resultado = procesar_docentes(df)
                            st.success(resultado)
                except Exception as e:
                    st.error(f"Error: {e}")
    
    # ========== TAB 3: CONFIGURACIÓN ==========
    with tab3:
        st.subheader("Configuración General")
        st.write("**Periodos académicos:** Periodo I, II, III, IV")
        st.write("**Escala de notas:** 0 a 5")
        st.write("**Nota mínima aprobatoria:** 3.0")
        st.info("Próximamente: más opciones de configuración")


# ======================================================
# FUNCIONES DE PROCESAMIENTO
# ======================================================

def procesar_estudiantes(df):
    headers = get_headers()
    
    # Limpiar decimales
    df["documento_estudiante"] = df["documento_estudiante"].astype(str).str.split('.').str[0]
    df["documento_acudiente"] = df["documento_acudiente"].astype(str).str.split('.').str[0]
    
    estudiantes_ok = 0
    acudientes_ok = 0
    
    # 1. Insertar acudientes
    acudientes_unicos = df[["nombre_acudiente", "documento_acudiente", "telefono_acudiente", "email_acudiente"]].drop_duplicates(subset=["documento_acudiente"])
    
    for _, row in acudientes_unicos.iterrows():
        doc = str(row["documento_acudiente"])
        url = f"{SUPABASE_URL}/rest/v1/personas?documento=eq.{doc}"
        resp = requests.get(url, headers=headers)
        
        if resp.status_code == 200 and not resp.json():
            persona = {
                "nombre": row["nombre_acudiente"],
                "documento": doc,
                "telefono": str(row["telefono_acudiente"]),
                "email": row.get("email_acudiente"),
                "rol": "acudiente"
            }
            r = requests.post(f"{SUPABASE_URL}/rest/v1/personas", 
                              headers={**headers, "Content-Type": "application/json"}, 
                              json=persona)
            if r.status_code == 201:
                acudientes_ok += 1
    
    # 2. Insertar estudiantes
    for _, row in df.iterrows():
        doc_est = str(row["documento_estudiante"])
        url = f"{SUPABASE_URL}/rest/v1/personas?documento=eq.{doc_est}"
        resp = requests.get(url, headers=headers)
        
        if resp.status_code == 200 and not resp.json():
            estudiante = {
                "nombre": f"{row['nombre_estudiante']} {row['apellidos_estudiante']}",
                "documento": doc_est,
                "rol": "estudiante"
            }
            r = requests.post(f"{SUPABASE_URL}/rest/v1/personas", 
                              headers={**headers, "Content-Type": "application/json"}, 
                              json=estudiante)
            if r.status_code == 201:
                estudiantes_ok += 1
    
    return f"✅ {estudiantes_ok} estudiantes y {acudientes_ok} acudientes insertados"


def procesar_docentes(df):
    st.write("=== DIAGNÓSTICO ===")
    st.write(f"Columnas encontradas: {list(df.columns)}")
    st.write(f"Primeras filas:")
    st.dataframe(df.head())
    
    headers = get_headers()
    
    # Limpiar decimales
    if "documento_docente" in df.columns:
        df["documento_docente"] = df["documento_docente"].astype(str).str.split('.').str[0]
    else:
        return "❌ Error: No se encontró la columna 'documento_docente'"
    
    docentes_ok = 0
    
    for idx, row in df.iterrows():
        doc = str(row["documento_docente"])
        st.write(f"Procesando: {doc}")
        
        # Verificar si el docente ya existe
        url = f"{SUPABASE_URL}/rest/v1/personas?documento=eq.{doc}"
        resp = requests.get(url, headers=headers)
        
        if resp.status_code == 200:
            if resp.json():
                st.write(f"⚠️ Docente {doc} ya existe")
            else:
                # Insertar nuevo docente
                nombre_completo = f"{row['nombre_docente']} {row['apellidos_docente']}"
                docente = {
                    "nombre": nombre_completo,
                    "documento": doc,
                    "rol": "docente"
                }
                r = requests.post(f"{SUPABASE_URL}/rest/v1/personas", 
                                  headers={**headers, "Content-Type": "application/json"}, 
                                  json=docente)
                if r.status_code == 201:
                    docentes_ok += 1
                    st.write(f"✅ Docente {nombre_completo} insertado")
                else:
                    st.write(f"❌ Error al insertar: {r.text}")
        else:
            st.write(f"❌ Error de conexión: {resp.status_code}")
    
    return f"✅ {docentes_ok} docentes insertados"
