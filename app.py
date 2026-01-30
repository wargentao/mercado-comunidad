import streamlit as st
from datetime import datetime, timedelta
import time
import base64

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Mercado Comunidad | Tao_Creator", page_icon="🛒", layout="wide")

# --- 2. SEGURIDAD Y CONSTANTES ---
PASSWORD_TAO = "tao"  
ADMIN_NAME = "Tao_Creator"

# --- 3. BASE DE DATOS GLOBAL (ESTRUCTURA COMPLEJA) ---
@st.cache_resource
def obtener_db_global():
    return {
        'muro': [],               
        'chats': {},              
        'baneos_temporales': {},  
        'ojo_de_tao': [],         
        'mantenimiento': False,   
        'aviso_mantenimiento': "🛠️ Servidor en optimización. Volvemos pronto.",
        'aviso_global': "",       
        'sugerencias': [],
        'metricas': {"visitas": 0, "ventas_hoy": 0}
    }

db = obtener_db_global()

def registrar_actividad(usuario, accion):
    ahora = datetime.now().strftime("%d/%m | %H:%M:%S")
    db['ojo_de_tao'].insert(0, f"📌 {ahora} | 👤 {usuario} ➜ {accion}")

# --- 4. ESTILOS CSS PERSONALIZADOS (PARA HACERLO MÁS GRANDE Y MEJOR) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { border-radius: 8px; font-weight: bold; transition: 0.3s; }
    .stButton>button:hover { transform: scale(1.02); }
    .product-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #eee;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .admin-badge {
        background-color: #880e4f;
        color: white;
        padding: 2px 8px;
        border-radius: 5px;
        font-size: 12px;
    }
    .update-banner {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-left: 5px solid #00d2ff;
    }
    </style>
