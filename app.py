import streamlit as st
from datetime import datetime

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Mercado Comunidad", page_icon="🛒", layout="centered")

# --- 2. SEGURIDAD MAESTRA ---
PASSWORD_TAO = "TAO2024" 
ADMIN_NAME = "TAO_CREATOR"

# --- 3. BASE DE DATOS GLOBAL (Sincroniza a todos los usuarios) ---
@st.cache_resource
def obtener_base_datos_global():
    return {
        'muro': [],
        'baneados': set(),
        'ojo_de_tao': [],
        'chats': {},
        'mantenimiento': False,
        'aviso_mantenimiento': "Mantenimiento técnico por Tao Wargen.",
        'sugerencias': []
    }

db = obtener_base_datos_global()

def registrar_actividad(usuario, accion):
    ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    registro = f"📌 [{ahora}] | 👤 {usuario}: {accion}"
    db['ojo_de_tao'].insert(0, registro)

# --- 4. ESTILO Y LOGO ---
def mostrar_logo():
    st.markdown("""
        <div style='text-align: center; background-color: #fce4ec; padding: 15px; border-radius: 15px; border: 3px solid #e91e63;'>
            <h1 style='color: #880e4f; margin: 0;'>🛒 MERCADO COMUNIDAD</h1>
            <p style='color: #ad1457; font-weight: bold;'>Plataforma Oficial de Tao Wargen</p>
        </div>
        <br>
    """, unsafe_allow_html=True)

