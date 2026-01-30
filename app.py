import streamlit as st
from datetime import datetime, timedelta
import time

# --- 1. CONFIGURACIÓN DE ALTO NIVEL ---
st.set_page_config(page_title="Mercado Comunidad | Tao_Creator", page_icon="🛒", layout="wide")

# --- 2. SEGURIDAD MAESTRA ---
PASSWORD_TAO = "tao"  
ADMIN_NAME = "Tao_Creator"

# --- 3. BASE DE DATOS GLOBAL (SINCRONIZADA) ---
@st.cache_resource
def obtener_db_global():
    return {
        'muro': [],               
        'chats': {},              
        'baneos_temporales': {},  
        'ojo_de_tao': [],         
        'mantenimiento': False,   
        'aviso_mantenimiento': "🛠️ El servidor se encuentra en mantenimiento técnico. Volvemos pronto.",
        'aviso_global': "",       
        'sugerencias': []
    }

db = obtener_db_global()

def registrar_actividad(usuario, accion):
    ahora = datetime.now().strftime("%H:%M:%S")
    db['ojo_de_tao'].insert(0, f"📌 [{ahora}] | 👤 {usuario}: {accion}")

# --- 4. LÓGICA DE ACCESO ---
if 'usuario' not in st.session_state:
    st.markdown("<h1 style='text-align: center; color: #e91e63;'>🛒 MERCADO COMUNIDAD</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container(border=True):
            st.subheader("👤 Identificación")
            u_in = st.text_input("Ingresá tu nombre:")
            p_in = ""
            if u_in == ADMIN_NAME:
                p_in = st.text_input("Llave Maestra:", type="password")
            
            if st.button("ACCEDER AL SISTEMA", use_container_width=True):
                ahora = datetime.now()
                
                # PRIORIDAD ADMIN
                if u_in == ADMIN_NAME and p_in == PASSWORD_TAO:
                    st.session_state.usuario = u_in
                    st.session_state.es_admin = True
                    registrar_actividad(u_in, "ACCESO ADMINISTRADOR")
                    st.rerun()
                
                # CHEQUEO BANEOS
                elif u_in in db['baneos_temporales'] and ahora < db['baneos_temporales'][u_in]:
                    st.error("🚫 Estás suspendido temporalmente.")
                
                # CHEQUEO MANTENIMIENTO
                elif db['mantenimiento']:
                    st.warning(f"🚧 {db['aviso_mantenimiento']}")
                
                # USUARIO NORMAL
                elif u_in.strip():
                    st.session_state.usuario = u_in
                    st.session_state.es_admin = False
                    registrar_actividad(u_in, "ACCESO USUARIO")
                    st.rerun()
    st.stop()

# --- 5. PANEL DE ADMINISTRADOR (SIDEBAR) ---
if st.session_state.get('es_admin'):
    with st.sidebar:
        st.error("👑 PANEL DE CONTROL")
        
        with st.expander("🚧 MANTENIMIENTO"):
            db['aviso_mantenimiento'] = st.text_area("Mensaje:", value=db['aviso_mantenimiento'])
            if st.button("🟢 ABRIR" if db['mantenimiento'] else "🔴 CERRAR", use_container_width=True):
                db['mantenimiento'] = not db['mantenimiento']
                st.rerun()
        
        with st.expander("📢 ACTUALIZACIONES"):
            db['aviso_global'] = st.text_area("Novedad:", value=db['aviso_global'])
            if st.button("Publicar Actualización"): st.rerun()
            if st.button("Borrar Aviso"): 
                db['aviso_global'] = ""
                st.rerun()

        with st.expander("🚫 BANEOS"):
            u_castigo = st.text_input("Usuario:")
            t_castigo = st.number_input("Minutos:", min_value=1, value=5)
            if st.button("Banear"):
                db['baneos_temporales'][u_castigo] = datetime.now() + timedelta(minutes=t_castigo)
                st.success("Baneado.")

        with st.expander("👁️ OJO DE TAO"):
            for log in db['ojo_de_tao'][:20]: st.caption(log)

# --- 6. INTERFAZ PRINCIPAL ---
st.markdown(f"### 👤 {st.session_state.usuario}")

if db['aviso_global']:
    st.info(f"✨ **ACTUALIZACIÓN:** {db['aviso_global']}")

if st.sidebar.button("🚪 Salir"):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

# --- 7. TABS (INCLUYENDO MIS PUBLICACIONES) ---
tabs = st.tabs(["🛒 El Muro", "📦 Mis Publicaciones", "💬 Chats", "💡 Sugerencias"])

with tabs[0]: # EL MURO
    with st.expander("➕ Publicar algo"):
        n_p = st.text_input("Producto:")
        p_p = st.number_input("Precio:", min_value=1)
        f_p = st.file_uploader("Foto:", type=['png','jpg','jpeg'])
        if st.button("Publicar Ahora"):
            if n_p and f_p:
                db['muro'].insert(0, {"id": time.time(), "n": n_p, "p": p_p, "v": st.session_state.usuario, "f": f_p})
                st.rerun()

    for i, item in enumerate(db['muro']):
        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 2, 0.5])
            with c1: st.image(item['f'])
            with c2:
                st.subheader(item['n'])
                st.write(f"💰 ${item['p']} | Vendedor: {item['v']}")
                if st.button("Chat", key=f"chat_{i}"): st.session_state.chat_activo = item['id']
            with c3:
                if st.session_state.es_admin and st.button("🗑️", key=f"del_{i}"):
                    db['muro'].pop(i); st.rerun()

with tabs[1]: # MIS PUBLICACIONES (AGREGADO)
    st.header("📦 Gestión de mis productos")
    mis_items = [x for x in db['muro'] if x['v'] == st.session_state.usuario]
    
    if not mis_items:
        st.info("Todavía no publicaste nada.")
    else:
        for idx, m in enumerate(mis_items):
            with st.container(border=True):
                col_a, col_b = st.columns([3, 1])
                col_a.write(f"**{m['n']}** - Precio: ${m['p']}")
                if col_b.button("Eliminar mi post", key=f"mi_del_{idx}"):
                    db['muro'] = [x for x in db['muro'] if x['id'] != m['id']]
                    st.rerun()

with tabs[2]: # CHATS
    st.info("Seleccioná un producto en el Muro para chatear.")

with tabs[3]: # SUGERENCIAS
    st.header("💡 Buzón para Tao_Creator")
    sug = st.text_area("Tu idea:")
    if st.button("Enviar"):
        db['sugerencias'].insert(0, {"u": st.session_state.usuario, "t": sug, "h": datetime.now().strftime("%H:%M")})
        st.success("Sugerencia enviada.")
    if st.session_state.es_admin:
        st.divider()
        for s in db['sugerencias']: st.write(f"**{s['u']}**: {s['t']}")
