import streamlit as st
from datetime import datetime

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Mercado Comunidad", page_icon="🛒", layout="centered")

# --- 2. SEGURIDAD MAESTRA ---
PASSWORD_TAO = "TAO2024" 
ADMIN_NAME = "TAO_CREATOR"

# --- 3. BASES DE DATOS COMPARTIDAS ---
for llave in ['muro', 'baneados', 'sugerencias', 'ojo_de_tao', 'carrito', 'chats', 'aviso_mantenimiento', 'mantenimiento']:
    if llave not in st.session_state:
        if llave == 'mantenimiento': st.session_state[llave] = False
        elif llave == 'aviso_mantenimiento': st.session_state[llave] = "Mantenimiento técnico por Tao Wargen."
        elif llave == 'chats': st.session_state[llave] = {} 
        else: st.session_state[llave] = []

def registrar_actividad(usuario, accion):
    ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    registro = f"📌 [{ahora}] | 👤 {usuario}: {accion}"
    st.session_state.ojo_de_tao.insert(0, registro)

# --- 4. CABECERA ---
def mostrar_logo():
    st.markdown("""
        <div style='text-align: center; background-color: #fce4ec; padding: 15px; border-radius: 15px; border: 3px solid #e91e63;'>
            <h1 style='color: #880e4f; margin: 0;'>🛒 MERCADO COMUNIDAD</h1>
            <p style='color: #ad1457; font-weight: bold;'>Plataforma Oficial de Tao Wargen</p>
        </div>
        <br>
    """, unsafe_allow_html=True)

