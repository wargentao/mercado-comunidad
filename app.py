import streamlit as st
from datetime import datetime, timedelta
import time

# --- 1. CONFIGURACIÓN DE ALTO NIVEL ---
st.set_page_config(page_title="Mercado Comunidad | Tao_Creator", page_icon="🛒", layout="wide")

# --- 2. SEGURIDAD MAESTRA ---
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
        'aviso_mantenimiento': "🛠️ El servidor se encuentra en mantenimiento técnico. Volvemos pronto.",
        'aviso_global': "",       
        'sugerencias': []
    }

db = obtener_db_global()

def registrar_actividad(usuario, accion):
    ahora = datetime.now().strftime("%H:%M:%S")
    db['ojo_de_tao'].insert(0, f"📌 [{ahora}] | 👤 {usuario}: {accion}")

# --- 4. ESTILOS CSS PROFESIONALES ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .update-box {
        background: linear-gradient(90deg, #e3f2fd 0%, #bbdefb 100%);
        border-left: 8px solid #1976d2;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 25px;
    }
    .product-card {
        border-radius: 15px;
        padding: 15px;
        background-color: white;
        border: 1px solid #e0e0e0;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# --- 5. LÓGICA DE ACCESO CON PRIORIDAD ADMIN ---
if 'usuario' not in st.session_state:
    st.markdown("<h1 style='text-align: center; color: #e91e63;'>🛒 MERCADO COMUNIDAD</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container(border=True):
            st.subheader("👤 Identificación")
            u_in = st.text_input("Nombre de Usuario:")
            
            p_in = ""
            if u_in == ADMIN_NAME:
                p_in = st.text_input("Llave Maestra:", type="password")
            
            if st.button("ACCEDER AL SISTEMA", use_container_width=True):
                ahora = datetime.now()
                
                # PRIORIDAD ABSOLUTA PARA TAO_CREATOR
                if u_in == ADMIN_NAME and p_in == PASSWORD_TAO:
                    st.session_state.usuario = u_in
                    st.session_state.es_admin = True
                    registrar_actividad(u_in, "ACCESO TOTAL CONCEDIDO")
                    st.rerun()
                
                # FILTRO DE BANEOS
                elif u_in in db['baneos_temporales'] and ahora < db['baneos_temporales'][u_in]:
                    st.error("🚫 Tu acceso ha sido revocado temporalmente por la administración.")
                
                # FILTRO DE MANTENIMIENTO
                elif db['mantenimiento']:
                    st.warning(f"🚧 {db['aviso_mantenimiento']}")
                
                # ACCESO ESTÁNDAR
                elif u_in.strip():
                    st.session_state.usuario = u_in
                    st.session_state.es_admin = False
                    registrar_actividad(u_in, "ENTRADA EXITOSA")
                    st.rerun()
                else:
                    st.error("Por favor, ingrese un nombre.")
    st.stop()

# --- 6. PANEL DE CONTROL AVANZADO (SIDEBAR) ---
if st.session_state.get('es_admin'):
    with st.sidebar:
        st.error("👑 MASTER CONTROL PANEL")
        
        with st.expander("🚧 GESTIÓN DE SERVIDOR"):
            db['aviso_mantenimiento'] = st.text_area("Mensaje de Mantenimiento:", value=db['aviso_mantenimiento'])
            if st.button("🟢 ABRIR SISTEMA" if db['mantenimiento'] else "🔴 ACTIVAR MANTENIMIENTO", use_container_width=True):
                db['mantenimiento'] = not db['mantenimiento']
                st.rerun()
        
        with st.expander("📢 COMUNICADOS GLOBALES"):
            db['aviso_global'] = st.text_area("Texto de Actualización:", value=db['aviso_global'])
            if st.button("Lanzar Actualización"): st.rerun()
            if st.button("Eliminar Aviso"): 
                db['aviso_global'] = ""
                st.rerun()

        with st.expander("🚫 PROTOCOLO DE SUSPENSIÓN"):
            u_target = st.text_input("Usuario:")
            t_min = st.number_input("Minutos:", min_value=1, value=5)
            if st.button("Ejecutar Baneo"):
                db['baneos_temporales'][u_target] = datetime.now() + timedelta(minutes=t_min)
                st.success(f"Usuario {u_target} bloqueado.")

        with st.expander("👁️ EL OJO DE TAO (LOGS)"):
            for log in db['ojo_de_tao'][:25]: st.caption(log)

# --- 7. INTERFAZ DE USUARIO Y PESTAÑAS ---
st.markdown(f"## 👤 Usuario: {st.session_state.usuario}")

if db['aviso_global']:
    st.markdown(f"""<div class="update-box"><strong>🚀 ACTUALIZACIÓN DE SISTEMA:</strong><br>{db['aviso_global']}</div>""", unsafe_allow_html=True)

if st.sidebar.button("🚪 SALIR DEL SISTEMA"):
    registrar_actividad(st.session_state.usuario, "SESIÓN FINALIZADA")
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

# CREACIÓN DE PESTAÑAS (INCLUYENDO MIS PUBLICACIONES)
tabs = st.tabs(["🛒 El Muro", "📦 Mis Publicaciones", "💬 Chats", "💡 Sugerencias"])

# --- TAB 1: EL MURO ---
with tabs[0]:
    with st.expander("➕ PUBLICAR NUEVO PRODUCTO"):
        col1, col2 = st.columns(2)
        n_p = col1.text_input("Nombre del artículo:")
        p_p = col2.number_input("Precio ($):", min_value=1)
        f_p = st.file_uploader("Foto del producto:", type=['png','jpg','jpeg'])
        if st.button("Lanzar al Mercado"):
            if n_p and f_p:
                db['muro'].insert(0, {
                    "id": f"{n_p}_{time.time()}", "nombre": n_p, "precio": p_p,
                    "vendedor": st.session_state.usuario, "foto": f_p
                })
                registrar_actividad(st.session_state.usuario, f"PUBLICÓ: {n_p}")
                st.rerun()

    for i, p in enumerate(db['muro']):
        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 2, 0.5])
            with c1: st.image(p['foto'], use_container_width=True)
            with c2:
                st.subheader(p['nombre'])
                st.write(f"💰 Valor: **${p['precio']}**")
                st.write(f"👤 Publicado por: {p['vendedor']}")
                if st.button(f"Chat con Vendedor", key=f"chat_{i}"):
                    st.session_state.chat_activo = p['id']
            with c3:
                if st.session_state.get('es_admin') and st.button("🗑️", key=f"del_{i}"):
                    db['muro'].pop(i)
                    st.rerun()

