# =====================================================================
# SDK CADRE_ENTREPRISE - MODULE INTERFACE UTILISATEUR (ui.py)
# =====================================================================
import cadre_entreprise.auth as auth
import streamlit as st


def afficher_ecran_login(nom_application="Portail Central", icone="🔐", **kwargs):
    """
    Affiche l'écran de connexion principal hybride (Mot de passe OU YubiKey 1-Click).
    Gère la rétrocompatibilité des arguments via **kwargs.
    """
    # 💡 ASTUCE PRO : Rétrocompatibilité
    # Si une app utilise la nomenclature "nom_app", on l'écrase sur nom_application
    nom_a_afficher = kwargs.get("nom_app", nom_application)

    _, col_centrale, _ = st.columns([1, 2, 1])

    with col_centrale:
        st.markdown(f"### {icone} {nom_a_afficher}")

        # -----------------------------------------------------------------
        # MIRE DE CONNEXION HYBRIDE (ONGLETS MOT DE PASSE & YUBIKEY 1-CLICK)
        # -----------------------------------------------------------------
        with st.container(border=True):
            tab_pass, tab_yubi = st.tabs([
                "🔑 Mot de Passe",
                "🛡️ Clé YubiKey (1-Click)",
            ])

            # --- ONGLET 1 : MOT DE PASSE CLASSIQUE ---
            with tab_pass:
                with st.form("form_login_sdk_pass"):
                    st.subheader("Connexion Enterprise")
                    f_login = st.text_input("Identifiant").lower().strip()
                    f_mdp = st.text_input("Mot de passe", type="password")
                    btn_connecter = st.form_submit_button(
                        "Se connecter 🔓", use_container_width=True, type="primary"
                    )

                if btn_connecter:
                    if f_login and f_mdp:
                        succes, msg = auth.connecter(f_login, f_mdp)
                        if succes:
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.warning("⚠️ Veuillez renseigner le login et le mot de passe.")

            # --- ONGLET 2 : YUBIKEY 1-CLICK (SANS SAISIE D'IDENTIFIANT) ---
            with tab_yubi:
                st.subheader("Connexion Instantanée YubiKey")
                st.caption(
                    "Insérez votre YubiKey, placez votre curseur ci-dessous et pressez le capteur."
                )
                with st.form("form_login_sdk_yubi_direct", clear_on_submit=True):
                    f_yubi_code = st.text_input(
                        "🔑 Pressez / Touchez votre YubiKey ici",
                        type="password",
                        help=(
                            "Aucun identifiant requis ! Votre clé physique vous"
                            " identifie automatiquement auprès du serveur."
                        ),
                    )
                    btn_connecter_yubi = st.form_submit_button(
                        "Valider par YubiKey 🛡️", use_container_width=True, type="primary"
                    )

                if btn_connecter_yubi:
                    if f_yubi_code:
                        # Appel de la résolution automatique par Public ID
                        succes, msg = auth.connecter_par_yubikey_directe(f_yubi_code)
                        if succes:
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.warning("⚠️ Veuillez insérer et toucher votre YubiKey.")


def afficher_sidebar_standard():
    """Affiche une barre latérale profil standardisée avec bouton de déconnexion."""
    if auth.est_connecte():
        user = auth.get_user_info()
        with st.sidebar:
            st.markdown(f"### 👤 {user.get('nom', 'Utilisateur')}")
            st.caption(f"Service : **{user.get('service', 'N/A')}**")
            st.caption(f"Rôle : **{user.get('role', 'USER')}**")
            st.divider()

            if st.button("🚪 Déconnexion", use_container_width=True):
                auth.deconnecter()