""", unsafe_allow_html=True)

# --- 5. LOGO Y CABECERA ---
def mostrar_cabecera():
    st.markdown(f"""
        <div style='text-align: center; background: linear-gradient(45deg, #e91e63, #880e4f); padding: 25px; border-radius: 20px; color: white; margin-bottom: 25px;'>
            <h1 style='margin: 0; font-size: 40px;'>🛒 MERCADO COMUNIDAD</h1>
            <p style='font-size: 18px; opacity: 0.9;'>Infraestructura Sincronizada gestionada por <b>{ADMIN_NAME}</b></p>
        </div>
    """, unsafe_allow_html=True)

# --- 6. SISTEMA DE ACCESO ---
if 'usuario' not in st.session_state:
    mostrar_cabecera()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container(border=True):
            st.subheader("🔐 Acceso al Sistema")
            nombre_in = st.text_input("Identificador de Usuario:")
            
            pass_in = ""
            if nombre_in == ADMIN_NAME:
                pass_in = st.text_input("Llave Maestra de Creador:", type="password")
            
            if st.button("INICIAR SESIÓN", use_container_width=True):
                ahora = datetime.now()
                
                # Verificación de Baneo
                if nombre_in in db['baneos_temporales']:
                    fin = db['baneos_temporales'][nombre_in]
                    if ahora < fin:
                        restante = fin - ahora
                        mins, segs = divmod(restante.seconds, 60)
                        st.error(f"🚫 CUENTA SUSPENDIDA. Podrás reintentar en {mins}m {segs}s.")
                        st.stop()
                
                # Validación de Identidad
                if nombre_in == ADMIN_NAME:
                    if pass_in == PASSWORD_TAO:
                        st.session_state.usuario = nombre_in
                        st.session_state.es_admin = True
                        registrar_actividad(nombre_in, "ACCESO NIVEL CREADOR")
                        st.rerun()
                    else: st.error("❌ Llave Maestra Inválida.")
                elif db['mantenimiento']:
                    st.warning(f"🚧 MODO MANTENIMIENTO: {db['aviso_mantenimiento']}")
                elif nombre_in.strip():
                    st.session_state.usuario = nombre_in
                    st.session_state.es_admin = False
                    registrar_actividad(nombre_in, "ACCESO USUARIO")
                    st.rerun()
    st.stop()

# --- 7. PANEL DE ADMINISTRACIÓN AVANZADO ---
if st.session_state.get('es_admin'):
    with st.sidebar:
        st.markdown(f"### 👑 Master Control: {ADMIN_NAME}")
        
        with st.expander("📢 ACTUALIZACIONES DEL SISTEMA"):
            aviso = st.text_area("Mensaje de actualización:", value=db['aviso_global'])
            if st.button("Publicar para Todos"):
                db['aviso_global'] = aviso
                registrar_actividad(ADMIN_NAME, "ACTUALIZÓ BANNER GLOBAL")
                st.rerun()
            if st.button("Limpiar Banner"):
                db['aviso_global'] = ""
                st.rerun()

        with st.expander("🚧 ESTADO DEL SERVIDOR"):
            db['aviso_mantenimiento'] = st.text_area("Mensaje de cierre:", value=db['aviso_mantenimiento'])
            if st.button("🟢 ABRIR / 🔴 CERRAR MERCADO"):
                db['mantenimiento'] = not db['mantenimiento']
                st.rerun()

        with st.expander("🚫 SEGURIDAD Y BANEOS"):
            u_ban = st.text_input("Usuario objetivo:")
            m_ban = st.number_input("Tiempo (Minutos):", min_value=1, value=10)
            if st.button("APLICAR BANEO TEMPORAL"):
                db['baneos_temporales'][u_ban] = datetime.now() + timedelta(minutes=m_ban)
                registrar_actividad(ADMIN_NAME, f"SUSPENDIÓ A {u_ban}")
                st.success(f"Castigo aplicado a {u_ban}")

        with st.expander("👁️ LOGS (OJO DE TAO)"):
            if st.button("Vaciar Historial"): db['ojo_de_tao'] = []
            for log in db['ojo_de_tao'][:50]:
                st.caption(log)

# --- 8. INTERFAZ DE USUARIO FINAL ---
mostrar_cabecera()

# Banner de Actualización Estilizado
if db['aviso_global']:
    st.markdown(f"""
        <div class="update-banner">
            <b>✨ NOTA DE ACTUALIZACIÓN:</b><br>{db['aviso_global']}
        </div>
    """, unsafe_allow_html=True)

# Barra de herramientas de usuario
c_user, c_out = st.columns([0.8, 0.2])
with c_user: st.markdown(f"👤 Bienvenido, **{st.session_state.usuario}**")
with c_out: 
    if st.button("🚪 SALIR"):
        registrar_actividad(st.session_state.usuario, "SESIÓN CERRADA")
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

t1, t2, t3, t4 = st.tabs(["🛒 MURO GLOBAL", "📦 MIS PRODUCTOS", "💬 CHATS", "💡 IDEAS"])

# --- TAB 1: MURO GLOBAL ---
with t1:
    with st.expander("➕ PUBLICAR NUEVO ARTÍCULO"):
        col_n, col_p = st.columns(2)
        nombre_p = col_n.text_input("Nombre del Producto:")
        precio_p = col_p.number_input("Precio (ARS):", min_value=0)
        foto_p = st.file_uploader("Imagen del producto:", type=['png','jpg','jpeg'])
        if st.button("🚀 LANZAR AL MURO", use_container_width=True):
            if nombre_p and foto_p:
                item_id = f"{nombre_p}_{time.time()}"
                db['muro'].insert(0, {
                    "id": item_id, "nombre": nombre_p, "precio": precio_p,
                    "vendedor": st.session_state.usuario, "foto": foto_p
                })
                registrar_actividad(st.session_state.usuario, f"PUBLICÓ: {nombre_p}")
                st.rerun()

    # Grid de productos
    for i, p in enumerate(db['muro']):
        st.markdown(f"""
            <div class="product-card">
                <div style="display: flex; gap: 20px; align-items: center;">
                    <div style="flex: 1;">
                        <h3 style="margin: 0; color: #880e4f;">{p['nombre']}</h3>
                        <p style="font-size: 20px; font-weight: bold; margin: 5px 0;">💰 ARS ${p['precio']}</p>
                        <p style="color: #666;">👤 Vendedor: {p['vendedor']}</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        col_btn, col_del = st.columns([0.8, 0.2])
        if col_btn.button(f"💬 Iniciar Chat por {p['nombre']}", key=f"chat_{i}"):
            st.session_state.chat_activo = p['id']
        if st.session_state.get('es_admin'):
            if col_del.button("🗑️", key=f"del_{i}"):
                db['muro'].pop(i)
                registrar_actividad(ADMIN_NAME, f"ELIMINÓ {p['nombre']}")
                st.rerun()

# --- TAB 4: SUGERENCIAS (MODO COMPLEJO) ---
with t4:
    st.header("💡 Buzón de Desarrollo")
    sug_text = st.text_area("¿Qué funcionalidad te gustaría ver en la próxima actualización?")
    if st.button("Enviar a Tao_Creator"):
        db['sugerencias'].insert(0, {
            "u": st.session_state.usuario, "t": sug_text, "h": datetime.now().strftime("%H:%M")
        })
        st.success("Sugerencia registrada en la base de datos.")
    
    if st.session_state.get('es_admin'):
        st.divider()
        st.subheader("🕵️ Sugerencias de Usuarios")
        for s in db['sugerencias']:
            st.info(f"**{s['u']}** [{s['h']}]: {s['t']}")
