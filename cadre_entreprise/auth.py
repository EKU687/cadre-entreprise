# =====================================================================
# SDK CADRE_ENTREPRISE - MODULE AUTHENTIFICATION (auth.py)
# =====================================================================
import bcrypt
import streamlit as st
from cadre_entreprise.database import supabase


def hacher_mot_de_passe(mot_de_passe_clair: str) -> str:
  """Génère un hash Bcrypt sécurisé à partir d'un mot de passe en texte clair."""
  if not mot_de_passe_clair:
    return ""
  bytes_mdp = mot_de_passe_clair.encode("utf-8")
  return bcrypt.hashpw(bytes_mdp, bcrypt.gensalt()).decode("utf-8")


def connecter(login: str, mdp_saisi: str):
  """Vérifie le login/mdp dans Supabase et initialise la session Streamlit.

  Gère également le cas du changement de mot de passe obligatoire.
  """
  login_clean = str(login).lower().strip()

  if not login_clean or not mdp_saisi:
    return False, "⚠️ Veuillez remplir tous les champs."

  try:
    res = (
        supabase.table("Utilisateur")
        .select("*")
        .eq("login", login_clean)
        .execute()
    )

    if not res.data or len(res.data) == 0:
      return False, "❌ Identifiant ou mot de passe incorrect."

    user = res.data[0]
    hash_stocke = user.get("mdp", "")

    # Vérification du mot de passe via Bcrypt
    if bcrypt.checkpw(
        mdp_saisi.encode("utf-8"), hash_stocke.encode("utf-8")
    ):

      # 🎯 CAS 1 : Première connexion -> Changement de MDP obligatoire
      if user.get("changement_mdp_requis", False):
        st.session_state["doit_changer_mdp"] = True
        st.session_state["user_temp"] = user
        return (
            True,
            "🔒 Première connexion : Veuillez choisir un nouveau mot de passe.",
        )

      # 🎯 CAS 2 : Connexion normale
      st.session_state["utilisateur"] = user
      st.session_state["connecte"] = True
      st.session_state["doit_changer_mdp"] = False
      return True, f"✅ Bienvenue {user.get('nom', login_clean)} !"
    else:
      return False, "❌ Identifiant ou mot de passe incorrect."

  except Exception as e:
    return False, f"❌ Erreur de connexion : {e}"


def changer_mot_de_passe(login: str, nouveau_mdp: str):
  """Met à jour le mot de passe dans Supabase et repasse 'changement_mdp_requis' à False."""
  try:
    hash_securise = hacher_mot_de_passe(nouveau_mdp)

    supabase.table("Utilisateur").update({
        "mdp": hash_securise,
        "changement_mdp_requis": False,
    }).eq("login", str(login).lower().strip()).execute()

    return True, "✅ Mot de passe mis à jour avec succès !"
  except Exception as e:
    return False, f"❌ Erreur lors du changement de mot de passe : {e}"


def deconnecter():
  """Réinitialise la session utilisateur et recharge la page."""
  st.session_state["utilisateur"] = None
  st.session_state["connecte"] = False
  st.session_state["doit_changer_mdp"] = False
  st.session_state["mode_edition"] = False
  st.rerun()


def est_connecte() -> bool:
  """Vérifie si un utilisateur est actuellement authentifié dans la session."""
  return st.session_state.get("connecte", False) and not st.session_state.get(
      "doit_changer_mdp", False
  )


def get_user_info() -> dict:
  """Renvoie le dictionnaire d'informations du compte connecté."""
  return st.session_state.get("utilisateur", {}) or {}