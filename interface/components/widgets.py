# interface/components/widgets.py
import streamlit as st
from typing import Optional, Callable, Any, List, Dict, Union
from datetime import datetime, timedelta
import time

class StyledButton:
    """
    Bouton personnalisé avec des styles prédéfinis pour différents usages.
    Permet de maintenir une cohérence visuelle dans l'application.
    """
    
    STYLES = {
        "primary": {
            "background": "linear-gradient(to right, #00B4DB, #0083B0)",
            "border": "none",
            "color": "white",
            "padding": "0.5rem 1rem",
            "border-radius": "5px",
            "cursor": "pointer"
        },
        "warning": {
            "background": "linear-gradient(to right, #f2994a, #f2c94c)",
            "border": "none",
            "color": "white"
        },
        "danger": {
            "background": "linear-gradient(to right, #ed213a, #93291e)",
            "border": "none",
            "color": "white"
        }
    }

    @staticmethod
    def render(
        label: str,
        key: str,
        style: str = "primary",
        on_click: Optional[Callable] = None,
        args: tuple = (),
        disabled: bool = False
    ) -> bool:
        """
        Affiche un bouton stylisé
        
        Args:
            label: Texte du bouton
            key: Identifiant unique du bouton
            style: Style à appliquer ("primary", "warning", "danger")
            on_click: Fonction à exécuter au clic
            args: Arguments pour la fonction on_click
            disabled: État désactivé du bouton
        
        Returns:
            bool: True si le bouton est cliqué
        """
        style_dict = StyledButton.STYLES.get(style, StyledButton.STYLES["primary"])
        
        button_html = f"""
        <button style="{'; '.join([f'{k}: {v}' for k, v in style_dict.items()])}"
                {' disabled' if disabled else ''}>
            {label}
        </button>
        """
        
        if st.markdown(button_html, unsafe_allow_html=True):
            if on_click and not disabled:
                on_click(*args)
            return True
        return False

class StatusIndicator:
    """
    Indicateur de statut visuel pour différents états
    (en cours, succès, erreur, etc.)
    """
    
    STATES = {
        "loading": {"icon": "⏳", "color": "blue", "text": "En cours..."},
        "success": {"icon": "✅", "color": "green", "text": "Succès"},
        "error": {"icon": "❌", "color": "red", "text": "Erreur"},
        "warning": {"icon": "⚠️", "color": "orange", "text": "Attention"},
        "idle": {"icon": "⭕", "color": "gray", "text": "En attente"}
    }

    @staticmethod
    def render(state: str, message: Optional[str] = None):
        """
        Affiche un indicateur de statut
        
        Args:
            state: État à afficher ("loading", "success", "error", etc.)
            message: Message personnalisé optionnel
        """
        status = StatusIndicator.STATES.get(state, StatusIndicator.STATES["idle"])
        display_message = message or status["text"]
        
        st.markdown(
            f"""
            <div style='color: {status["color"]}; display: flex; align-items: center;'>
                <span style='font-size: 1.2em; margin-right: 10px;'>{status["icon"]}</span>
                <span>{display_message}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

class TimeSelector:
    """Composant pour sélectionner une période de temps"""
    
    def __init__(self):
        self.periods = {
            "1h": "1 heure",
            "4h": "4 heures",
            "1d": "1 jour",
            "1w": "1 semaine",
            "1m": "1 mois"
        }

    @staticmethod
    def render(key: str, default: str = "1h") -> str:
        """Affiche un sélecteur de période"""
        return st.selectbox(
            "Période",
            options=["1h", "4h", "1d", "1w", "1m"],
            index=0,
            key=f"{key}_period",
            format_func=lambda x: {
                "1h": "1 heure",
                "4h": "4 heures",
                "1d": "1 jour",
                "1w": "1 semaine",
                "1m": "1 mois"
            }[x]
        )

class FormattedInput:
    """
    Champs de saisie formatés pour différents types de données
    (prix, pourcentage, montant, etc.)
    """
    
    @staticmethod
    def price_input(
        label: str,
        key: str,
        min_value: float = 0.0,
        default: float = 0.0
    ) -> float:
        """Champ de saisie pour les prix"""
        return st.number_input(
            label,
            min_value=min_value,
            value=default,
            format="%.8f",
            step=0.00000001,
            key=key
        )
    
    @staticmethod
    def percentage_input(
        label: str,
        key: str,
        min_value: float = 0.0,
        max_value: float = 100.0,
        default: float = 0.0
    ) -> float:
        """Champ de saisie pour les pourcentages"""
        return st.number_input(
            label,
            min_value=min_value,
            max_value=max_value,
            value=default,
            format="%.2f",
            step=0.1,
            key=key
        )
    
    @staticmethod
    def amount_input(
        label: str,
        key: str,
        currency: str = "USDT",
        min_value: float = 0.0,
        default: float = 0.0
    ) -> float:
        """Champ de saisie pour les montants"""
        col1, col2 = st.columns([4, 1])
        with col1:
            amount = st.number_input(
                label,
                min_value=min_value,
                value=default,
                format="%.2f",
                step=0.01,
                key=key
            )
        with col2:
            st.markdown(f"### {currency}")
        return amount

# Exemple d'utilisation
if __name__ == "__main__":
    st.title("Test des Widgets")
    
    # Test du bouton stylisé
    if StyledButton.render("Sauvegarder", "save_btn", "primary"):
        st.write("Bouton cliqué!")
    
    # Test de l'indicateur de statut
    StatusIndicator.render("loading", "Chargement des données...")
    
    # Test du sélecteur de temps
    period = TimeSelector.render("test_time")
    st.write(f"Période sélectionnée: {period}")
    
    # Test des champs de saisie formatés
    price = FormattedInput.price_input("Prix d'entrée", "entry_price")
    percentage = FormattedInput.percentage_input("Stop Loss (%)", "stop_loss")
    amount = FormattedInput.amount_input("Montant", "amount")