# interface/components/alerts.py
import streamlit as st
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Literal
from datetime import datetime
import time

@dataclass
class NotificationMessage:
    """Représente une notification ou une alerte"""
    message: str
    type: Literal["info", "success", "warning", "error"]
    timestamp: datetime = field(default_factory=datetime.now)
    is_read: bool = False
    details: Optional[Dict] = None
    
    def format_time(self) -> str:
        """Formate le timestamp pour l'affichage"""
        now = datetime.now()
        delta = now - self.timestamp
        
        if delta.days > 0:
            return f"Il y a {delta.days} jours"
        elif delta.seconds > 3600:
            return f"Il y a {delta.seconds // 3600}h"
        elif delta.seconds > 60:
            return f"Il y a {delta.seconds // 60}m"
        else:
            return "À l'instant"

class AlertSystem:
    """
    Système de gestion des alertes et notifications.
    Permet d'afficher différents types de messages et de gérer leur état.
    """
    
    def __init__(self):
        """Initialise le système d'alertes"""
        if 'notifications' not in st.session_state:
            st.session_state.notifications = []
    
    def add_notification(
        self,
        message: str,
        notification_type: Literal["info", "success", "warning", "error"],
        details: Optional[Dict] = None
    ):
        """
        Ajoute une nouvelle notification
        
        Args:
            message: Contenu principal de la notification
            notification_type: Type de la notification
            details: Informations supplémentaires (optionnel)
        """
        notification = NotificationMessage(
            message=message,
            type=notification_type,
            details=details
        )
        st.session_state.notifications.insert(0, notification)
    
    def clear_all(self):
        """Efface toutes les notifications"""
        st.session_state.notifications = []
    
    def mark_all_as_read(self):
        """Marque toutes les notifications comme lues"""
        for notif in st.session_state.notifications:
            notif.is_read = True
    
    def get_unread_count(self) -> int:
        """Retourne le nombre de notifications non lues"""
        return sum(1 for n in st.session_state.notifications if not n.is_read)

    def render(self):
        """Affiche l'interface des notifications"""
        with st.container():
            # En-tête avec compteur
            unread = self.get_unread_count()
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"### 🔔 Notifications ({unread} non lues)")
            
            with col2:
                if st.button("Tout marquer comme lu"):
                    self.mark_all_as_read()
                    
            with col3:
                if st.button("Effacer tout"):
                    if st.session_state.notifications:  # Vérification pour éviter une confirmation inutile
                        self.clear_all()
            
            # Affichage des notifications
            if not st.session_state.notifications:
                st.info("Aucune notification")
                return
            
            for notification in st.session_state.notifications:
                self._render_notification(notification)

    def _render_notification(self, notification: NotificationMessage):
        """
        Affiche une notification individuelle
        
        Args:
            notification: Notification à afficher
        """
        # Couleurs et icônes selon le type
        styles = {
            "info": {"icon": "ℹ️", "color": "blue"},
            "success": {"icon": "✅", "color": "green"},
            "warning": {"icon": "⚠️", "color": "orange"},
            "error": {"icon": "❌", "color": "red"}
        }
        
        style = styles[notification.type]
        
        with st.container():
            # Utilisation du markdown pour le style
            st.markdown(
                f"""
                <div style='padding: 10px; border-left: 3px solid {style['color']}; margin: 5px 0;'>
                    {style['icon']} {notification.message}
                </div>
                """,
                unsafe_allow_html=True
            )
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.caption(notification.format_time())
            
            # Affichage des détails si présents
            if notification.details:
                with st.expander("Voir les détails"):
                    for key, value in notification.details.items():
                        st.write(f"**{key}:** {value}")
            
            # Mise à jour du statut de lecture
            if not notification.is_read:
                notification.is_read = True

# Exemple d'utilisation:
if __name__ == "__main__":
    alert_system = AlertSystem()
    
    # Exemple d'ajout de différentes notifications
    alert_system.add_notification(
        "BTC/USDT a atteint votre prix cible de 50000$",
        "success",
        {"Prix actuel": "50000$", "Target": "50000$", "Gain": "+5%"}
    )
    
    alert_system.add_notification(
        "RSI en zone de survente sur ETH/USDT",
        "warning",
        {"RSI": "29.5", "Prix": "2800$"}
    )
    
    # Affichage des notifications
    alert_system.render()