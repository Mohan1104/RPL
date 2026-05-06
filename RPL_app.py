import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from RPL_data_utils import apply_theme, load_batting, load_bowling, load_fielding, load_players

st.set_page_config(page_title="RPL Tournament Analytics", page_icon="🏏", layout="wide", initial_sidebar_state="expanded")
apply_theme()

st.markdown("# 🏏 RPL Cricket Analytics")
st.markdown("*Analysis of the 5 seasons of the Ryland Premier League*")
st.divider()

bat = load_batting()
bowl = load_bowling()
field = load_fielding()
players = load_players()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Seasons", bat['season'].nunique())
c2.metric("Players", len(players))
c3.metric("Batting Records", len(bat))
c4.metric("Bowling Records", len(bowl))

st.divider()

st.markdown("### 🏆 Quick Highlights")
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Top Run Scorers (All-Time)")
    agg = bat.groupby('player')['runs'].sum().reset_index().sort_values('runs', ascending=False).head(10)
    agg.index = range(1, len(agg)+1)
    agg.columns = ['Player', 'Total Runs']
    st.dataframe(agg, use_container_width=True)

with col2:
    st.markdown("#### Top Wicket Takers (All-Time)")
    agg = bowl.groupby('player')['wickets'].sum().reset_index().sort_values('wickets', ascending=False).head(10)
    agg.index = range(1, len(agg)+1)
    agg.columns = ['Player', 'Total Wickets']
    st.dataframe(agg, use_container_width=True)

st.divider()
st.markdown("#### 📌 Navigate using the sidebar to explore:")
st.markdown("""
- **Team Squads** — Rosters, captains, marquee players and championship titles
- **Player Profile** — Deep-dive into any player's season-by-season performance
- **Player Comparison** — Compare runs, wickets, or fielding across multiple players  
- **All-Rounder Index** — Radar chart comparison of all-round ability
- **Leaderboards** — Season and all-time rankings for batting, bowling & fielding
- **Match Results** — Season-by-season match results, points tables and head-to-head records
""")
