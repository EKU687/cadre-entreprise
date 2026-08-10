import streamlit as st
from supabase import Client, create_client


@st.cache_resource
def get_supabase_client() -> Client:
  """Initialise et met en cache la connexion au client Supabase via secrets.toml.

  Returns:
      Client: L'instance configurée du client Supabase.
  """
  try:
    url_supabase = st.secrets["SUPABASE_URL"]
    key_supabase = st.secrets["SUPABASE_KEY"]
    return create_client(url_supabase, key_supabase)
  except Exception as e:
    st.error(
        f"❌ [DATABASE ERROR] Impossible d'initialiser Supabase : {e}.\n"
        "Vérifiez que le fichier `.streamlit/secrets.toml` contient bien"
        " 'SUPABASE_URL' et 'SUPABASE_KEY'."
    )
    st.stop()


# Instance globale réutilisable
supabase = get_supabase_client()