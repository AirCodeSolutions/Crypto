# interface/components/styles.py

MOBILE_STYLES = """
<style>
@media (max-width: 640px) {
    /* Boutons */
    .stButton button {
        width: 100%;
        margin: 0.5rem 0;
    }
    
    /* Sélecteurs */
    .row-widget.stSelectbox {
        min-width: 100%;
    }
    
    /* Conteneur principal */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 0.5rem;
        padding-right: 0.5rem;
    }
    
    /* Métriques */
    .metric-container {
        font-size: 0.9rem !important;
    }
    .metric-value {
        word-break: break-word;
    }
    
    /* Colonnes */
    .column > div {
        padding: 0.5rem 0;
    }
    
    /* Expandeurs */
    .streamlit-expanderHeader {
        font-size: 0.9rem;
    }
}
</style>
"""