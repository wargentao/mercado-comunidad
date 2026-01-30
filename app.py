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
        'aviso_global': "",       # Mensajes de actualización
        'sugerencias': []
    }

db = obtener_db_global()

def registrar_actividad(usuario, accion):
    ahora = datetime.now().strftime("%H:%M:%S")
    db['ojo_de_tao'].insert(0, f"📌 [{ahora}] | 👤 {usuario}: {accion}")

# --- 4. ESTILOS CSS PARA HACERLO MÁS ROBUSTO ---
st.markdown("""
    <style>
    .stApp { background-color: #fcfcfc; }
    .update-box {
        background-color: #e3f2fd;
        border-left: 6px solid #2196f3;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .admin-card {
        background-color: #fff0f0;
        border: 1px solid #ffcdd2;
        padding: 10px;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 5. LÓGICA DE ACCESO Y MANTENIMIENTO ---
if 'usuario' not in st.session_state:
    st.markdown("<h1 style='text-align: center; color: #e91e63;'>🛒 MERCADO COMUNIDAD</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container(border=True):
            st.subheader("👤 Identificación de Usuario")
            u_in = st.text_input("Ingresá tu nombre:")
            
            p_in = ""
            if u_in == ADMIN_NAME:
                p_in = st.text_input("Llave Maestra:", type="password")
            
            if st.button("ACCEDER AL SISTEMA", use_container_width=True):
                ahora = datetime.now()
                
                # REGLA DE ORO: SI ES EL CREADOR, ENTRA DIRECTO
                if u_in == ADMIN_NAME and p_in == PASSWORD_TAO:
                    st.session_state.usuario = u_in
                    st.session_state.es_admin = True
                    registrar_actividad(u_in, "ENTRÓ AL PANEL DE CONTROL")
                    st.rerun()
                
                # REGLA 2: REVISAR SI EL USUARIO ESTÁ BANEADO
                elif u_in in db['baneos_temporales'] and ahora < db['baneos_temporales'][u_in]:
                    mins_restantes = int((db['baneos_temporales'][u_in] - ahora).total_seconds() / 60)
                    st.error(f"🚫 Acceso denegado. Estás suspendido por {mins_restantes + 1} minuto(s).")
                
                # REGLA 3: REVISAR MANTENIMIENTO (SOLO PARA NO-ADMINS)
                elif db['mantenimiento']:
                    st.warning(f"🚧 MANTENIMIENTO ACTIVO: {db['aviso_mantenimiento']}")
                
                # REGLA 4: ENTRADA DE USUARIO NORMAL
                elif u_in.strip():
                    st.session_state.usuario = u_in
                    st.session_state.es_admin = False
                    registrar_actividad(u_in, "ENTRÓ AL MERCADO")
                    st.rerun()
                else:
                    st.error("Escribí un nombre válido.")
    st.stop()

# --- 6. PANEL DE ADMINISTRADOR (SIDEBAR) ---
if st.session_state.get('es_admin'):
    with st.sidebar:
        st.error("👑 PANEL DE TAO_CREATOR")
        
        # GESTIÓN DE MANTENIMIENTO
        with st.expander("🚧 ESTADO DEL MERCADO"):
            db['aviso_mantenimiento'] = st.text_area("Mensaje para los usuarios:", value=db['aviso_mantenimiento'])
            if db['mantenimiento']:
                if st.button("🟢 ABRIR MERCADO", use_container_width=True):
                    db['mantenimiento'] = False
                    registrar_actividad(ADMIN_NAME, "ABRIÓ EL MERCADO")
                    st.rerun()
            else:
                if st.button("🔴 CERRAR POR MANTENIMIENTO", use_container_width=True):
                    db['mantenimiento'] = True
                    registrar_actividad(ADMIN_NAME, "CERRÓ EL MERCADO")
                    st.rerun()
        
        # ACTUALIZACIONES
        with st.expander("📢 LANZAR ACTUALIZACIÓN"):
            db['aviso_global'] = st.text_area("Descripción de la mejora:", value=db['aviso_global'])
            if st.button("Publicar Aviso Global"):
                registrar_actividad(ADMIN_NAME, "PUBLICÓ UNA ACTUALIZACIÓN")
                st.success("Actualización lanzada.")
            if st.button("Quitar Aviso"):
                db['aviso_global'] = ""
                st.rerun()

        # BANEOS
        with st.expander("🚫 BANEO TEMPORAL"):
            u_castigo = st.text_input("Usuario a castigar:")
            t_castigo = st.number_input("Minutos:", min_value=1, value=10)
            if st.button("Aplicar Castigo"):
                db['baneos_temporales'][u_castigo] = datetime.now() + timedelta(minutes=t_castigo)
                registrar_actividad(ADMIN_NAME, f"BANEÓ A {u_castigo}")
                st.success(f"Usuario {u_castigo} bloqueado.")

        # OJO DE TAO
        with st.expander("👁️ OJO DE TAO"):
            for log in db['ojo_de_tao'][:30]:
                st.caption(log)

# --- 7. INTERFAZ PRINCIPAL DE USUARIO ---
st.markdown(f"<h2 style='color: #ad1457;'>🛒 Bienvenido, {st.session_state.usuario}</h2>", unsafe_allow_html=True)

# MOSTRAR ACTUALIZACIONES SI EXISTEN
if db['aviso_global']:
    st.markdown(f"""
        <div class="update-box">
            <strong>✨ NUEVA ACTUALIZACIÓN:</strong><br>{db['aviso_global']}
        </div>
    """, unsafe_allow_html=True)

if st.sidebar.button("🚪 Cerrar Sesión"):
    registrar_actividad(st.session_state.usuario, "SALIÓ")
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

tabs = st.tabs(["🛒 El Muro", "💬 Mis Chats", "💡 Sugerencias"])

with tabs[0]: # EL MURO
    with st.expander("➕ Publicar un producto"):
        col1, col2 = st.columns(2)
        nombre_p = col1.text_input("¿Qué vendés?")
        precio_p = col2.number_input("Precio ($):", min_value=1)
        foto_p = st.file_uploader("Subí una foto:", type=['png','jpg','jpeg'])
        if st.button("🚀 Publicar Ahora"):
            if nombre_p and foto_p:
                db['muro'].insert(0, {
                    "id": f"{nombre_p}_{time.time()}", 
                    "nombre": nombre_p, "precio": precio_p, 
                    "vendedor": st.session_state.usuario, "foto": foto_p
                })
                registrar_actividad(st.session_state.usuario, f"PUBLICÓ: {nombre_p}")
                st.rerun()

    for i, p in enumerate(db['muro']):
        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 2, 0.5])
            with c1: st.image(p['foto'])
            with c2:
                st.subheader(p['nombre'])
                st.write(f"💰 Precio: **${p['precio']}**")
                st.write(f"👤 Vende: {p['vendedor']}")
                if st.button(f"Chat con {p['vendedor']}", key=f"chat_{i}"):
                    st.session_state.chat_activo = p['id']
            with c3:
                if st.session_state.get('es_admin'):
                    if st.button("🗑️", key=f"del_{i}"):
                        db['muro'].pop(i)
                        st.rerun()

with tabs[2]: # SUGERENCIAS
    st.header("💡 ¿Tenés una idea para el mercado?")
    idea = st.text_area("Escribí tu sugerencia para Tao_Creator:")
    if st.button("Enviar Sugerencia"):
        db['sugerencias'].insert(0, {"u": st.session_state.usuario, "t": idea, "h": datetime.now().strftime("%H:%M")})
        st.success("¡Gracias! Tu idea fue enviada.")
    
    if st.session_state.get('es_admin'):
        st.divider()
        st.subheader("🕵️ Buzón de Sugerencias")
        for s in db['sugerencias']:
            st.write(f"**{s['u']}** ({s['h']}): {s['t']}")
