# =====================================================================
# SDK CADRE_ENTREPRISE - MODULE INTERFACE UTILISATEUR (ui.py)
# =====================================================================
import cadre_entreprise.auth as auth
import streamlit as st


def afficher_ecran_login(nom_app="Portail Central", icone="🔐"):
  """Affiche l'écran de connexion ou l'écran de premier changement de mot de passe."""
  _, col_centrale, _ = st.columns([1, 2, 1])

  with col_centrale:
    st.markdown(f"### {icone} {nom_app}")

    # -----------------------------------------------------------------
    # SCÉNARIO A : PREMIÈRE CONNEXION (CHANGEMENT DE MDP IMPÉRATIF)
    # -----------------------------------------------------------------
    if st.session_state.get("doit_changer_mdp", False):
      st.warning("🔒 **Première connexion détectée**")
      st.caption(
          "Pour des raisons de sécurité, vous devez modifier le mot de passe"
          " provisoire avant d'accéder à l'application."
      )

      with st.form("form_changement_mdp_sdk"):
        p1 = st.text_input("Nouveau mot de passe", type="password")
        p2 = st.text_input("Confirmer le mot de passe", type="password")
        btn_valider = st.form_submit_button(
            "💾 Enregistrer mon nouveau mot de passe", use_container_width=True
        )

      if btn_valider:
        if not p1 or not p2:
          st.error("⚠️ Veuillez remplir les deux champs.")
        elif p1 != p2:
          st.error("❌ Les mots de passe ne correspondent pas.")
        elif len(p1) < 6:
          st.error("⚠️ Le mot de passe doit contenir au moins 6 caractères.")
        else:
          user_temp = st.session_state.get("user_temp", {})
          succes, msg = auth.changer_mot_de_passe(user_temp.get("login"), p1)
          if succes:
            st.success(
                "✅ Mot de passe mis à jour ! Veuillez vous connecter avec"
                " votre nouveau mot de passe."
            )
            # Réinitialisation de l'état temporaire
            st.session_state["doit_changer_mdp"] = False
            st.session_state.pop("user_temp", None)
            st.rerun()
          else:
            st.error(msg)

    # -----------------------------------------------------------------
    # SCÉNARIO B : MIRE DE CONNEXION NORMALE
    # -----------------------------------------------------------------
    else:
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
      if st.button("🚪 Déconnexion", use_container_width=True):
        auth.deconnecter()