import streamlit as st
import requests
from modulos.utils import SUPABASE_URL, get_headers
import json  # Añade esta línea

def mostrar():
    st.title("📚 Plataforma Escolar")
    st.subheader("Iniciar Sesión")
    
    if "recover_mode" not in st.session_state:
        st.session_state.recover_mode = False
    
    if not st.session_state.recover_mode:
        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Ingresar", use_container_width=True):
                url = f"{SUPABASE_URL}/rest/v1/usuarios_login?username=eq.{usuario}"
                headers = get_headers()
                response = requests.get(url, headers=headers)
                
                # --- CÓDIGO DE DEPURACIÓN ---
                st.write("📡 URL:", url)
                st.write("🔍 Status:", response.status_code)
                st.write("📦 Datos recibidos:", response.json() if response.status_code == 200 else "Error")
                # ----------------------------
                
                if response.status_code == 200:
                    datos = response.json()
                    if datos:
                        st.write("🔑 Password en BD:", datos[0].get("password_hash"))
                        st.write("🔑 Password ingresada:", password)
                        if datos[0].get("password_hash") == password:
                            user_data = datos[0]
                            st.session_state.logged_in = True
                            st.session_state.usuario = usuario
                            st.session_state.user_data = user_data
                            st.rerun()
                        else:
                            st.error("❌ Usuario o contraseña incorrectos")
                    else:
                        st.error("❌ Usuario no encontrado")
                else:
                    st.error("❌ Error de conexión")
        
        with col2:
            if st.button("¿Olvidaste tu contraseña?", use_container_width=True):
                st.session_state.recover_mode = True
                st.rerun()
        
        st.divider()
        st.caption("Usuarios: 4303389656, admin")
        st.caption("Contraseña: demo2026")
    
    else:
        st.subheader("🔐 Recuperar Contraseña")
        
        usuario_rec = st.text_input("Usuario")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Enviar instrucciones", use_container_width=True):
                url = f"{SUPABASE_URL}/rest/v1/usuarios_login?username=eq.{usuario_rec}"
                headers = get_headers()
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200 and response.json():
                    user_data = response.json()[0]
                    st.success(f"✅ Usuario encontrado. Tu contraseña es: {user_data['password_hash']}")
                else:
                    st.error("❌ Usuario no encontrado")
        
        with col2:
            if st.button("Volver al inicio", use_container_width=True):
                st.session_state.recover_mode = False
                st.rerun()
