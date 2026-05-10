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

SHORT = {
    'Gully Boyz': 'GB',
    'Ryland Challengers Birmingham': 'RCB',
    'Ryland Super Kings': 'RSK',
    'Ryland Royals': 'RR',
}

def apply_theme():
    """Apply dark premium theme CSS from styles.css."""
    styles_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'styles.css')
    if os.path.exists(styles_path):
        with open(styles_path) as f:
            st.html(f"<style>{f.read()}</style>")
    
    # Hide the standard Streamlit header/footer for a cleaner look
    st.html("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stMainBlockContainer {padding-top: 1rem;}
    </style>
    """)

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

@st.cache_data
def load_rosters():
    rosters_path = os.path.join(DATA_DIR, 'team_rosters.json')
    if os.path.exists(rosters_path):
        with open(rosters_path) as f:
            return json.load(f)
    return {}

@st.cache_data
def load_results():
    results_path = os.path.join(DATA_DIR, 'match_results.json')
    if os.path.exists(results_path):
        with open(results_path) as f:
            return json.load(f)
    return []

@st.cache_data
def load_auctions():
    auctions_path = os.path.join(DATA_DIR, 'auction_data.json')
    if os.path.exists(auctions_path):
        with open(auctions_path) as f:
            return json.load(f)
    return {}

@st.cache_data
def load_bios():
    bios_path = os.path.join(DATA_DIR, 'player_bios.json')
    if os.path.exists(bios_path):
        with open(bios_path) as f:
            return json.load(f)
    return {}
