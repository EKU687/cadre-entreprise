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
    """Vérifie le login/mdp dans Supabase et initialise la session Streamlit."""
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
            st.session_state["utilisateur"] = user
            st.session_state["connecte"] = True
            return True, f"✅ Bienvenue {user.get('nom', login_clean)} !"
        else:
            return False, "❌ Identifiant ou mot de passe incorrect."

    except Exception as e:
        return False, f"❌ Erreur de connexion : {e}"


def changer_mon_mot_de_passe(
    login: str, mdp_actuel: str, nouveau_mdp: str
) -> tuple[bool, str]:
    """Permet à un utilisateur connecté de modifier son propre mot de passe.

    Vérifie d'abord que le mot de passe actuel saisi est valide.
    """
    login_clean = str(login).lower().strip()

    if not mdp_actuel or not nouveau_mdp:
        return False, "⚠️ Veuillez remplir tous les champs du formulaire."

    if len(nouveau_mdp) < 6:
        return (
            False,
            "⚠️ Le nouveau mot de passe doit contenir au moins 6 caractères.",
        )

    try:
        # 1. Vérification du mot de passe actuel en base de données
        res = (
            supabase.table("Utilisateur")
            .select("mdp")
            .eq("login", login_clean)
            .execute()
        )

        if not res.data or len(res.data) == 0:
            return False, "❌ Utilisateur introuvable."

        hash_actuel = res.data[0].get("mdp", "")

        if not bcrypt.checkpw(
            mdp_actuel.encode("utf-8"), hash_actuel.encode("utf-8")
        ):
            return False, "❌ Le mot de passe actuel est incorrect."

        # 2. Hachage du nouveau mot de passe et mise à jour dans Supabase
        nouveau_hash = hacher_mot_de_passe(nouveau_mdp)

        supabase.table("Utilisateur").update({"mdp": nouveau_hash}).eq(
            "login", login_clean
        ).execute()

        # 3. Mise à jour du dictionnaire utilisateur en session si connecté
        if (
            st.session_state.get("utilisateur")
            and st.session_state["utilisateur"].get("login") == login_clean
        ):
            st.session_state["utilisateur"]["mdp"] = nouveau_hash

        return True, "✅ Votre mot de passe a été modifié avec succès !"

    except Exception as e:
        return False, f"❌ Erreur lors du changement de mot de passe : {e}"


def charger_droits_utilisateur(login: str, code_app: str) -> dict:
    """
    Interroge la table Autorisation de Supabase pour récupérer 
    le rôle et le périmètre de l'utilisateur sur une application spécifique.
    """
    try:
        res = (
            supabase.table("Autorisation")
            .select("role, perimetre")
            .eq("login", login)
            .eq("code_app", code_app)
            .execute()
        )

        if res.data and len(res.data) > 0:
            row = res.data[0]
            return {
                "acces": True,
                "role": row.get("role", "UTILISATEUR"),
                "perimetre": row.get("perimetre", "RESTREINT"),
            }
        else:
            # Si aucune ligne n'est trouvée -> Pas d'accès
            return {"acces": False, "role": "AUCUN", "perimetre": "AUCUN"}

    except Exception as e:
        print(f"⚠️ Erreur lors du chargement des droits : {e}")
        return {"acces": False, "role": "ERREUR", "perimetre": "AUCUN"}


def charger_contexte_securite(login: str, code_app: str = "IDENTIS") -> dict:
    """
    Nouveau : Récupère l'identité complète de l'utilisateur, sa Direction de rattachement
    ET son niveau d'habilitation pour une application donnée.
    """
    login_clean = str(login).lower().strip()
    
    # 1. Chargement des droits de l'app
    droits = charger_droits_utilisateur(login_clean, code_app)
    
    if not droits["acces"]:
        return {
            "login": login_clean,
            "nom": login_clean,
            "sigle_direction": "NON DÉFINI",
            "acces": False,
            "role": "AUCUN",
            "perimetre": "AUCUN"
        }

    # 2. Chargement des infos utilisateur et de sa direction
    sigle_direction = "DSF"  # Valeur par défaut
    nom_user = login_clean

    try:
        res_u = supabase.table("Utilisateur").select("nom, service").eq("login", login_clean).execute()
        if res_u.data:
            nom_user = res_u.data[0].get("nom", login_clean)
            service_code = res_u.data[0].get("service")

            # Récupération de la Direction associée au Service
            if service_code:
                res_s = supabase.table("Services").select("Directions(sigle_direction)").eq("sigle_service", service_code).execute()
                if res_s.data and res_s.data[0].get("Directions"):
                    sigle_direction = res_s.data[0]["Directions"].get("sigle_direction", "DSF")

    except Exception as err:
        print(f"⚠️ Erreur lors du calcul du périmètre direction : {err}")

    return {
        "login": login_clean,
        "nom": nom_user,
        "sigle_direction": sigle_direction,
        "acces": True,
        "role": droits["role"],
        "perimetre": droits["perimetre"]
    }


def deconnecter():
    """Réinitialise la session utilisateur et force la redirection vers le portail central."""
    # 1. Nettoyage de la session
    st.session_state["utilisateur"] = None
    st.session_state["connecte"] = False
    st.session_state["mode_edition"] = False

    # 2. Double technique de redirection (JS + Meta Refresh)
    url_portail = "https://portail-gnc.streamlit.app"
    redirection_code = f"""
        <meta http-equiv="refresh" content="0; url={url_portail}">
        <script>
            window.top.location.href = "{url_portail}";
        </script>
    """
    st.html(redirection_code)

    # 3. 🛑 LE COUP DE FREIN MAGIQUE
    st.stop()


def est_connecte() -> bool:
    """Vérifie si un utilisateur est actuellement authentifié dans la session."""
    return bool(
        st.session_state.get("connecte", False)
        and st.session_state.get("utilisateur")
    )


def get_user_info() -> dict:
    """Renvoie le dictionnaire d'informations du compte connecté."""
    return st.session_state.get("utilisateur", {}) or {}