# --- TAB 2: MIS PUBLICACIONES (EL PEDIDO ESPECIAL) ---
with tabs[1]:
    st.header("📦 Gestión de Mis Artículos")
    mis_articulos = [x for x in db['muro'] if x['vendedor'] == st.session_state.usuario]
    
    if not mis_articulos:
        st.info("Aún no tienes productos en venta. ¡Publica tu primer artículo en la pestaña El Muro!")
    else:
        st.write(f"Tienes **{len(mis_articulos)}** artículos activos.")
        for idx, m in enumerate(mis_articulos):
            with st.container(border=True):
                col_info, col_img, col_acc = st.columns([2, 1, 1])
                with col_info:
                    st.markdown(f"### {m['nombre']}")
                    st.markdown(f"**Precio actual:** ${m['precio']}")
                with col_img:
                    st.image(m['foto'], width=100)
                with col_acc:
                    # Aquí el usuario puede borrar su propia publicación
                    if st.button("Eliminar Publicación", key=f"user_del_{idx}"):
                        db['muro'] = [x for x in db['muro'] if x['id'] != m['id']]
                        registrar_actividad(st.session_state.usuario, f"ELIMINÓ SU POST: {m['nombre']}")
                        st.success("Eliminado correctamente.")
                        st.rerun()

# --- TAB 4: SUGERENCIAS ---
with tabs[3]:
    st.header("💡 Centro de Feedback")
    idea = st.text_area("¿Cómo podemos mejorar el Mercado?")
    if st.button("Enviar Sugerencia Directa"):
        db['sugerencias'].insert(0, {"u": st.session_state.usuario, "t": idea, "h": datetime.now().strftime("%H:%M")})
        st.success("Tu mensaje ha sido enviado a la base de datos de Tao_Creator.")
    
    if st.session_state.get('es_admin'):
        st.divider()
        st.subheader("🕵️ Historial de Sugerencias")
        for s in db['sugerencias']:
            st.write(f"🔹 **{s['u']}** ({s['h']}): {s['t']}")
