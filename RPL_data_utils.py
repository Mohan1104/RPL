"""Shared data loading and theme utilities for all pages."""
import streamlit as st
import pandas as pd
import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

# Color palette
COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#f43f5e', '#8b5cf6', '#06b6d4', '#ec4899', '#84cc16']
TEAM_COLORS = {
    'Gully Boyz': '#10b981',
    'Ryland Challengers Birmingham': '#f43f5e',
    'Ryland Super Kings': '#f59e0b',
    'Ryland Royals': '#8b5cf6',
}

def apply_theme():
    """Apply dark premium theme CSS."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .block-container { max-width: 1200px; padding-top: 2rem; }
    .stMetric { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px; padding: 16px; }
    .stMetric:hover { border-color: rgba(255,255,255,0.15); }
    [data-testid="stMetricValue"] { font-size: 1.8rem; font-weight: 800; }
    h1 { font-weight: 800 !important; }
    h2, h3 { font-weight: 700 !important; }
    div[data-testid="stSidebar"] { background: rgba(10,14,26,0.95); }
    .stDataFrame { border-radius: 12px; overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_batting():
    with open(os.path.join(DATA_DIR, 'batting.json')) as f:
        return pd.DataFrame(json.load(f))

@st.cache_data
def load_bowling():
    with open(os.path.join(DATA_DIR, 'bowling.json')) as f:
        return pd.DataFrame(json.load(f))

@st.cache_data
def load_fielding():
    with open(os.path.join(DATA_DIR, 'fielding.json')) as f:
        return pd.DataFrame(json.load(f))

@st.cache_data
def load_players():
    with open(os.path.join(DATA_DIR, 'players.json')) as f:
        return json.load(f)

def get_player_list():
    return sorted([p['name'] for p in load_players()])
