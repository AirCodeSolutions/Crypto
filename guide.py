# guide.py
import streamlit as st

class TradingGuide:
    @staticmethod
    def render_guide():
        st.title("📚 Guide de Trading Crypto Avancé")
        
        guide_section = st.selectbox(
            "Choisir une section",
            ["Démarrage Rapide", "Système de Scoring", "Trading Court Terme", 
             "Gestion de Position", "Signaux de Trading", "Indicateurs Techniques", 
             "Analyse Multi-Timeframes", "Gestion des Risques"]
        )
        
        if guide_section == "Démarrage Rapide":
            TradingGuide._quick_start_guide()
        elif guide_section == "Système de Scoring":
            TradingGuide._scoring_system_guide()
        elif guide_section == "Trading Court Terme":
            TradingGuide._short_term_trading_guide()
        elif guide_section == "Gestion de Position":
            TradingGuide._position_management_guide()
        elif guide_section == "Signaux de Trading":
            TradingGuide._trading_signals_guide()
        elif guide_section == "Indicateurs Techniques":
            TradingGuide._technical_indicators_guide()
        elif guide_section == "Analyse Multi-Timeframes":
            TradingGuide._multi_timeframe_guide()
        elif guide_section == "Gestion des Risques":
            TradingGuide._risk_management_guide()

    @staticmethod
    def _quick_start_guide():
        st.markdown("""
        ## 🚀 Guide de Démarrage Rapide
        
        ### 1. Configuration Initiale
        1. Définissez votre capital initial dans la section Portfolio
        2. Configurez vos paramètres de risque (1-2% par trade maximum)
        3. Commencez par suivre 2-3 cryptos principales
        
        ### 2. Premiers Pas
        1. Utilisez la page "Analyse en Direct" pour suivre vos cryptos
        2. Attendez les signaux avec un score > 0.7
        3. Vérifiez toujours le ratio risque/récompense (min 1:2)
        
        ### 3. Validation d'une Entrée
        - Score technique élevé
        - Volume confirmant
        - Plusieurs timeframes alignés
        
        ### 4. Gestion des Positions
        - Utilisez toujours des stops
        - Prenez des profits partiels
        - Suivez votre plan de trading
        """)

    @staticmethod
    def _scoring_system_guide():
        st.markdown("""
        ## 🎯 Comprendre le Système de Scoring

        ### 1. Composition du Score (0-1)
        
        #### Score Technique (70%)
        - **Tendance EMA (25%)**
            * 0.25: EMA9 > EMA20 > EMA50
            * 0.15: EMA9 > EMA20
            * 0.00: Pas de tendance claire
        
        - **Momentum RSI (25%)**
            * 0.25: RSI 40-60
            * 0.20: RSI < 30
            * 0.15: RSI 30-40 ou 60-70
            * 0.00: RSI > 70
        
        - **Volume (25%)**
            * 0.25: Volume > 150% moyenne
            * 0.15: Volume > 100% moyenne
            * 0.00: Volume < moyenne
        
        - **Risk/Reward (25%)**
            * 0.25: R/R ≥ 3
            * 0.15: R/R ≥ 2
            * 0.00: R/R < 2
        
        #### Score Contextuel (30%)
        - Multi-Timeframes (15%)
        - Volume Global (10%)
        - Volatilité (5%)
        
        ### 2. Interprétation
        
        | Score | Qualité | Action |
        |-------|----------|---------|
        | ≥ 0.8 | Excellent | Position size 100% |
        | ≥ 0.7 | Très bon | Position size 75% |
        | ≥ 0.6 | Bon | Position size 50% |
        | < 0.6 | Faible | Pas de trade |
        """)

    @staticmethod
    def _short_term_trading_guide():
        st.markdown("""
        ## ⚡ Guide du Trading Court Terme
        
        ### 1. QUAND ACHETER
        
        #### Conditions Primaires
        - Score global ≥ 0.7
        - RSI entre 30-40
        - Volume > moyenne
        - MACD en reprise
        
        #### Confirmations
        - Support proche (-1-2%)
        - Timeframes alignés
        - Pas de résistance proche
        
        ### 2. QUAND VENDRE
        
        #### Sortie en Profit
        - Target 1: +2-3%
        - RSI > 70
        - MACD baissier
        
        #### Sortie en Perte
        - Stop loss touché (-1%)
        - Support cassé
        - Volume baissier fort
        
        ### 3. MEILLEURS MOMENTS
        
        #### Heures Optimales (UTC)
        - 2-4h: Session Asie
        - 7-9h: Europe
        - 13-15h: USA
        """)

    @staticmethod
    def _position_management_guide():
        st.markdown("""
        ## 💼 Gestion des Positions
        
        ### 1. Entrée en Position
        
        #### Entrée Progressive
        ```
        - 50% au signal initial
        - 50% à la confirmation
        ```
        
        #### Stop Loss Initial
        ```
        - 1% sous l'entrée maximum
        - Ajuster selon la volatilité
        ```
        
        ### 2. Gestion Active
        
        #### Sorties Partielles
        ```
        1. 50% au premier objectif (+2%)
        2. 30% au second objectif (+3%)
        3. 20% avec stop trailing
        ```
        
        #### Ajustement des Stops
        ```
        1. Initial: -1%
        2. Breakeven: après +1%
        3. Trailing: 0.5% sous les plus hauts
        ```
        """)

    @staticmethod
    def _trading_signals_guide():
        st.markdown("""
        ## 🎯 Signaux de Trading
        
        ### 1. Signaux d'Achat
        
        #### Conditions Techniques
        - RSI: 30-40
        - MACD: Croisement haussier
        - Volume: > moyenne 20 périodes
        
        #### Force du Signal
        - 0.8-1.0: Très fort
        - 0.6-0.8: Fort
        - < 0.6: Faible
        
        ### 2. Confirmation des Signaux
        
        #### Étapes de Validation
        1. Vérifier plusieurs timeframes
        2. Confirmer le volume
        3. Valider le contexte
        
        #### Gestion des Faux Signaux
        1. Stops serrés
        2. Validation multi-indicateurs
        3. Patience et discipline
        """)

    @staticmethod
    def _risk_management_guide():
        st.markdown("""
        ## ⚠️ Gestion des Risques
        
        ### 1. Règles Fondamentales
        
        #### Risque par Position
        ```
        - Maximum 1-2% du capital
        - Stops systématiques
        - Position sizing adaptatif
        ```
        
        #### Risque Global
        ```
        - Max 5% du capital en risque
        - 3-4 positions maximum
        - Diversification des cryptos
        ```
        
        ### 2. Position Sizing
        
        #### Calcul de la Taille
        ```
        Taille = (Capital × %Risque) ÷ (Prix entrée - Stop loss)
        ```
        
        #### Ajustement selon Score
        - Score 0.8+: 100% taille calculée
        - Score 0.7-0.8: 75% taille calculée
        - Score 0.6-0.7: 50% taille calculée
        
        ### 3. Protection du Capital
        
        #### Règles de Survie
        1. Jamais de martingale
        2. Pas d'émotions
        3. Journal de trading
        4. Plan de trading strict
        """)

class Documentation:
    """Documentation des fonctionnalités de l'application"""
    
    @staticmethod
    def get_api_documentation():
        return {
            "exchange": {
                "description": "Interface avec KuCoin",
                "methods": [
                    "get_valid_symbol",
                    "fetch_ticker",
                    "fetch_ohlcv"
                ]
            },
            "indicators": {
                "description": "Indicateurs techniques",
                "methods": [
                    "calculate_rsi",
                    "calculate_support_resistance",
                    "detect_divergence"
                ]
            },
            "portfolio": {
                "description": "Gestion du portfolio",
                "methods": [
                    "add_position",
                    "update_positions",
                    "close_position"
                ]
            }
        }

    @staticmethod
    def get_error_codes():
        return {
            "E001": "Erreur de connexion à l'exchange",
            "E002": "Symbole invalide",
            "E003": "Capital insuffisant",
            "E004": "Erreur de calcul d'indicateur",
            "E005": "Position inexistante"
        }

# Fonction principale pour rendre le guide
def render_documentation():
    guide = TradingGuide()
    guide.render_guide()
