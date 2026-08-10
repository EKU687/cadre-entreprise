import modules.auth as auth
import streamlit as st


def afficher_ecran_login(nom_application: str = "Application", icone: str = "🚀"):
  """Affiche le formulaire de connexion standardisé dans un conteneur épuré."""
  st.title(f"{icone} {nom_application}")
  st.subheader("🔐 Veuillez vous identifier pour accéder à l'application")

  # Centrage visuel du formulaire
  col_left, col_center, col_right = st.columns([1, 2, 1])

  with col_center:
    with st.container(border=True):
      st.markdown(
          f"<h3 style='text-align: center;'>Connexion Enterprise</h3>",
          unsafe_allow_html=True,
      )

      with st.form("form_login_standard"):
        login_saisi = st.text_input("Identifiant").lower().strip()
        mdp_saisi = st.text_input("Mot de passe", type="password")
        st.write("")  # Espacement
        btn_login = st.form_submit_button(
            "Se connecter 🔓", use_container_width=True
        )

      if btn_login:
        if not login_saisi or not mdp_saisi:
          st.warning("⚠️ Veuillez remplir tous les champs.")
        else:
          succes = auth.authentifier_utilisateur(login_saisi, mdp_saisi)
          if succes:
            st.success("✅ Connexion réussie !")
            st.rerun()
          else:
            st.error("❌ Identifiant ou mot de passe incorrect.")


def afficher_sidebar_standard(
    url_portail_hub: str = "https://portail-hub.streamlit.app",
):
  """Affiche la barre latérale standardisée avec profil, retour portail et déconnexion."""
  user = auth.get_user_info()

  if not user:
    return

  user_nom = user.get("nom", "Utilisateur")
  user_role = str(user.get("role", "USER")).upper().strip()
  user_service = user.get("service", "N/A")

  with st.sidebar:
    # Bloc Profil Utilisateur
    st.markdown("### 👤 Profil Connecté")
    st.write(f"**{user_nom}**")
    st.caption(f"🛡️ Rôle : **{user_role}**")
    st.caption(f"🏢 Service : **{user_service}**")
    st.divider()

    # Le conteneur du bas pour les actions globales
    st.link_button(
        "🏠 Retour au Portail HUB", url_portail_hub, use_container_width=True
    )
    st.write("")

    if st.button(
        "🚪 Se déconnecter", use_container_width=True, type="secondary"
    ):
      auth.deconnecter()