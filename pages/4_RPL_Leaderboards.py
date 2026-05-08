import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from RPL_data_utils import apply_theme, load_batting, load_bowling, load_fielding

import json

st.set_page_config(page_title="Leaderboards | RPL", page_icon="🏆", layout="wide")
apply_theme()

bat = load_batting()
bowl = load_bowling()
field = load_fielding()

@st.cache_data
def load_auctions():
    auctions_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'auction_data.json')
    if os.path.exists(auctions_path):
        with open(auctions_path) as f:
            return json.load(f)
    return {}

auctions = load_auctions()

st.markdown("# 🏆 Leaderboards")
st.markdown("*All-time and per-season rankings*")
st.divider()

col1, col2 = st.columns([1, 1])
with col1:
    category = st.selectbox("Category", ["Batting", "Bowling", "Fielding", "Auction Points"])
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

elif category == "Fielding":
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

elif category == "Auction Points":
    auction_rows = []
    # Extract VFM data if available
    vfm_data = auctions.get("ValueIndex", {})
    career_vfm = vfm_data.get("Career", {})
    seasons_vfm = vfm_data.get("Seasons", {})

    for s_num, s_data in auctions.items():
        if s_num == "ValueIndex": continue
        if season_filter is not None and str(season_filter) != s_num:
            continue
        for p, price in s_data.items():
            if str(price).isdigit() or isinstance(price, (int, float)):
                vfm_val = 0
                if season_filter is None:
                    vfm_val = career_vfm.get(p, 0)
                else:
                    vfm_val = seasons_vfm.get(p, {}).get(s_num, 0)
                auction_rows.append({"player": p, "season": int(s_num), "points": int(price), "VFM": vfm_val})
    
    auc_df = pd.DataFrame(auction_rows)
    
    if auc_df.empty:
        agg = pd.DataFrame(columns=["Player", "Points", "Value Index"])
        display_cols = ["Player", "Points", "Value Index"]
    else:
        if season_filter is None:
            # For all-time, we calculate total points and avg points per season in auction
            agg = auc_df.groupby("player").agg({
                "points": ["sum", "count"],
                "VFM": "first"
            }).reset_index()
            agg.columns = ["player", "points_sum", "auction_seasons", "VFM"]
            agg["Avg Pts/Season"] = (agg["points_sum"] / agg["auction_seasons"]).round(0).astype(int)
            agg["VFM"] = agg["VFM"].round(2)
            
            bat_runs = bat.groupby("player")["runs"].sum().reset_index()
            bowl_wkts = bowl.groupby("player")["wickets"].sum().reset_index()
            
            agg = pd.merge(agg, bat_runs, on="player", how="left").fillna(0)
            agg = pd.merge(agg, bowl_wkts, on="player", how="left").fillna(0)
            
            agg["Runs / 1k Pts"] = (agg["runs"] / (agg["points_sum"] / 1000)).round(1)
            agg["Wkts / 1k Pts"] = (agg["wickets"] / (agg["points_sum"] / 1000)).round(2)
            
            agg = agg.sort_values("VFM", ascending=False).reset_index(drop=True)
            agg.index = agg.index + 1
            agg.columns = ["Player", "Total Pts", "Seasons", "Value Index", "Avg Pts/Season", "Runs", "Wickets", "Runs/1k Pts", "Wkts/1k Pts"]
            display_cols = ["Player", "Total Pts", "Avg Pts/Season", "Value Index", "Runs", "Wickets", "Runs/1k Pts", "Wkts/1k Pts"]
        else:
            agg = auc_df.copy()
            agg["VFM"] = agg["VFM"].round(2)
            agg["Avg Pts/Season"] = agg["points"] # For single season, avg is just the points
            s_bat = bat[bat['season'] == season_filter][["player", "runs"]]
            s_bowl = bowl[bowl['season'] == season_filter][["player", "wickets"]]
            
            agg = pd.merge(agg, s_bat, on="player", how="left").fillna(0)
            agg = pd.merge(agg, s_bowl, on="player", how="left").fillna(0)
            
            agg["Runs / 1k Pts"] = (agg["runs"] / (agg["points"] / 1000)).round(1)
            agg["Wkts / 1k Pts"] = (agg["wickets"] / (agg["points"] / 1000)).round(2)
            
            agg = agg.sort_values("VFM", ascending=False).reset_index(drop=True)
            agg.index = agg.index + 1
            agg.columns = ["Player", "Season", "Points", "Value Index", "Avg Pts/Season", "Runs", "Wickets", "Runs/1k Pts", "Wkts/1k Pts"]
            display_cols = ["Player", "Points", "Avg Pts/Season", "Value Index", "Runs", "Wickets", "Runs/1k Pts", "Wkts/1k Pts"]

st.markdown(f"### {category} — {'All-Time' if season_filter is None else f'Season {season_filter}'}")
if category == "Auction Points":
    st.info("**Relative Value Index:** A normalized efficiency metric that compares a player's runs, wickets, and dismissals against the season's top performers relative to their auction price.")
st.dataframe(agg[display_cols], use_container_width=True, height=600)
st.caption(f"Showing {len(agg)} players")
