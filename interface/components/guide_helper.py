# interface/components/guide_helper.py
import streamlit as st

class GuideHelper:
    """Composant d'aide et de guide"""
    
    @staticmethod
    def show_indicator_help():
        """Affiche l'aide pour les indicateurs"""
        with st.expander("❓ Comprendre les indicateurs", expanded=False):
            st.markdown("""
                ### 📊 Indicateurs Techniques
                
                #### Score Technique (0-1)
                - > 0.8 : Configuration idéale
                - > 0.7 : Signal favorable
                - < 0.7 : Attendre meilleure opportunité
                
                #### RSI (0-100)
                - < 30 : Survente (opportunité d'achat)
                - 30-70 : Zone neutre
                - > 70 : Surachat (risqué pour l'achat)
                
                #### Volume
                Important pour confirmer les mouvements :
                - Volume > moyenne : Mouvement plus fiable
                - Volume faible : Prudence conseillée
                
                #### Signaux
                - STRONG_BUY : Très forte opportunité
                - BUY : Bonne opportunité
                - NEUTRAL : Pas de signal clair
                - SELL : Signal de vente
            """)

    @staticmethod
    def show_quick_guide():
        """Affiche un guide rapide pour le trading"""
        with st.expander("📚 Guide Rapide", expanded=False):
            st.markdown("""
                ### 🚀 Guide de Trading Rapide
                
                #### 1. Paramètres Recommandés
                - Capital initial: 100€ maximum pour débuter
                - Risque par trade: 1.5% maximum
                - Stop loss: Toujours en place
                
                #### 2. Configuration Idéale
                - Score > 0.7
                - RSI entre 30-45
                - Volume en augmentation
                - Signal BUY ou STRONG_BUY
                
                #### 3. Gestion des Risques
                - Maximum 2 positions simultanées
                - Prise de profits à +3%
                - Stop loss à -1.5%
                
                #### 4. Points d'Attention
                - Vérifier plusieurs timeframes
                - Surveiller le volume
                - Ne pas forcer les trades
            """)