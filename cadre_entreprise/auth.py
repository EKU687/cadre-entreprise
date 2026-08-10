import bcrypt
from modules.database import supabase
import streamlit as st


def hacher_mot_de_passe(mdp_clair: str) -> str:
  """Hache un mot de passe en clair avec un sel bcrypt."""
  salt = bcrypt.gensalt()
  return bcrypt.hashpw(mdp_clair.encode("utf-8"), salt).decode("utf-8")


def verifier_mot_de_passe(mdp_saisi: str, mdp_hache: str) -> bool:
  """Vérifie un mot de passe saisi par rapport au hash stocké en BDD."""
  try:
    return bcrypt.checkpw(mdp_saisi.encode("utf-8"), mdp_hache.encode("utf-8"))
  except Exception:
    return False


def initialiser_session():
  """Initialise les variables d'état de session si elles n'existent pas."""
  if "connecte" not in st.session_state:
    st.session_state["connecte"] = False
  if "user_info" not in st.session_state:
    st.session_state["user_info"] = None


def est_connecte() -> bool:
  """Vérifie si l'utilisateur actuel est authentifié."""
  initialiser_session()
  return st.session_state["connecte"]


def get_user_info() -> dict:
  """Retourne le dictionnaire contenant les informations de l'utilisateur connecté."""
  initialiser_session()
  return st.session_state["user_info"]


def authentifier_utilisateur(login: str, mdp_saisi: str) -> bool:
  """Tente de connecter un utilisateur via la table 'Utilisateur' de Supabase."""
  initialiser_session()
  login_clean = login.lower().strip()

  try:
    res = (
        supabase.table("Utilisateur")
        .select("*")
        .eq("login", login_clean)
        .execute()
    )
    if res.data and verifier_mot_de_passe(
        mdp_saisi, res.data[0].get("mdp", "")
    ):
      st.session_state["connecte"] = True
      st.session_state["user_info"] = res.data[0]
      return True
    return False
  except Exception as e:
    st.error(f"❌ Erreur lors de l'authentification : {e}")
    return False


def deconnecter():
  """Réinitialise la session et déconnecte l'utilisateur."""
  st.session_state["connecte"] = False
  st.session_state["user_info"] = None
  st.rerun()