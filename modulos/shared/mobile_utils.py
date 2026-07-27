import streamlit as st

def es_movil():
    """Detecta si el usuario está en dispositivo móvil"""
    try:
        user_agent = st.context.headers.get("User-Agent", "").lower()
        dispositivos = ["android", "iphone", "ipad", "mobile", "phone", "blackberry", "windows phone"]
        return any(device in user_agent for device in dispositivos)
    except:
        return False

def aplicar_css_movil():
    """Aplica CSS para mejorar experiencia en móvil"""
    st.markdown("""
    <style>
        /* Aumentar tamaño de texto general */
        p, li, div, span, .stMarkdown, .stTextInput, .stSelectbox {
            font-size: 16px !important;
        }
        
        /* Botones más grandes y táctiles */
        button {
            padding: 12px !important;
            margin: 8px 0 !important;
            font-size: 16px !important;
            min-height: 48px !important;
        }
        
        /* Inputs más grandes */
        input, textarea, select {
            font-size: 16px !important;
            padding: 10px !important;
            min-height: 44px !important;
        }
        
        /* Tarjetas para listas */
        .mobile-card {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 15px;
            margin: 10px 0;
            border: 1px solid #e9ecef;
        }
        
        /* Espaciado general */
        .stApp {
            padding: 10px !important;
        }
        
        /* Tablas responsivas */
        .stDataFrame {
            overflow-x: auto !important;
        }
        
        /* Títulos más grandes */
        h1 {
            font-size: 24px !important;
        }
        h2 {
            font-size: 20px !important;
        }
        h3 {
            font-size: 18px !important;
        }
    </style>
    """, unsafe_allow_html=True)

def menu_responsivo(opciones, titulo="Menú", key="menu"):
    """
    Muestra un menú adaptativo:
    - En móvil: selectbox
    - En escritorio: botones horizontales
    Retorna la opción seleccionada
    """
    if es_movil():
        return st.selectbox(titulo, opciones, key=key)
    else:
        cols = st.columns(len(opciones))
        for idx, opcion in enumerate(opciones):
            with cols[idx]:
                if st.button(opcion, use_container_width=True, key=f"{key}_{idx}"):
                    return opcion
        return opciones[0]

def mostrar_tarjeta(titulo, contenido, icono=None):
    """Muestra una tarjeta optimizada para móvil"""
    if icono:
        titulo = f"{icono} {titulo}"
    with st.container():
        st.markdown(f"""
        <div class="mobile-card">
            <strong>{titulo}</strong><br>
            {contenido}
        </div>
        """, unsafe_allow_html=True)

def tabla_responsiva(df, columnas_mostrar):
    """
    Muestra tabla responsiva:
    - En móvil: tarjetas
    - En escritorio: dataframe
    """
    if es_movil():
        for idx, row in df.iterrows():
            contenido = "<br>".join([f"<strong>{col}:</strong> {row.get(col, 'N/A')}" for col in columnas_mostrar])
            mostrar_tarjeta(f"Registro {idx+1}", contenido)
    else:
        st.dataframe(df[columnas_mostrar], use_container_width=True)