# --- 5. FILTRO DE MANTENIMIENTO ---
if st.session_state.mantenimiento and not st.session_state.get('es_admin_real', False):
    mostrar_logo()
    st.markdown(f"""
        <div style='text-align: center; background-color: #1a1a1a; padding: 60px; border-radius: 30px; border: 5px solid #ff4b4b;'>
            <h1 style='color: white; font-size: 80px;'>🛠️</h1>
            <h2 style='color: #ff4b4b;'>MANTENIMIENTO ACTIVADO</h2>
            <div style='background-color: #262626; padding: 20px; border-radius: 15px; margin: 20px 0;'>
                <p style='color: #eeeeee; font-size: 20px;'>"{st.session_state.aviso_mantenimiento}"</p>
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
            if nombre_in in st.session_state.baneados:
                st.error("🚫 Tu acceso ha sido revocado.")
            elif nombre_in == ADMIN_NAME and pass_in != PASSWORD_TAO:
                st.error("❌ Llave incorrecta.")
            elif not nombre_in.strip():
                st.warning("Escribí un nombre.")
            else:
                st.session_state.usuario = nombre_in
                st.session_state.es_admin_real = (nombre_in == ADMIN_NAME)
                st.session_state.nombre_falso_activo = False
                registrar_actividad(nombre_in, "INICIÓ SESIÓN")
                st.rerun()
    st.stop()

# --- 7. PANEL DE ADMINISTRADOR (SOLO CREADOR) ---
if st.session_state.get('es_admin_real', False):
    with st.sidebar:
        st.error(f"👑 PANEL {ADMIN_NAME}")
        
        # MODO INCOGNITO
        st.subheader("🕵️ Identidad Oculta")
        if not st.session_state.nombre_falso_activo:
            n_falso = st.text_input("Nombre falso para infiltrarse:")
            if st.button("🎭 Usar Identidad Falsa"):
                if n_falso.strip() and n_falso != ADMIN_NAME:
                    st.session_state.usuario = n_falso
                    st.session_state.nombre_falso_activo = True
                    registrar_actividad(ADMIN_NAME, f"INFILTRADO COMO: {n_falso}")
                    st.rerun()
        else:
            if st.button("🔙 Volver a ser TAO_CREATOR"):
                st.session_state.usuario = ADMIN_NAME
                st.session_state.nombre_falso_activo = False
                st.rerun()

        st.divider()
        st.subheader("🚧 Mantenimiento")
        motivo_mante = st.text_area("Razón del cierre:", value=st.session_state.aviso_mantenimiento)
        if st.button("🔴 CERRAR / 🟢 ABRIR"):
            st.session_state.aviso_mantenimiento = motivo_mante
            st.session_state.mantenimiento = not st.session_state.mantenimiento
            st.rerun()
        
        st.divider()
        st.subheader("👁️ OJO DE TAO")
        for log in st.session_state.ojo_de_tao[:15]: st.caption(log)
        
        st.divider()
        u_ban = st.text_input("Bannear usuario:")
        if st.button("BAN"): 
            st.session_state.baneados.append(u_ban)
            registrar_actividad(ADMIN_NAME, f"BANEÓ A {u_ban}")
            st.rerun()

# --- 8. INTERFAZ PRINCIPAL ---
mostrar_logo()
st.caption(f"Usuario: **{st.session_state.usuario}**")

# Botón salir para usuarios comunes
if st.sidebar.button("🚪 Cerrar Sesión"):
    registrar_actividad(st.session_state.usuario, "CERRÓ SESIÓN")
    for k in ['usuario', 'es_admin_real', 'nombre_falso_activo']:
        if k in st.session_state: del st.session_state[k]
    st.rerun()

tabs = st.tabs(["🛒 El Muro", "🛍️ Mi Carrito", "💬 Mis Chats", "💡 Sugerencias"])

# --- TAB 1: EL MURO ---
with tabs[0]:
    with st.expander("➕ Publicar Artículo (FOTO OBLIGATORIA)"):
        c1, c2 = st.columns(2)
        with c1:
            prod_n = st.text_input("¿Qué vendés?")
            prod_p = st.number_input("Precio/Puja (ARS $):", min_value=1)
        with c2:
            es_sub = st.checkbox("¿Es subasta?")
            foto_p = st.file_uploader("Foto Principal", type=['png', 'jpg', 'jpeg'])
        
        prod_d = st.text_area("Descripción (Opcional)")
        fotos_x = st.file_uploader("Fotos extras (Opcional)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

        if st.button("🚀 Publicar Ahora", disabled=(not foto_p or not prod_n)):
            id_p = f"{prod_n}_{datetime.now().timestamp()}"
            st.session_state.muro.insert(0, {
                "id": id_p, "n": prod_n, "p": prod_p, "v": st.session_state.usuario, 
                "s": es_sub, "g": "Nadie", "f": foto_p, "d": prod_d, "fx": fotos_x
            })
            registrar_actividad(st.session_state.usuario, f"PUBLICÓ: {prod_n}")
            st.rerun()

    for i, item in enumerate(st.session_state.muro):
        with st.container(border=True):
            ci, ct, cc = st.columns([1.5, 2.5, 0.8])
            with ci:
                st.image(item['f'], use_container_width=True)
                if item.get('fx'):
                    c_ex = st.columns(len(item['fx']))
                    for ix, im in enumerate(item['fx']): c_ex[ix].image(im, use_container_width=True)
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
                    st.write(f"💰 **ARS ${item['p']}**")
                    st.caption(f"Vende: {item['v']}")
                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        if st.button("🛒 Guardar", key=f"ca_{i}"):
                            st.session_state.carrito.append(item); st.toast("Guardado")
                    with col_b2:
                        if st.button(f"💬 Chat", key=f"ch_{i}"):
                            st.session_state.chat_activo = item['id']
                            st.toast("Chat abierto en la pestaña de Chats")
            with cc:
                if st.session_state.get('es_admin_real'):
                    if st.button("🔴", key=f"t_{i}"):
                        registrar_actividad(ADMIN_NAME, f"BORRÓ: {item['n']}")
                        st.session_state.muro.pop(i); st.rerun()

# --- TAB 2: CARRITO ---
with tabs[1]:
    st.header("Tus cosas guardadas")
    for c in st.session_state.carrito:
        st.write(f"📦 **{c['n']}** - ARS ${c['p']} (Vendedor: {c['v']})")

# --- TAB 3: CHATS ---
with tabs[2]:
    st.header("Mensajes de Intercambio")
    chat_id = st.session_state.get('chat_activo')
    if chat_id:
        prod = next((x for x in st.session_state.muro if x['id'] == chat_id), None)
        if prod:
            st.subheader(f"Chat de: {prod['n']}")
            mensajes = st.session_state.chats.get(chat_id, [])
            for m in mensajes: st.write(f"**{m['u']}:** {m['t']}")
            
            n_msg = st.text_input("Escribí acá:", key="input_chat")
            if st.button("Enviar ➡️"):
                if n_msg:
                    st.session_state.chats.setdefault(chat_id, []).append({"u": st.session_state.usuario, "t": n_msg})
                    registrar_actividad(st.session_state.usuario, f"CHATEÓ EN {prod['n']}")
                    st.rerun()
    else:
        st.info("Elegí un producto en el muro y tocá el botón de Chat para hablar con el vendedor.")

# --- TAB 4: SUGERENCIAS ---
with tabs[3]:
    idea = st.text_area("¿Cómo mejoramos el Mercado?")
    if st.button("Enviar Sugerencia"):
        st.session_state.sugerencias.append(f"{st.session_state.usuario}: {idea}")
        st.success("¡Gracias! Tao Wargen lo revisará.")
