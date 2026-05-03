import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from RPL_data_utils import apply_theme, load_batting, load_bowling, load_fielding

st.set_page_config(page_title="Leaderboards | RPL", page_icon="🏆", layout="wide")
apply_theme()

bat = load_batting()
bowl = load_bowling()
field = load_fielding()

st.markdown("# 🏆 Leaderboards")
st.markdown("*All-time and per-season rankings*")
st.divider()

col1, col2 = st.columns([1, 1])
with col1:
    category = st.selectbox("Category", ["Batting", "Bowling", "Fielding"])
with col2:
    season_opts = ["All-Time"] + [f"Season {s}" for s in range(1, 6)]
    season_sel = st.selectbox("Season", season_opts)

st.divider()

if season_sel == "All-Time":
    season_filter = None
else:
    season_filter = int(season_sel.split()[-1])

if category == "Batting":
    data = bat if season_filter is None else bat[bat['season'] == season_filter]
    if season_filter is None:
        agg = data.groupby('player').agg(
            Team=('team', 'last'),
            Mat=('matches', 'sum'),
            Inns=('innings', 'sum'),
            Runs=('runs', 'sum'),
            HS=('highest', 'max'),
            NO=('not_outs', 'sum'),
            Fours=('fours', 'sum'),
            Sixes=('sixes', 'sum'),
            Fifties=('fifties', 'sum'),
            Hundreds=('hundreds', 'sum'),
        ).reset_index()
        agg['Avg'] = (agg['Runs'] / (agg['Inns'] - agg['NO']).clip(lower=1)).round(2)
        agg = agg.sort_values('Runs', ascending=False).reset_index(drop=True)
        agg.index = agg.index + 1
        agg = agg.rename(columns={'player': 'Player'})
        display_cols = ['Player', 'Team', 'Mat', 'Inns', 'Runs', 'HS', 'Avg', 'Fours', 'Sixes', 'Fifties', 'Hundreds']
    else:
        agg = data[['player','team','matches','innings','runs','balls','highest','not_outs',
                     'average','strike_rate','fours','sixes','fifties','hundreds']].copy()
        agg = agg.sort_values('runs', ascending=False).reset_index(drop=True)
        agg.index = agg.index + 1
        agg.columns = ['Player','Team','Mat','Inns','Runs','Balls','HS','NO','Avg','SR','4s','6s','50s','100s']
        display_cols = list(agg.columns)

elif category == "Bowling":
    data = bowl if season_filter is None else bowl[bowl['season'] == season_filter]
    if season_filter is None:
        agg = data.groupby('player').agg(
            Team=('team', 'last'),
            Mat=('matches', 'sum'),
            Inns=('innings', 'sum'),
            Overs=('overs', 'sum'),
            Runs=('runs', 'sum'),
            Wickets=('wickets', 'sum'),
            Best=('best_figures', 'max'),
            Maidens=('maidens', 'sum'),
        ).reset_index()
        agg['Avg'] = (agg['Runs'] / agg['Wickets'].clip(lower=1)).round(2)
        agg['Econ'] = (agg['Runs'] / agg['Overs'].clip(lower=0.1)).round(2)
        agg = agg.sort_values('Wickets', ascending=False).reset_index(drop=True)
        agg.index = agg.index + 1
        agg = agg.rename(columns={'player': 'Player'})
        agg['Overs'] = agg['Overs'].round(1)
        display_cols = ['Player', 'Team', 'Mat', 'Overs', 'Runs', 'Wickets', 'Best', 'Avg', 'Econ', 'Maidens']
    else:
        agg = data[['player','team','matches','innings','overs','runs','wickets',
                     'best_figures','maidens','average','economy','strike_rate']].copy()
        agg = agg.sort_values('wickets', ascending=False).reset_index(drop=True)
        agg.index = agg.index + 1
        agg.columns = ['Player','Team','Mat','Inns','Overs','Runs','Wkts','Best','Mdns','Avg','Econ','SR']
        display_cols = list(agg.columns)

else:  # Fielding
    data = field if season_filter is None else field[field['season'] == season_filter]
    if season_filter is None:
        agg = data.groupby('player').agg(
            Team=('team', 'last'),
            Mat=('matches', 'sum'),
            Dismissals=('dismissals', 'sum'),
            Catches=('catches', 'sum'),
            CaughtBowled=('caught_bowled', 'sum'),
            RunOuts=('run_outs', 'sum'),
            AssistRO=('assist_runouts', 'sum'),
            Stumpings=('stumpings', 'sum'),
        ).reset_index()
        agg = agg.sort_values('Dismissals', ascending=False).reset_index(drop=True)
        agg.index = agg.index + 1
        agg = agg.rename(columns={'player': 'Player'})
        display_cols = ['Player', 'Team', 'Mat', 'Dismissals', 'Catches', 'CaughtBowled', 'RunOuts', 'AssistRO', 'Stumpings']
    else:
        agg = data[['player','team','matches','dismissals','catches','caught_bowled',
                     'caught_behind','run_outs','assist_runouts','stumpings']].copy()
        agg = agg.sort_values('dismissals', ascending=False).reset_index(drop=True)
        agg.index = agg.index + 1
        agg.columns = ['Player','Team','Mat','Dismissals','Catches','C&B','C Behind','Run Outs','Assist RO','Stumpings']
        display_cols = list(agg.columns)

st.markdown(f"### {category} — {'All-Time' if season_filter is None else f'Season {season_filter}'}")
st.dataframe(agg[display_cols], use_container_width=True, height=600)
st.caption(f"Showing {len(agg)} players")
