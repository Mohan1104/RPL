import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shared_utils import apply_theme, load_batting, load_bowling, load_fielding, load_players

st.set_page_config(page_title="RPL Tournament Analytics", page_icon="🏏", layout="wide", initial_sidebar_state="expanded")
apply_theme()

st.markdown("# :material/sports_cricket: RPL Cricket Analytics")
st.markdown("Analysis of the 5 seasons of the **Ryland Premier League**")

bat = load_batting()
bowl = load_bowling()
field = load_fielding()
players = load_players()

# Summary Metrics in a bordered container
with st.container(border=True):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Seasons", bat['season'].nunique(), help="Total recorded seasons")
    c2.metric("Players", len(players), help="Total unique players")
    c3.metric("Batting Records", len(bat))
    c4.metric("Bowling Records", len(bowl))

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("### :material/workspace_premium: All-Time Leaders")
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown("#### Top Run Scorers")
        agg = bat.groupby('player')['runs'].sum().reset_index().sort_values('runs', ascending=False).head(10)
        agg.index = range(1, len(agg)+1)
        agg.columns = ['Player', 'Runs']
        st.dataframe(agg, use_container_width=True)

with col2:
    with st.container(border=True):
        st.markdown("#### Top Wicket Takers") 
        agg = bowl.groupby('player')['wickets'].sum().reset_index().sort_values('wickets', ascending=False).head(10)
        agg.index = range(1, len(agg)+1)
        agg.columns = ['Player', 'Wickets']
        st.dataframe(agg, use_container_width=True)

st.markdown("<br><br>", unsafe_allow_html=True)

with st.expander(":material/explore: Explore the Analytics Dashboard", expanded=True):
    st.page_link("pages/0_RPL_Team_Squads.py", label="**Team Squads** — Rosters, captains, and auction values", icon="🏟️")
    st.page_link("pages/1_RPL_Player_Profile.py", label="**Player Profile** — Deep-dive into individual season-by-season performance", icon="👤")
    st.page_link("pages/2_RPL_Player_Comparison.py", label="**Player Comparison** — Head-to-head metrics comparison", icon="📊")
    st.page_link("pages/3_RPL_Allrounder_Index.py", label="**All-Rounder Index** — Radar charts for multi-dimensional skill analysis", icon="🕸️")
    st.page_link("pages/4_RPL_Leaderboards.py", label="**Leaderboards** — Seasonal and career rankings", icon="🏆")
    st.page_link("pages/5_RPL_Match_Results.py", label="**Match Results** — Points tables and head-to-head records", icon="📋")
