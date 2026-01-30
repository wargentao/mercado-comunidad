import streamlit as st
from datetime import datetime, timedelta
import time
import pandas as pd

# --- 1. CONFIGURACIÓN ESTRUCTURAL ---
st.set_page_config(
    page_title="Mercado Comunidad OS | Tao_Creator", 
    page_icon="🛒", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. NÚCLEO DE SEGURIDAD ---
# Tu clave maestra y usuario recordados
PASSWORD_TAO = "tao"  
ADMIN_NAME = "Tao_Creator"

# --- 3. MOTOR DE BASE DE DATOS (PERSISTENTE EN SERVIDOR) ---
@st.cache_resource
def inicializar_sistema_maestro():
    return {
        'muro': [],               
        'chats': {},              
        'baneos_temporales': {},  
        'ojo_de_tao': [],         
        'mantenimiento': False,   
        'aviso_mantenimiento': "🚨 SISTEMA EN OPTIMIZACIÓN - EL ADMINISTRADOR ESTÁ TRABAJANDO.",
        'aviso_global': "Bienvenido a la versión 2.0 del Mercado Sincronizado.",
        'sugerencias': [],
        'stats': {"total_visitas": 0, "objetos_borrados": 0}
    }

db = inicializar_sistema_maestro()

def log_maestro(usuario, accion):
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db['ojo_de_tao'].insert(0, f"⚡ [{ahora}] | {usuario} >> {accion}")

# --- 4. ESTILOS DE INTERFAZ AVANZADA (CSS) ---
st.markdown("""
    <style>
    /* Fondo y contenedores */
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e1e1e;
        border-radius: 5px 5px 0px 0px;
        padding: 10px 20px;
    }
    /* Tarjetas de productos */
    .product-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        transition: 0.3s;
    }
    .product-card:hover { border-color: #e91e63; transform: translateY(-5px); }
    /* Banner de actualización */
    .banner-tao {
        background: linear-gradient(135deg, #6200ea 0%, #d500f9 100%);
        padding: 20px;
        border-radius: 15px;
        border-left: 10px solid #ffffff;
        margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 5. SISTEMA DE PERSISTENCIA DE SESIÓN ---
# Si 'usuario' ya está en session_state, Streamlit NO mostrará el login al recargar.
if 'usuario' not in st.session_state:
    st.markdown("<h1 style='text-align: center; color: #e91e63;'>🔴 SISTEMA DE ACCESO CENTRAL</h1>", unsafe_allow_html=True)
    
    col_l, col_c, col_r = st.columns([1, 1.5, 1])
    with col_c:
        with st.container(border=True):
            user_input = st.text_input("Credencial de Usuario:", placeholder="Escribe tu nombre...")
            
            pass_input = ""
            if user_input == ADMIN_NAME:
                pass_input = st.text_input("Código Maestro Tao:", type="password")
            
            if st.button("INICIALIZAR SESIÓN", use_container_width=True):
                ahora = datetime.now()
                
                # VALIDACIÓN DE ADMINISTRADOR (TAO_CREATOR)
                if user_input == ADMIN_NAME and pass_input == PASSWORD_TAO:
                    st.session_state.usuario = user_input
                    st.session_state.es_admin = True
                    log_maestro(user_input, "ACCESO TOTAL CONCEDIDO (BYPASS MANTENIMIENTO)")
                    st.rerun()
                
                # VALIDACIÓN DE BANEOS
                elif user_input in db['baneos_temporales'] and ahora < db['baneos_temporales'][user_input]:
                    st.error("❌ IDENTIDAD RESTRINGIDA: Tu acceso está suspendido.")
                
                # VALIDACIÓN DE MANTENIMIENTO
                elif db['mantenimiento']:
                    st.warning(f"🚧 SERVIDOR CERRADO: {db['aviso_mantenimiento']}")
                
                # ACCESO ESTÁNDAR
                elif user_input.strip():
                    st.session_state.usuario = user_input
                    st.session_state.es_admin = False
                    log_maestro(user_input, "INICIO DE SESIÓN ESTÁNDAR")
                    st.rerun()
    st.stop()

# --- 6. PANEL DE CONTROL DE ALTA COMPLEJIDAD (SOLO PARA TAO_CREATOR) ---
if st.session_state.get('es_admin'):
    with st.sidebar:
        st.markdown(f"### 👑 MASTER CONSOLE: {ADMIN_NAME}")
        st.divider()
        
        with st.expander("🛠️ GESTIÓN DE NÚCLEO"):
            db['mantenimiento'] = st.toggle("Modo Mantenimiento Global", value=db['mantenimiento'])
            db['aviso_mantenimiento'] = st.text_area("Mensaje de Bloqueo:", db['aviso_mantenimiento'])
            if st.button("Actualizar Estado"): st.rerun()

        with st.expander("📢 BROADCAST DE ACTUALIZACIÓN"):
            db['aviso_global'] = st.text_area("Novedades de la Versión:", db['aviso_global'])
            if st.button("Enviar a todos los nodos"):
                log_maestro(ADMIN_NAME, "BROADCAST ENVIADO")
                st.success("Mensaje propagado.")

        with st.expander("🚫 PROTOCOLOS DE SEGURIDAD"):
            u_ban = st.text_input("ID de Usuario a restringir:")
            t_ban = st.number_input("Minutos de baneo:", 1, 1440, 10)
            if st.button("Ejecutar Suspensión"):
                db['baneos_temporales'][u_ban] = datetime.now() + timedelta(minutes=t_ban)
                log_maestro(ADMIN_NAME, f"BANEO APLICADO A {u_ban}")
                st.warning(f"Usuario {u_ban} bloqueado.")

        with st.expander("📊 TELEMETRÍA (OJO DE TAO)"):
            st.write(f"Posts activos: {len(db['muro'])}")
            if st.button("Vaciar Logs"): db['ojo_de_tao'] = []
            for l in db['ojo_de_tao'][:40]:
                st.caption(l)

# --- 7. INTERFAZ OPERATIVA PRINCIPAL ---
# Banner Persistente de Identidad
c1, c2 = st.columns([0.8, 0.2])
c1.markdown(f"# 🛒 MERCADO COMUNIDAD")
if c2.button("🚪 LOGOUT", use_container_width=True):
    log_maestro(st.session_state.usuario, "LOGOUT MANUAL")
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.rerun()

# Notificación de Actualización (Diseño Premium)
if db['aviso_global']:
    st.markdown(f"""
        <div class="banner-tao">
            <h4 style='margin:0; color:white;'>🚀 COMUNICADO DE TAO_CREATOR:</h4>
            <p style='margin:0; color:white; font-size:1.1em;'>{db['aviso_global']}</p>
        </div>
    """, unsafe_allow_html=True)

# SISTEMA DE PESTAÑAS
t_muro, t_mis_posts, t_chats, t_ideas = st.tabs([
    "🌐 MURO GLOBAL", "📦 MIS PUBLICACIONES", "💬 COMUNICACIONES", "💡 I+D"
])

# --- TAB: MURO GLOBAL ---
with t_muro:
    with st.expander("📤 LANZAR NUEVA PUBLICACIÓN AL MERCADO"):
        col_n, col_p = st.columns(2)
        n_p = col_n.text_input("Nombre del ítem:")
        p_p = col_p.number_input("Valor de intercambio ($):", min_value=1)
        f_p = st.file_uploader("Evidencia fotográfica:", type=['png','jpg','jpeg'])
        if st.button("PUBLICAR EN RED", use_container_width=True):
            if n_p and f_p:
                p_id = f"REF-{int(time.time())}"
                db['muro'].insert(0, {
                    "id": p_id, "n": n_p, "p": p_p, 
                    "v": st.session_state.usuario, "f": f_p,
                    "t": datetime.now().strftime("%H:%M")
                })
                log_maestro(st.session_state.usuario, f"NUEVO POST: {n_p}")
                st.rerun()

    # Visualización Compleja de Muro
    st.write("---")
    cols = st.columns(3) # Grid de 3 columnas
    for i, item in enumerate(db['muro']):
        with cols[i % 3]:
            st.markdown(f"""<div class="product-card">""", unsafe_allow_html=True)
            st.image(item['f'], use_container_width=True)
            st.subheader(item['n'])
            st.markdown(f"**💰 Precio:** ${item['p']}  \n**👤 Vendedor:** {item['v']}  \n**⏰ Hora:** {item['t']}")
            
            btn_c, btn_d = st.columns(2)
            if btn_c.button(f"💬 Chat", key=f"c_{item['id']}"):
                st.session_state.chat_activo = item['id']
            
            # Borrado administrativo
            if st.session_state.get('es_admin'):
                if btn_d.button(f"🗑️", key=f"adm_d_{item['id']}"):
                    db['muro'].pop(i)
                    log_maestro(ADMIN_NAME, f"BORRADO ADMIN: {item['n']}")
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

# --- TAB: MIS PUBLICACIONES (EL PEDIDO CLAVE) ---
with t_mis_posts:
    st.header("📦 Gestión de Inventario Personal")
    mis_cosas = [x for x in db['muro'] if x['v'] == st.session_state.usuario]
    
    if not mis_cosas:
        st.info("No posees activos publicados actualmente.")
    else:
        st.write(f"Gestionando **{len(mis_cosas)}** artículos:")
        for m in mis_cosas:
            with st.container(border=True):
                ca, cb, cc = st.columns([1, 3, 1])
                ca.image(m['f'], width=100)
                cb.markdown(f"### {m['n']} \n **Valor:** ${m['p']}")
                if cc.button("RETIRAR POST", key=f"self_d_{m['id']}"):
                    db['muro'] = [x for x in db['muro'] if x['id'] != m['id']]
                    log_maestro(st.session_state.usuario, f"RETIRÓ SU POST: {m['n']}")
                    st.rerun()

# --- TAB: COMUNICACIONES ---
with t_chats:
    st.warning("Sistema de mensajería cifrado en desarrollo. Selecciona un producto del muro para iniciar.")

# --- TAB: I+D (SUGERENCIAS) ---
with t_ideas:
    st.header("💡 Feedback para Tao_Creator")
    feedback = st.text_area("Propuesta de mejora para el núcleo del sistema:")
    if st.button("Enviar Propuesta"):
        db['sugerencias'].insert(0, {
            "u": st.session_state.usuario, "t": feedback, "h": datetime.now().strftime("%H:%M")
        })
        st.success("Datos enviados a la base del Creador.")
    
    if st.session_state.get('es_admin'):
        st.divider()
        st.subheader("🕵️ Revisión de Sugerencias Entrantes")
        for s in db['sugerencias']:
            st.info(f"**{s['u']}** ({s['h']}): {s['t']}")
