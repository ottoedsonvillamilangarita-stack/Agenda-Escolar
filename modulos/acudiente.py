import streamlit as st
import requests
from utils import SUPABASE_URL, get_headers
from modulos.features.calificaciones import mostrar_notas_acudiente

def mostrar(data):
    st.title("👨‍👩‍👧 Panel del Acudiente")
    
    documento_acudiente = data.get('documento')
    
    st.write(f"Bienvenido, Acudiente")
    st.write(f"Documento: {documento_acudiente}")
    
    headers = get_headers()
    
    # ============================================
    # MENÚ PRINCIPAL
    # ============================================
    st.divider()
    st.subheader("📌 Funciones disponibles")
    
    opcion = st.selectbox(
        "Seleccionar función",
        [
            "👨‍👩‍👧 Mis Hijos",
            "📖 Notas de mis hijos",
            "📋 Asistencia",
            "👤 Mi Perfil"
        ]
    )
    
    st.divider()
    
    # ============================================
    # REDIRECCIÓN SEGÚN OPCIÓN
    # ============================================
    
    if opcion == "👨‍👩‍👧 Mis Hijos":
        # Mostrar lista de hijos
        url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_acudiente=eq.{documento_acudiente}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            datos = response.json()
            if datos:
                st.success(f"✅ Acudiente encontrado con {len(datos)} hijo(s)")
                
                for hijo in datos:
                    with st.expander(f"📘 {hijo.get('nombre_estudiante', 'N/A')}"):
                        st.write(f"**Nombre:** {hijo.get('nombre_estudiante', 'N/A')}")
                        st.write(f"**Apellidos:** {hijo.get('apellidos_estudiante', 'N/A')}")
                        st.write(f"**Curso:** {hijo.get('curso', 'N/A')}")
                        st.write(f"**Parentesco:** {hijo.get('parentesco', 'N/A')}")
                        st.write(f"**Teléfono:** {hijo.get('telefono_acudiente', 'N/A')}")
            else:
                st.warning("No se encontraron hijos asociados a este acudiente")
        else:
            st.error(f"Error {response.status_code}: {response.text}")
    
    elif opcion == "📖 Notas de mis hijos":
        mostrar_notas_acudiente(data)
    
    elif opcion == "📋 Asistencia":
        st.subheader("📋 Asistencia")
        st.info("🚧 Módulo en desarrollo")
    
    elif opcion == "👤 Mi Perfil":
        st.subheader("👤 Mi Perfil")
        st.info("🚧 Módulo en desarrollo")
