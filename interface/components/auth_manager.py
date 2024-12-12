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

    def _check_existing_user(self, username: str, email: str) -> bool:
        """Vérifie si un utilisateur existe déjà"""
        try:
            # Récupérer tous les enregistrements et vérifier manuellement
            records = self.airtable._utilisateurs.all()
            
            for record in records:
                fields = record.get('fields', {})
                if fields.get('name') == username or fields.get('email') == email:
                    return True
            return False
            
        except Exception as e:
            print(f"Erreur lors de la vérification de l'utilisateur: {str(e)}")
            return True  # En cas d'erreur, on suppose que l'utilisateur existe

    def register(self, username: str, email: str, password: str) -> Tuple[bool, str]:
        """
        Enregistre un nouvel utilisateur
        Retourne (succès, message)
        """
        try:
            
            # Vérification si l'utilisateur existe déjà
            if self._check_existing_user(username, email):
                return False, "Nom d'utilisateur ou email déjà utilisé"
                
            # Création du nouvel utilisateur avec des champs séparés
            user_data = {
                "name": username,
                "email": email,
                "password": self.hash_password(password),
                "status": "pending",
                #"created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "created_at": time.strftime("%d-%m-%Y %H:%M:%S"),
                "capital": 1000,
                "risk": 1.5
            }
            
            self.airtable._utilisateurs.create(user_data)
            return True, "Inscription réussie ! En attente de validation."
            
        except Exception as e:
            return False, f"Erreur lors de l'inscription: {str(e)}"

    def login(self, username: str, password: str) -> Tuple[bool, str]:
        """
        Authentifie un utilisateur
        Retourne (succès, message)
        """
        try:
            # Récupérer tous les utilisateurs et chercher une correspondance
            records = self.airtable._utilisateurs.all()
            user = None
            
            for record in records:
                fields = record.get('fields', {})
                if fields.get('name') == username:
                    user = record
                    break
            
            if not user:
                return False, "Utilisateur non trouvé"
                
            # Vérification du mot de passe
            if user['fields']['password'] != self.hash_password(password):
                return False, "Mot de passe incorrect"
                
            # Vérification du statut
            if user['fields']['status'] != "active":
                return False, "Compte en attente de validation"
                
            # Connexion réussie
            st.session_state.logged_in = True
            st.session_state.user_info = {
                'id': user['id'],
                'username': user['fields']['name'],
                'email': user['fields']['email'],
                'settings': {
                    'initial_capital': float(user['fields'].get('capital', 1000)),
                    'risk_per_trade': float(user['fields'].get('risk', 1.5))
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
            self.airtable._utilisateurs.update(
                user_id,
                {
                    "capital": new_capital,
                    "risk": new_risk
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