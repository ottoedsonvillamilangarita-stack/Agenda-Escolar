# ============================================
# admin.py - VERSIÓN COMPLETA MEJORADA
# ============================================

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, time
from typing import Dict, List, Optional, Any
import logging
from utils import SUPABASE_URL, get_headers

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================
# CONSTANTES
# ============================================
CURSOS = ["901", "902", "903", "1001", "1002", "1003", "1101"]
DIAS_SEMANA = {1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves", 5: "Viernes", 6: "Sábado"}
PARENTESCOS = ["", "Padre", "Madre", "Tío", "Tía", "Abuelo", "Abuela", "Otro"]
SEXOS = ["", "Masculino", "Femenino"]
TIPOS_CONTRATO = ["", "Planta", "Contrato", "Cátedra", "Ocasional"]
AÑO_ACTUAL = datetime.now().year

# ============================================
# CLASE BASE PARA GESTIÓN DE SUPABASE
# ============================================
class SupabaseManager:
    """Manejador centralizado para operaciones con Supabase"""
    
    def __init__(self):
        self.headers = get_headers()
        self.base_url = SUPABASE_URL
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                     params: Optional[Dict] = None) -> Dict[str, Any]:
        """Realiza una solicitud HTTP a Supabase con manejo de errores"""
        try:
            url = f"{self.base_url}/rest/v1/{endpoint}"
            
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, params=params)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == "PATCH":
                response = requests.patch(url, headers=self.headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Método HTTP no soportado: {method}")
            
            if response.status_code in [200, 201, 204]:
                return {"success": True, "data": response.json() if response.content else [], "status": response.status_code}
            else:
                logger.error(f"Error {response.status_code}: {response.text}")
                return {"success": False, "error": f"Error {response.status_code}: {response.text}", "status": response.status_code}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión: {str(e)}")
            return {"success": False, "error": f"Error de conexión: {str(e)}"}
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            return {"success": False, "error": f"Error inesperado: {str(e)}"}
    
    def get(self, table: str, filters: Optional[Dict] = None) -> List[Dict]:
        """Obtiene registros de una tabla"""
        params = {}
        if filters:
            for key, value in filters.items():
                if isinstance(value, list):
                    params[key] = f"in.({','.join(map(str, value))})"
                else:
                    params[key] = f"eq.{value}"
        
        result = self._make_request("GET", table, params=params)
        return result.get("data", []) if result.get("success") else []
    
    def get_all(self, table: str) -> List[Dict]:
        """Obtiene todos los registros de una tabla"""
        return self.get(table)
    
    def create(self, table: str, data: Dict) -> bool:
        """Crea un nuevo registro"""
        result = self._make_request("POST", table, data=data)
        return result.get("success", False)
    
    def update(self, table: str, data: Dict, filters: Dict) -> bool:
        """Actualiza registros existentes"""
        filter_str = "&".join([f"{k}=eq.{v}" for k, v in filters.items()])
        endpoint = f"{table}?{filter_str}"
        result = self._make_request("PATCH", endpoint, data=data)
        return result.get("success", False)
    
    def delete(self, table: str, filters: Dict) -> bool:
        """Elimina registros"""
        filter_str = "&".join([f"{k}=eq.{v}" for k, v in filters.items()])
        endpoint = f"{table}?{filter_str}"
        result = self._make_request("DELETE", endpoint)
        return result.get("success", False)

# ============================================
# FUNCIONES AUXILIARES
# ============================================
def crear_usuario(db: SupabaseManager, username: str, password: str, rol: str, documento: str):
    """Crea un usuario en el sistema"""
    user_data = {
        "username": username,
        "password_hash": password,
        "rol": rol,
        "documento": documento,
        "roles": [rol]
    }
    return db.create("usuarios_login", user_data)

# ============================================
# CLASE DE GESTIÓN DE ESTUDIANTES
# ============================================
class StudentManager:
    """Gestiona operaciones relacionadas con estudiantes"""
    
    def __init__(self, db: SupabaseManager):
        self.db = db
    
    def get_all_students(self) -> List[Dict]:
        """Obtiene todos los estudiantes"""
        return self.db.get_all("estudiantes")
    
    def get_student_by_document(self, documento: str) -> Optional[Dict]:
        """Obtiene un estudiante por su documento"""
        result = self.db.get("estudiantes", {"documento_estudiante": documento})
        return result[0] if result else None
    
    def create_student(self, data: Dict) -> bool:
        """Crea un nuevo estudiante"""
        if self.get_student_by_document(data.get("documento_estudiante")):
            return False
        return self.db.create("estudiantes", data)
    
    def update_student(self, documento: str, data: Dict) -> bool:
        """Actualiza un estudiante existente"""
        return self.db.update("estudiantes", data, {"documento_estudiante": documento})
    
    def get_guardians(self, documento_estudiante: str) -> List[Dict]:
        """Obtiene los acudientes de un estudiante"""
        return self.db.get("estudiante_acudiente", {"documento_estudiante": documento_estudiante})
    
    def add_guardian(self, data: Dict) -> bool:
        """Agrega un acudiente a un estudiante"""
        return self.db.create("estudiante_acudiente", data)
    
    def update_guardian(self, guardian_id: int, data: Dict) -> bool:
        """Actualiza un acudiente"""
        return self.db.update("estudiante_acudiente", data, {"id": guardian_id})
    
    def delete_guardian(self, guardian_id: int) -> bool:
        """Elimina un acudiente"""
        return self.db.delete("estudiante_acudiente", {"id": guardian_id})

# ============================================
# CLASE DE GESTIÓN DE DOCENTES
# ============================================
class TeacherManager:
    """Gestiona operaciones relacionadas con docentes"""
    
    def __init__(self, db: SupabaseManager):
        self.db = db
    
    def get_all_teachers(self) -> List[Dict]:
        """Obtiene todos los docentes"""
        return self.db.get_all("docentes")
    
    def get_teacher_by_document(self, documento: str) -> Optional[Dict]:
        """Obtiene un docente por su documento"""
        result = self.db.get("docentes", {"documento_docente": documento})
        return result[0] if result else None
    
    def create_teacher(self, data: Dict) -> bool:
        """Crea un nuevo docente"""
        if self.get_teacher_by_document(data.get("documento_docente")):
            return False
        return self.db.create("docentes", data)
    
    def update_teacher(self, documento: str, data: Dict) -> bool:
        """Actualiza un docente existente"""
        return self.db.update("docentes", data, {"documento_docente": documento})

# ============================================
# FUNCIÓN PRINCIPAL mostrar()
# ============================================
def mostrar(data):
    """Función principal del panel de administrador"""
    st.title("🛡️ Panel de Administrador")
    st.write(f"Bienvenido, {data.get('username', 'Admin')}")
    
    # Inicializar sesión
    if "admin_seccion" not in st.session_state:
        st.session_state.admin_seccion = "dashboard"
    
    # Menú de navegación
    menu_items = [
        ("📊 Dashboard", "dashboard"),
        ("👨‍🎓 Estudiantes", "estudiantes"),
        ("👨‍👩‍👧 Acudientes", "acudientes"),
        ("👨‍🏫 Docentes", "docentes"),
        ("📚 Asignación", "asignacion"),
        ("⚙️ Sistema", "sistema")
    ]
    
    cols = st.columns(len(menu_items))
    for idx, (label, key) in enumerate(menu_items):
        with cols[idx]:
            if st.button(
                label,
                use_container_width=True,
                type="primary" if st.session_state.admin_seccion == key else "secondary"
            ):
                st.session_state.admin_seccion = key
                st.rerun()
    
    st.divider()
    
    # Redirigir a la sección correspondiente
    secciones = {
        "dashboard": mostrar_dashboard,
        "estudiantes": gestion_estudiantes,
        "acudientes": gestion_acudientes,
        "docentes": gestion_docentes,
        "asignacion": mostrar_asignacion,
        "sistema": mostrar_sistema
    }
    
    secciones.get(st.session_state.admin_seccion, mostrar_dashboard)()

# ============================================
# DASHBOARD
# ============================================
def mostrar_dashboard():
    """Muestra el dashboard con estadísticas generales"""
    st.subheader("📊 Dashboard General")
    
    db = SupabaseManager()
    
    # Obtener estadísticas
    estudiantes = db.get_all("estudiantes")
    docentes = db.get_all("docentes")
    
    total_estudiantes = len(estudiantes)
    total_docentes = len(set([d.get('documento_docente') for d in docentes if d.get('documento_docente')]))
    
    # Mostrar métricas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👨‍🎓 Estudiantes", total_estudiantes)
    col2.metric("👨‍🏫 Docentes", total_docentes)
    col3.metric("📚 Cursos", len(set([e.get('curso') for e in estudiantes if e.get('curso')])))
    col4.metric("📅 Año Lectivo", AÑO_ACTUAL)
    
    # Información adicional
    with st.expander("📊 Detalles adicionales"):
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Distribución por curso:**")
            cursos = {}
            for e in estudiantes:
                curso = e.get('curso', 'Sin curso')
                cursos[curso] = cursos.get(curso, 0) + 1
            for curso, count in sorted(cursos.items()):
                st.write(f"- {curso}: {count} estudiantes")
        
        with col2:
            st.write("**Información general:**")
            st.write(f"- Total de estudiantes: {total_estudiantes}")
            st.write(f"- Total de docentes: {total_docentes}")
            st.write(f"- Total de cursos: {len(cursos)}")
            if len(cursos) > 0:
                st.write(f"- Promedio por curso: {total_estudiantes / len(cursos):.1f}")

# ============================================
# GESTIÓN DE ESTUDIANTES
# ============================================
def gestion_estudiantes():
    """Gestión completa de estudiantes"""
    st.subheader("👨‍🎓 Gestión de Estudiantes")
    
    db = SupabaseManager()
    student_manager = StudentManager(db)
    
    tab1, tab2, tab3 = st.tabs(["📋 Lista de Estudiantes", "➕ Nuevo Estudiante", "✏️ Editar Estudiante"])
    
    with tab1:
        mostrar_lista_estudiantes(student_manager)
    
    with tab2:
        mostrar_formulario_nuevo_estudiante(student_manager, db)
    
    with tab3:
        mostrar_formulario_editar_estudiante(student_manager, db)

def mostrar_lista_estudiantes(student_manager: StudentManager):
    """Muestra la lista de estudiantes"""
    try:
        estudiantes = student_manager.get_all_students()
        if estudiantes:
            df = pd.DataFrame(estudiantes)
            # Renombrar columnas para mejor visualización
            column_mapping = {
                'nombre_estudiante': 'Nombre',
                'apellidos_estudiante': 'Apellidos',
                'documento_estudiante': 'Documento',
                'curso': 'Curso',
                'telefono_estudiante': 'Teléfono',
                'email_estudiante': 'Email'
            }
            df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
            
            st.dataframe(df, use_container_width=True)
            st.caption(f"Total: {len(estudiantes)} estudiantes")
        else:
            st.info("No hay estudiantes registrados")
    except Exception as e:
        st.error(f"Error al cargar estudiantes: {str(e)}")

def mostrar_formulario_nuevo_estudiante(student_manager: StudentManager, db: SupabaseManager):
    """Muestra el formulario para crear un nuevo estudiante"""
    st.write("**Registrar nuevo estudiante**")
    
    with st.form("nuevo_estudiante", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Datos personales**")
            nombre = st.text_input("Nombre *")
            apellidos = st.text_input("Apellidos *")
            documento = st.text_input("Documento de identidad *")
            curso = st.selectbox("Curso *", CURSOS)
            telefono = st.text_input("Teléfono")
            email = st.text_input("Email")
            direccion = st.text_input("Dirección")
        
        with col2:
            st.markdown("**Datos del acudiente**")
            nombre_acudiente = st.text_input("Nombre del acudiente *")
            documento_acudiente = st.text_input("Documento del acudiente *")
            parentesco = st.selectbox("Parentesco", PARENTESCOS)
            telefono_acudiente = st.text_input("Teléfono del acudiente")
            email_acudiente = st.text_input("Email del acudiente")
            direccion_acudiente = st.text_input("Dirección del acudiente")
        
        if st.form_submit_button("💾 Registrar Estudiante", type="primary"):
            # Validaciones
            if not all([nombre, apellidos, documento, curso, nombre_acudiente, documento_acudiente]):
                st.error("❌ Completa todos los campos obligatorios (*)")
                return
            
            # Verificar si el estudiante ya existe
            if student_manager.get_student_by_document(documento):
                st.error(f"❌ Ya existe un estudiante con el documento {documento}")
                return
            
            # Crear estudiante
            data_estudiante = {
                "nombre_estudiante": nombre.strip(),
                "apellidos_estudiante": apellidos.strip(),
                "documento_estudiante": documento.strip(),
                "curso": curso,
                "telefono_estudiante": telefono.strip() if telefono else None,
                "email_estudiante": email.strip() if email else None,
                "direccion_estudiante": direccion.strip() if direccion else None
            }
            
            if student_manager.create_student(data_estudiante):
                # Crear usuario para el estudiante
                crear_usuario(db, documento, "demo2026", "estudiante", documento)
                
                # Crear acudiente
                data_acudiente = {
                    "documento_estudiante": documento,
                    "documento_acudiente": documento_acudiente.strip(),
                    "nombre_acudiente": nombre_acudiente.strip(),
                    "parentesco": parentesco if parentesco else None,
                    "telefono_acudiente": telefono_acudiente.strip() if telefono_acudiente else None,
                    "email_acudiente": email_acudiente.strip() if email_acudiente else None,
                    "direccion_acudiente": direccion_acudiente.strip() if direccion_acudiente else None,
                    "es_principal": True
                }
                student_manager.add_guardian(data_acudiente)
                
                # Crear usuario para el acudiente
                crear_usuario(db, documento_acudiente.strip(), "demo2026", "acudiente", documento_acudiente.strip())
                
                st.success(f"✅ Estudiante {nombre} {apellidos} registrado exitosamente")
                st.info(f"🔑 Usuario estudiante: {documento} | Contraseña: demo2026")
                st.info(f"🔑 Usuario acudiente: {documento_acudiente} | Contraseña: demo2026")
                st.balloons()
            else:
                st.error("❌ Error al registrar el estudiante")

def mostrar_formulario_editar_estudiante(student_manager: StudentManager, db: SupabaseManager):
    """Muestra el formulario para editar un estudiante"""
    st.write("**Editar estudiante existente**")
    
    documento_buscar = st.text_input("Documento de identidad del estudiante", key="buscar_estudiante_editar")
    
    if not documento_buscar:
        return
    
    estudiante = student_manager.get_student_by_document(documento_buscar)
    if not estudiante:
        st.warning("No se encontró un estudiante con ese documento")
        return
    
    acudientes = student_manager.get_guardians(documento_buscar)
    
    with st.form("editar_estudiante_completo"):
        st.success(f"Editando: {estudiante.get('nombre_estudiante', '')} {estudiante.get('apellidos_estudiante', '')}")
        
        # Datos personales
        st.markdown("### Datos personales")
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre", value=estudiante.get('nombre_estudiante', ''))
            apellidos = st.text_input("Apellidos", value=estudiante.get('apellidos_estudiante', ''))
            st.text_input("Documento", value=estudiante.get('documento_estudiante', ''), disabled=True)
            curso = st.selectbox("Curso", CURSOS, index=CURSOS.index(estudiante.get('curso', '901')))
        with col2:
            telefono = st.text_input("Teléfono", value=estudiante.get('telefono_estudiante', ''))
            email = st.text_input("Email", value=estudiante.get('email_estudiante', ''))
            direccion = st.text_input("Dirección", value=estudiante.get('direccion_estudiante', ''))
        
        st.divider()
        
        # Acudientes
        st.markdown("### Acudientes")
        for idx, acud in enumerate(acudientes):
            with st.container():
                st.markdown(f"**Acudiente {idx + 1}**")
                col1, col2 = st.columns(2)
                with col1:
                    nombre_acud = st.text_input("Nombre", value=acud.get('nombre_acudiente', ''), key=f"acud_nombre_{idx}")
                    doc_acud = st.text_input("Documento", value=acud.get('documento_acudiente', ''), key=f"acud_doc_{idx}")
                    parentesco_acud = st.selectbox("Parentesco", PARENTESCOS, 
                                                  index=PARENTESCOS.index(acud.get('parentesco', '')), 
                                                  key=f"acud_parentesco_{idx}")
                with col2:
                    telefono_acud = st.text_input("Teléfono", value=acud.get('telefono_acudiente', ''), key=f"acud_telefono_{idx}")
                    email_acud = st.text_input("Email", value=acud.get('email_acudiente', ''), key=f"acud_email_{idx}")
                    direccion_acud = st.text_input("Dirección", value=acud.get('direccion_acudiente', ''), key=f"acud_direccion_{idx}")
                    es_principal = st.checkbox("Acudiente principal", value=acud.get('es_principal', False), key=f"acud_principal_{idx}")
                
                if st.button(f"🗑️ Eliminar acudiente {idx + 1}", key=f"eliminar_acud_{idx}"):
                    student_manager.delete_guardian(acud['id'])
                    st.success("Acudiente eliminado")
                    st.rerun()
                st.divider()
        
        # Agregar acudiente
        with st.expander("➕ Agregar otro acudiente"):
            col1, col2 = st.columns(2)
            with col1:
                nuevo_nombre = st.text_input("Nombre", key="nuevo_acud_nombre")
                nuevo_doc = st.text_input("Documento", key="nuevo_acud_doc")
                nuevo_parentesco = st.selectbox("Parentesco", PARENTESCOS, key="nuevo_acud_parentesco")
            with col2:
                nuevo_telefono = st.text_input("Teléfono", key="nuevo_acud_telefono")
                nuevo_email = st.text_input("Email", key="nuevo_acud_email")
                nuevo_direccion = st.text_input("Dirección", key="nuevo_acud_direccion")
            
            if st.button("Agregar acudiente", key="btn_agregar_acud"):
                if nuevo_nombre and nuevo_doc:
                    new_acud_data = {
                        "documento_estudiante": documento_buscar,
                        "documento_acudiente": nuevo_doc.strip(),
                        "nombre_acudiente": nuevo_nombre.strip(),
                        "parentesco": nuevo_parentesco if nuevo_parentesco else None,
                        "telefono_acudiente": nuevo_telefono.strip() if nuevo_telefono else None,
                        "email_acudiente": nuevo_email.strip() if nuevo_email else None,
                        "direccion_acudiente": nuevo_direccion.strip() if nuevo_direccion else None,
                        "es_principal": False
                    }
                    if student_manager.add_guardian(new_acud_data):
                        # Crear usuario si no existe
                        if not db.get("usuarios_login", {"username": nuevo_doc.strip()}):
                            crear_usuario(db, nuevo_doc.strip(), "demo2026", "acudiente", nuevo_doc.strip())
                        st.success("Acudiente agregado")
                        st.rerun()
                    else:
                        st.error("Error al agregar acudiente")
        
        if st.form_submit_button("💾 Guardar todos los cambios", type="primary"):
            # Actualizar estudiante
            data_update = {
                "nombre_estudiante": nombre.strip(),
                "apellidos_estudiante": apellidos.strip(),
                "curso": curso,
                "telefono_estudiante": telefono.strip() if telefono else None,
                "email_estudiante": email.strip() if email else None,
                "direccion_estudiante": direccion.strip() if direccion else None
            }
            student_manager.update_student(documento_buscar, data_update)
            
            # Actualizar acudientes
            for idx, acud in enumerate(acudientes):
                nombre_acud = st.session_state.get(f"acud_nombre_{idx}", acud.get('nombre_acudiente', ''))
                doc_acud = st.session_state.get(f"acud_doc_{idx}", acud.get('documento_acudiente', ''))
                parentesco_acud = st.session_state.get(f"acud_parentesco_{idx}", acud.get('parentesco', ''))
                telefono_acud = st.session_state.get(f"acud_telefono_{idx}", acud.get('telefono_acudiente', ''))
                email_acud = st.session_state.get(f"acud_email_{idx}", acud.get('email_acudiente', ''))
                direccion_acud = st.session_state.get(f"acud_direccion_{idx}", acud.get('direccion_acudiente', ''))
                es_principal = st.session_state.get(f"acud_principal_{idx}", acud.get('es_principal', False))
                
                if nombre_acud and doc_acud:
                    acud_data = {
                        "nombre_acudiente": nombre_acud.strip(),
                        "documento_acudiente": doc_acud.strip(),
                        "parentesco": parentesco_acud if parentesco_acud else None,
                        "telefono_acudiente": telefono_acud.strip() if telefono_acud else None,
                        "email_acudiente": email_acud.strip() if email_acud else None,
                        "direccion_acudiente": direccion_acud.strip() if direccion_acud else None,
                        "es_principal": es_principal
                    }
                    student_manager.update_guardian(acud['id'], acud_data)
            
            st.success("✅ Estudiante actualizado exitosamente")
            st.balloons()
            st.rerun()

# ============================================
# GESTIÓN DE ACUDIENTES
# ============================================
def gestion_acudientes():
    """Gestión completa de acudientes"""
    st.subheader("👨‍👩‍👧 Gestión de Acudientes")
    
    db = SupabaseManager()
    student_manager = StudentManager(db)
    
    tab1, tab2 = st.tabs(["📋 Lista de Acudientes", "✏️ Editar Acudiente"])
    
    with tab1:
        mostrar_lista_acudientes(student_manager)
    
    with tab2:
        mostrar_formulario_editar_acudiente(student_manager)

def mostrar_lista_acudientes(student_manager: StudentManager):
    """Muestra la lista de acudientes"""
    try:
        acudientes_rel = student_manager.db.get_all("estudiante_acudiente")
        
        if not acudientes_rel:
            st.info("No hay acudientes registrados")
            return
        
        # Agrupar acudientes por documento
        acudientes_dict = {}
        for rel in acudientes_rel:
            doc_acud = rel.get('documento_acudiente')
            if doc_acud and doc_acud not in acudientes_dict:
                # Obtener datos del estudiante
                estudiante = student_manager.get_student_by_document(rel.get('documento_estudiante'))
                nombre_hijo = estudiante.get('nombre_estudiante') if estudiante else "Desconocido"
                
                acudientes_dict[doc_acud] = {
                    "nombre": rel.get('nombre_acudiente'),
                    "documento": doc_acud,
                    "telefono": rel.get('telefono_acudiente'),
                    "email": rel.get('email_acudiente'),
                    "direccion": rel.get('direccion_acudiente'),
                    "hijos": [nombre_hijo]
                }
            elif doc_acud:
                # Agregar otro hijo
                estudiante = student_manager.get_student_by_document(rel.get('documento_estudiante'))
                nombre_hijo = estudiante.get('nombre_estudiante') if estudiante else "Desconocido"
                if nombre_hijo not in acudientes_dict[doc_acud]["hijos"]:
                    acudientes_dict[doc_acud]["hijos"].append(nombre_hijo)
        
        if acudientes_dict:
            df = pd.DataFrame([{
                "Nombre": v["nombre"],
                "Documento": v["documento"],
                "Teléfono": v["telefono"],
                "Email": v["email"],
                "Dirección": v.get("direccion", ""),
                "Hijos": ", ".join(v["hijos"])
            } for v in acudientes_dict.values()])
            st.dataframe(df, use_container_width=True)
            st.caption(f"Total: {len(acudientes_dict)} acudientes")
    except Exception as e:
        st.error(f"Error al cargar acudientes: {str(e)}")

def mostrar_formulario_editar_acudiente(student_manager: StudentManager):
    """Muestra el formulario para editar un acudiente"""
    st.write("**Buscar acudiente por documento**")
    doc_buscar = st.text_input("Documento del acudiente", key="buscar_acudiente")
    
    if not doc_buscar:
        return
    
    acudientes = student_manager.db.get("estudiante_acudiente", {"documento_acudiente": doc_buscar})
    
    if not acudientes:
        st.warning("No se encontró un acudiente con ese documento")
        return
    
    acudiente = acudientes[0]
    
    with st.form("editar_acudiente"):
        st.success(f"Editando acudiente: {acudiente.get('nombre_acudiente', '')}")
        
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre", value=acudiente.get('nombre_acudiente', ''))
            st.text_input("Documento", value=acudiente.get('documento_acudiente', ''), disabled=True)
            parentesco = st.selectbox("Parentesco", PARENTESCOS, 
                                     index=PARENTESCOS.index(acudiente.get('parentesco', '')))
        with col2:
            telefono = st.text_input("Teléfono", value=acudiente.get('telefono_acudiente', ''))
            email = st.text_input("Email", value=acudiente.get('email_acudiente', ''))
            direccion = st.text_input("Dirección", value=acudiente.get('direccion_acudiente', ''))
        
        st.write("**Hijos asociados:**")
        for acud in acudientes:
            estudiante = student_manager.get_student_by_document(acud.get('documento_estudiante'))
            if estudiante:
                st.write(f"- {estudiante.get('nombre_estudiante')} ({estudiante.get('curso')})")
        
        if st.form_submit_button("💾 Guardar Cambios", type="primary"):
            for acud in acudientes:
                update_data = {
                    "nombre_acudiente": nombre.strip(),
                    "parentesco": parentesco if parentesco else None,
                    "telefono_acudiente": telefono.strip() if telefono else None,
                    "email_acudiente": email.strip() if email else None,
                    "direccion_acudiente": direccion.strip() if direccion else None
                }
                student_manager.update_guardian(acud['id'], update_data)
            
            st.success("✅ Acudiente actualizado exitosamente")
            st.rerun()

# ============================================
# GESTIÓN DE DOCENTES
# ============================================
def gestion_docentes():
    """Gestión completa de docentes"""
    st.subheader("👨‍🏫 Gestión de Docentes")
    
    db = SupabaseManager()
    teacher_manager = TeacherManager(db)
    
    tab1, tab2, tab3 = st.tabs(["📋 Lista de Docentes", "➕ Nuevo Docente", "✏️ Editar Docente"])
    
    with tab1:
        mostrar_lista_docentes(teacher_manager)
    
    with tab2:
        mostrar_formulario_nuevo_docente(teacher_manager, db)
    
    with tab3:
        mostrar_formulario_editar_docente(teacher_manager)

def mostrar_lista_docentes(teacher_manager: TeacherManager):
    """Muestra la lista de docentes"""
    try:
        docentes = teacher_manager.get_all_teachers()
        if docentes:
            df = pd.DataFrame(docentes)
            # Renombrar columnas para mejor visualización
            column_mapping = {
                'nombre_docente': 'Nombre',
                'apellidos_docente': 'Apellidos',
                'documento_docente': 'Documento',
                'telefono_docente': 'Teléfono',
                'email_docente': 'Email',
                'titulo': 'Título',
                'tipo_contrato': 'Contrato'
            }
            df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
            
            st.dataframe(df, use_container_width=True)
            st.caption(f"Total: {len(docentes)} docentes")
        else:
            st.info("No hay docentes registrados")
    except Exception as e:
        st.error(f"Error al cargar docentes: {str(e)}")

def mostrar_formulario_nuevo_docente(teacher_manager: TeacherManager, db: SupabaseManager):
    """Muestra el formulario para crear un nuevo docente"""
    st.write("**Registrar nuevo docente**")
    
    with st.form("nuevo_docente", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Datos personales**")
            nombre = st.text_input("Nombre *")
            apellidos = st.text_input("Apellidos *")
            documento = st.text_input("Documento de identidad *")
            fecha_nacimiento = st.date_input("Fecha de nacimiento", value=None)
            sexo = st.selectbox("Sexo", SEXOS)
            direccion = st.text_input("Dirección")
        with col2:
            st.markdown("**Datos profesionales**")
            telefono = st.text_input("Teléfono")
            email = st.text_input("Email")
            titulo = st.text_input("Título profesional")
            especializacion = st.text_input("Especialización")
            tipo_contrato = st.selectbox("Tipo de contrato", TIPOS_CONTRATO)
            fecha_ingreso = st.date_input("Fecha de ingreso", value=None)
            observaciones = st.text_area("Observaciones", height=68)
        
        if st.form_submit_button("💾 Registrar Docente", type="primary"):
            if not all([nombre, apellidos, documento]):
                st.error("❌ Completa todos los campos obligatorios (*)")
                return
            
            if teacher_manager.get_teacher_by_document(documento):
                st.error(f"❌ Ya existe un docente con el documento {documento}")
                return
            
            data = {
                "nombre_docente": nombre.strip(),
                "apellidos_docente": apellidos.strip(),
                "documento_docente": documento.strip(),
                "fecha_nacimiento": str(fecha_nacimiento) if fecha_nacimiento else None,
                "sexo_docente": sexo if sexo else None,
                "direccion_docente": direccion.strip() if direccion else None,
                "
