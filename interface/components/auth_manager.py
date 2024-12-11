# interface/components/auth_manager.py
import streamlit as st
import hashlib
import time
from typing import Optional, Dict, Tuple
from services.storage import AirtableService

class AuthManager:
    """Gère l'authentification et les sessions utilisateur"""
    
    def __init__(self, airtable_service: AirtableService):
        self.airtable = airtable_service
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
        if 'user_info' not in st.session_state:
            st.session_state.user_info = None

    def hash_password(self, password: str) -> str:
        """Hash le mot de passe de manière sécurisée"""
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username: str, email: str, password: str) -> Tuple[bool, str]:
        """
        Enregistre un nouvel utilisateur
        Retourne (succès, message)
        """
        try:
            # Vérification si l'utilisateur existe déjà
            formula = f"OR({{Username}}='{username}', {{Email}}='{email}')"
            existing_users = self.airtable.utilisateurs.first(formula=formula)
            
            if existing_users:
                return False, "Nom d'utilisateur ou email déjà utilisé"
                
            # Création du nouvel utilisateur avec des champs séparés
            user_data = {
                "Username": username,
                "Email": email,
                "Password": self.hash_password(password),
                "Status": "pending",  # En attente de validation
                "Created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "Initial_capital": 1000,  # Valeur par défaut
                "Risk_per_trade": 1.5     # Valeur par défaut
            }
            
            self.airtable.utilisateurs.create(user_data)
            return True, "Inscription réussie ! En attente de validation."
            
        except Exception as e:
            return False, f"Erreur lors de l'inscription: {str(e)}"

    def login(self, username: str, password: str) -> Tuple[bool, str]:
        """
        Authentifie un utilisateur
        Retourne (succès, message)
        """
        try:
            # Recherche de l'utilisateur
            formula = f"{{Username}}='{username}'"
            user = self.airtable.utilisateurs.first(formula=formula)
            
            if not user:
                return False, "Utilisateur non trouvé"
                
            # Vérification du mot de passe
            if user['fields']['Password'] != self.hash_password(password):
                return False, "Mot de passe incorrect"
                
            # Vérification du statut
            if user['fields']['Status'] != "active":
                return False, "Compte en attente de validation"
                
            # Connexion réussie - stockage des paramètres séparés
            st.session_state.logged_in = True
            st.session_state.user_info = {
                'id': user['id'],
                'username': user['fields']['Username'],
                'email': user['fields']['Email'],
                'settings': {
                    'initial_capital': float(user['fields'].get('Initial_capital', 1000)),
                    'risk_per_trade': float(user['fields'].get('Risk_per_trade', 1.5))
                }
            }
            
            return True, "Connexion réussie !"
            
        except Exception as e:
            return False, f"Erreur lors de la connexion: {str(e)}"

    def logout(self):
        """Déconnecte l'utilisateur"""
        st.session_state.logged_in = False
        st.session_state.user_info = None

    def render_login_form(self):
        """Affiche le formulaire de connexion"""
        st.markdown("## 🔐 Connexion")
        
        with st.form("login_form"):
            username = st.text_input("Nom d'utilisateur")
            password = st.text_input("Mot de passe", type="password")
            
            submitted = st.form_submit_button("Se connecter")
            
            if submitted:
                success, message = self.login(username, password)
                if success:
                    st.success(message)
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(message)

    def render_register_form(self):
        """Affiche le formulaire d'inscription"""
        st.markdown("## 📝 Inscription")
        
        with st.form("register_form"):
            username = st.text_input("Nom d'utilisateur")
            email = st.text_input("Email")
            password = st.text_input("Mot de passe", type="password")
            password_confirm = st.text_input("Confirmer le mot de passe", type="password")
            
            submitted = st.form_submit_button("S'inscrire")
            
            if submitted:
                if not all([username, email, password, password_confirm]):
                    st.error("Veuillez remplir tous les champs")
                elif password != password_confirm:
                    st.error("Les mots de passe ne correspondent pas")
                else:
                    success, message = self.register(username, email, password)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

    def update_user_settings(self, user_id: str, new_capital: float, new_risk: float) -> bool:
        """Met à jour les paramètres de l'utilisateur"""
        try:
            self.airtable.utilisateurs.update(
                user_id,
                {
                    "Initial_capital": new_capital,
                    "Risk_per_trade": new_risk
                }
            )
            
            # Mise à jour des informations en session
            if st.session_state.user_info:
                st.session_state.user_info['settings'] = {
                    "initial_capital": new_capital,
                    "risk_per_trade": new_risk
                }
            
            return True
        except Exception as e:
            st.error(f"Erreur lors de la mise à jour des paramètres: {str(e)}")
            return False