# =====================================================================
# SDK CADRE_ENTREPRISE - MODULE INTERFACE UTILISATEUR (ui.py)
# =====================================================================
import cadre_entreprise.auth as auth
import streamlit as st


def afficher_ecran_login(nom_application="Portail Central", icone="🔐", **kwargs):
    """
    Affiche l'écran de connexion principal.
    (Note: Le changement de mot de passe obligatoire est géré séparément)
    """
    # 💡 ASTUCE PRO : Rétrocompatibilité absolue ! 
    # Si une app utilise la nouvelle nomenclature "nom_app", on l'écrase sur nom_application
    nom_a_afficher = kwargs.get("nom_app", nom_application)

    _, col_centrale, _ = st.columns([1, 2, 1])

    with col_centrale:
        st.markdown(f"### {icone} {nom_a_afficher}")

        # -----------------------------------------------------------------
        # MIRE DE CONNEXION NORMALE
        # -----------------------------------------------------------------
        with st.container(border=True):
            with st.form("form_login_sdk"):
                st.subheader("Connexion Enterprise")
                f_login = st.text_input("Identifiant").lower().strip()
                f_mdp = st.text_input("Mot de passe", type="password")
                btn_connecter = st.form_submit_button(
                    "Se connecter 🔓", use_container_width=True
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


def afficher_sidebar_standard():
    """Affiche une barre latérale profil standardisée avec bouton de déconnexion."""
    if auth.est_connecte():
        user = auth.get_user_info()
        with st.sidebar:
            st.markdown(f"### 👤 {user.get('nom', 'Utilisateur')}")
            st.caption(f"Service : **{user.get('service', 'N/A')}**")
            st.caption(f"Rôle : **{user.get('role', 'USER')}**")
            st.divider()
            
            # (Optionnel : C'est ici que tu pourras ajouter ton futur bouton de changement de MDP)
            
            if st.button("🚪 Déconnexion", use_container_width=True):
                auth.deconnecter()