# --- 5. FILTRO DE MANTENIMIENTO GLOBAL ---
# Si el admin real está logueado, él puede saltarse el mantenimiento para arreglar cosas
es_admin_real = st.session_state.get('es_admin_real', False)
if db['mantenimiento'] and not es_admin_real:
    mostrar_logo()
    st.markdown(f"""
        <div style='text-align: center; background-color: #1a1a1a; padding: 60px; border-radius: 30px; border: 5px solid red;'>
            <h1 style='color: white; font-size: 80px;'>🛠️</h1>
            <h2 style='color: #ff4b4b;'>MANTENIMIENTO ACTIVADO</h2>
            <div style='background-color: #262626; padding: 20px; border-radius: 15px; margin: 20px 0;'>
                <p style='color: #eeeeee; font-size: 20px;'>"{db['aviso_mantenimiento']}"</p>
            </div>
            <p style='color: #888;'>Atentamente: Tao Wargen</p>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# --- 6. SISTEMA DE LOGIN ---
if 'usuario' not in st.session_state:
    mostrar_logo()
    with st.container(border=True):
        st.subheader("👤 Identificarse")
        nombre_in = st.text_input("Nombre de usuario:")
        pass_in = ""
        if nombre_in == ADMIN_NAME:
            pass_in = st.text_input("Llave Maestra:", type="password")
        
        if st.button("Entrar", use_container_width=True):
            if nombre_in in db['baneados']:
                st.error("🚫 Tu acceso ha sido revocado por el administrador.")
            elif nombre_in == ADMIN_NAME and pass_in != PASSWORD_TAO:
                st.error("❌ Llave incorrecta.")
            elif not nombre_in.strip():
                st.warning("Escribí un nombre.")
            else:
                st.session_state.usuario = nombre_in
                st.session_state.es_admin_real = (nombre_in == ADMIN_NAME)
                st.session_state.nombre_falso_activo = False
                registrar_actividad(nombre_in, "ENTRÓ AL MERCADO")
                st.rerun()
    st.stop()

# --- 7. PANEL DE ADMINISTRADOR (SOLO TAO_CREATOR) ---
if st.session_state.get('es_admin_real', False):
    with st.sidebar:
        st.error(f"👑 PANEL {ADMIN_NAME}")
        
        # MODO INCÓGNITO
        st.subheader("🕵️ Identidad Oculta")
        if not st.session_state.nombre_falso_activo:
            n_falso = st.text_input("Nombre para infiltrarse:")
            if st.button("🎭 Usar Nombre Falso"):
                if n_falso.strip() and n_falso != ADMIN_NAME:
                    st.session_state.usuario = n_falso
                    st.session_state.nombre_falso_activo = True
                    registrar_actividad(ADMIN_NAME, f"INFILTRADO COMO: {n_falso}")
                    st.rerun()
        else:
            st.info(f"Usando: {st.session_state.usuario}")
            if st.button("🔙 Volver a TAO_CREATOR"):
                st.session_state.usuario = ADMIN_NAME
                st.session_state.nombre_falso_activo = False
                st.rerun()

        st.divider()
        st.subheader("🚧 Mantenimiento")
        motivo = st.text_area("Mensaje para usuarios:", value=db['aviso_mantenimiento'])
        if st.button("🔴 CERRAR / 🟢 ABRIR MERCADO"):
            db['aviso_mantenimiento'] = motivo
            db['mantenimiento'] = not db['mantenimiento']
            registrar_actividad(ADMIN_NAME, f"Mantenimiento cambiado a: {db['mantenimiento']}")
            st.rerun()
        
        st.divider()
        st.subheader("👁️ OJO DE TAO (Actividad Global)")
        for log in db['ojo_de_tao'][:20]: st.caption(log)
        
        st.divider()
        u_ban = st.text_input("Nombre a BANEAR:")
        if st.button("EJECUTAR BAN"): 
            db['baneados'].add(u_ban)
            registrar_actividad(ADMIN_NAME, f"BANEÓ A: {u_ban}")
            st.success(f"{u_ban} bloqueado.")
            st.rerun()

# --- 8. INTERFAZ PRINCIPAL ---
mostrar_logo()
st.caption(f"Conectado como: **{st.session_state.usuario}**")

if st.sidebar.button("🚪 Cerrar Sesión"):
    registrar_actividad(st.session_state.usuario, "SALIÓ")
    del st.session_state.usuario
    if 'es_admin_real' in st.session_state: del st.session_state.es_admin_real
    st.rerun()

tabs = st.tabs(["🛒 El Muro", "🛍️ Mi Carrito", "💬 Chats", "💡 Sugerencias"])

# --- MURO ---
with tabs[0]:
    with st.expander("➕ Publicar Artículo"):
        c1, c2 = st.columns(2)
        with c1:
            prod_n = st.text_input("Producto:")
            prod_p = st.number_input("Precio ARS $:", min_value=1)
        with c2:
            es_sub = st.checkbox("¿Es subasta?")
            foto_p = st.file_uploader("Foto Principal", type=['png', 'jpg', 'jpeg'])
        
        prod_d = st.text_area("Descripción (Opcional)")
        fotos_x = st.file_uploader("Fotos extras", type=['png', 'jpg'], accept_multiple_files=True)

        if st.button("🚀 Publicar", disabled=(not foto_p or not prod_n)):
            id_p = f"{prod_n}_{datetime.now().timestamp()}"
            db['muro'].insert(0, {
                "id": id_p, "n": prod_n, "p": prod_p, "v": st.session_state.usuario, 
                "s": es_sub, "g": "Nadie", "f": foto_p, "d": prod_d, "fx": fotos_x
            })
            registrar_actividad(st.session_state.usuario, f"PUBLICÓ: {prod_n}")
            st.rerun()

    for i, item in enumerate(db['muro']):
        with st.container(border=True):
            ci, ct, cc = st.columns([1.5, 2.5, 0.8])
            with ci:
                st.image(item['f'], use_container_width=True)
                if item.get('fx'):
                    c_ex = st.columns(len(item['fx']))
                    for ix, im in enumerate(item['fx']): c_ex[ix].image(im)
            with ct:
                st.subheader(item['n'])
                if item.get('d'): st.caption(f"📝 {item['d']}")
                if item['s']:
                    st.info(f"🔨 Puja: ARS ${item['p']} | Líder: {item['g']}")
                    oferta = st.number_input("Pujar:", min_value=int(item['p']+10), key=f"of_{i}")
                    if st.button("Pujar", key=f"bof_{i}"):
                        item['p'] = oferta; item['g'] = st.session_state.usuario
                        registrar_actividad(st.session_state.usuario, f"PUJÓ ARS ${oferta} en {item['n']}")
                        st.rerun()
                else:
                    st.write(f"💰 **ARS ${item['p']}** | Vende: {item['v']}")
                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        if st.button("🛒 Guardar", key=f"ca_{i}"):
                            st.session_state.setdefault('mi_carrito', []).append(item)
                            st.toast("Guardado")
                    with col_b2:
                        if st.button("💬 Chat", key=f"ch_{i}"):
                            st.session_state.chat_activo = item['id']
            with cc:
                if st.session_state.get('es_admin_real'):
                    if st.button("🔴", key=f"t_{i}"):
                        db['muro'].pop(i)
                        registrar_actividad(ADMIN_NAME, f"ELIMINÓ {item['n']}")
                        st.rerun()

# --- CARRITO ---
with tabs[1]:
    st.header("Tus cosas guardadas")
    carrito_personal = st.session_state.get('mi_carrito', [])
    for c in carrito_personal:
        st.write(f"📦 **{c['n']}** - ARS ${c['p']} (Vendedor: {c['v']})")

# --- CHATS ---
with tabs[2]:
    chat_id = st.session_state.get('chat_activo')
    if chat_id:
        p_chat = next((x for x in db['muro'] if x['id'] == chat_id), None)
        if p_chat:
            st.subheader(f"Chat: {p_chat['n']}")
            mensajes = db['chats'].get(chat_id, [])
            for m in mensajes: st.write(f"**{m['u']}:** {m['t']}")
            
            n_msg = st.text_input("Escribí un mensaje:", key="msg")
            if st.button("Enviar"):
                db['chats'].setdefault(chat_id, []).append({"u": st.session_state.usuario, "t": n_msg})
                st.rerun()
    else:
        st.write("Seleccioná un producto y tocá 'Chat'.")

# --- SUGERENCIAS ---
with tabs[3]:
    idea = st.text_area("¿Cómo mejorar?")
    if st.button("Enviar"):
        db['sugerencias'].append(f"{st.session_state.usuario}: {idea}")
        registrar_actividad(st.session_state.usuario, "ENVIÓ SUGERENCIA")
        st.success("¡Recibido!")
