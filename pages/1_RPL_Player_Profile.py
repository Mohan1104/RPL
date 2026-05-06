import streamlit as st
import plotly.graph_objects as go
import sys, os, json, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from RPL_data_utils import apply_theme, load_batting, load_bowling, load_fielding, get_player_list, COLORS, TEAM_COLORS

st.set_page_config(page_title="Player Profile | RPL", page_icon="👤", layout="wide")
apply_theme()

bat = load_batting()
bowl = load_bowling()
field = load_fielding()
players = get_player_list()

BIOS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'player_bios.json')
RESULTS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'match_results.json')
ROSTERS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'team_rosters.json')

@st.cache_data
def load_bios():
    if os.path.exists(BIOS_FILE):
        with open(BIOS_FILE) as f:
            return json.load(f)
    return {}

@st.cache_data
def load_results():
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE) as f:
            return json.load(f)
    return []

@st.cache_data
def load_rosters():
    if os.path.exists(ROSTERS_FILE):
        with open(ROSTERS_FILE) as f:
            return json.load(f)
    return {}

bios = load_bios()
results = load_results()
rosters = load_rosters()

# Calculate champions per season
champions = {}
for r in results:
    if r['match_type'] == 'Final':
        s = str(r['season'])
        w = r['winner']
        if w == 'Abandoned':
            champions[s] = [r['team1'], r['team2']]
        else:
            champions[s] = [w]

st.markdown("# 👤 Player Profile")
st.markdown("*Select a player to view detailed performance across seasons*")
st.divider()

if 'random_player_idx' not in st.session_state:
    st.session_state.random_player_idx = random.randint(0, len(players) - 1)

col1, col2 = st.columns([1, 2])
with col1:
    player = st.selectbox("Select Player", players, index=st.session_state.random_player_idx)
with col2:
    view = st.radio("View", ["Season Breakdown", "Aggregate", "Trends"], index=2, horizontal=True)

if not player:
    st.info("Please select a player")
    st.stop()

p_bat = bat[bat['player'] == player]
p_bowl = bowl[bowl['player'] == player]
p_field = field[field['player'] == player]

seasons_played = sorted(set(
    list(p_bat['season'].unique()) + list(p_bowl['season'].unique()) + list(p_field['season'].unique())
))

if not seasons_played:
    st.warning(f"No data found for {player}")
    st.stop()

teams = sorted(set(
    list(p_bat['team'].unique()) + list(p_bowl['team'].unique()) + list(p_field['team'].unique())
))

st.markdown(f"**Teams:** {', '.join(teams)} &nbsp;|&nbsp; **Seasons:** {', '.join(str(s) for s in seasons_played)}")
st.divider()

# Calculate championships for the player
player_titles = 0
for s, champs in champions.items():
    team_data = rosters.get(s, {})
    for c_team in champs:
        t_roster = team_data.get(c_team, {})
        if t_roster and player in t_roster.get('players', []):
            player_titles += 0.5 if len(champs) > 1 else 1

bio_data = bios.get(player, {})
role = bio_data.get("role", "Player")
description = bio_data.get("description", "An RPL player.")
photo_path = bio_data.get("photo_path", "")

# ── Top Bio Section ──
c1, c2 = st.columns([1, 4])
with c1:
    photo_abs_path = os.path.join(os.path.dirname(__file__), '..', photo_path) if photo_path else ""
    if photo_abs_path and os.path.exists(photo_abs_path):
        st.image(photo_abs_path, use_container_width=True)
    else:
        # Placeholder Avatar
        initials = "".join([n[0] for n in player.split()[:2]]).upper()
        st.markdown(f"""
        <div style="background:#1e293b;width:100%;aspect-ratio:1/1;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:3.5rem;font-weight:800;color:#94a3b8;border:3px solid #334155;box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
            {initials}
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown(f"<div style='text-align:center;margin-top:16px;font-weight:800;color:#f59e0b;letter-spacing:1px;text-transform:uppercase;font-size:0.9rem;'>{role}</div>", unsafe_allow_html=True)

with c2:
    st.markdown(f"<h2 style='margin-top:0;padding-top:0;'>{player}</h2>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:#cbd5e1;font-size:1.15rem;margin-bottom:24px;line-height:1.6;'>{description}</div>", unsafe_allow_html=True)
    
    # High-level summary metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Seasons", int(p_bat['season'].count()) if not p_bat.empty else 0)
    m2.metric("Total Runs", int(p_bat['runs'].sum()) if not p_bat.empty else 0)
    m3.metric("Total Wickets", int(p_bowl['wickets'].sum()) if not p_bowl.empty else 0)
    
    win_text = f"{int(player_titles)}" if player_titles.is_integer() else f"{player_titles}"
    m4.metric("🏆 Championships", win_text)

st.divider()

# ── Season Breakdown ──
if view == "Season Breakdown":
    season = st.selectbox("Season", seasons_played)
    sb = p_bat[p_bat['season'] == season]
    sw = p_bowl[p_bowl['season'] == season]
    sf = p_field[p_field['season'] == season]

    st.markdown("### 🏏 Batting")
    if not sb.empty:
        r = sb.iloc[0]
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("Runs", int(r['runs']) if r['runs'] else 0)
        c2.metric("Innings", int(r['innings']) if r['innings'] else 0)
        c3.metric("Average", f"{r['average']:.2f}" if r['average'] else "-")
        c4.metric("Strike Rate", f"{r['strike_rate']:.1f}" if r['strike_rate'] else "-")
        c5.metric("Highest", int(r['highest']) if r['highest'] else 0)
        c6.metric("4s / 6s", f"{int(r['fours'] or 0)} / {int(r['sixes'] or 0)}")
    else:
        st.caption("No batting data this season")

    st.markdown("### 🎳 Bowling")
    if not sw.empty:
        r = sw.iloc[0]
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("Wickets", int(r['wickets']) if r['wickets'] else 0)
        c2.metric("Overs", r['overs'] if r['overs'] else 0)
        c3.metric("Economy", f"{r['economy']:.2f}" if r['economy'] else "-")
        c4.metric("Average", f"{r['average']:.2f}" if r['average'] else "-")
        c5.metric("Best", int(r['best_figures']) if r['best_figures'] else 0)
        c6.metric("Maidens", int(r['maidens']) if r['maidens'] else 0)
    else:
        st.caption("No bowling data this season")

    st.markdown("### 🧤 Fielding")
    if not sf.empty:
        r = sf.iloc[0]
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Dismissals", int(r['dismissals']) if r['dismissals'] else 0)
        c2.metric("Catches", int(r['catches']) if r['catches'] else 0)
        c3.metric("Run Outs", int(r['run_outs']) if r['run_outs'] else 0)
        c4.metric("C&B", int(r['caught_bowled']) if r['caught_bowled'] else 0)
        c5.metric("Stumpings", int(r['stumpings']) if r['stumpings'] else 0)
    else:
        st.caption("No fielding data this season")

# ── Aggregate ──
elif view == "Aggregate":
    st.markdown("### 🏏 Batting (Totals & Averages)")
    if not p_bat.empty:
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total Runs", int(p_bat['runs'].sum()))
        c2.metric("Total Innings", int(p_bat['innings'].sum()))
        c3.metric("Avg (weighted)", f"{p_bat['runs'].sum() / max(p_bat['innings'].sum() - p_bat['not_outs'].sum(), 1):.2f}")
        c4.metric("Best Season Avg", f"{p_bat['average'].max():.2f}" if p_bat['average'].max() else "-")
        c5.metric("Seasons Batted", len(p_bat))
    else:
        st.caption("No batting data")

    st.markdown("### 🎳 Bowling (Totals & Averages)")
    if not p_bowl.empty:
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total Wickets", int(p_bowl['wickets'].sum()))
        c2.metric("Total Overs", f"{p_bowl['overs'].sum():.1f}")
        total_runs = p_bowl['runs'].sum()
        total_wkts = p_bowl['wickets'].sum()
        c3.metric("Avg (weighted)", f"{total_runs / max(total_wkts, 1):.2f}")
        c4.metric("Best Economy", f"{p_bowl['economy'].min():.2f}" if p_bowl['economy'].min() else "-")
        c5.metric("Seasons Bowled", len(p_bowl))
    else:
        st.caption("No bowling data")

    st.markdown("### 🧤 Fielding (Totals)")
    if not p_field.empty:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Dismissals", int(p_field['dismissals'].sum()))
        c2.metric("Total Catches", int(p_field['catches'].sum()))
        c3.metric("Total Run Outs", int(p_field['run_outs'].sum()))
        c4.metric("Total Stumpings", int(p_field['stumpings'].sum()))
    else:
        st.caption("No fielding data")

# ── Trends ──
else:
    col1, col2 = st.columns(2)
    with col1:
        if not p_bat.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=p_bat['season'], y=p_bat['runs'], mode='lines+markers',
                name='Runs', line=dict(color=COLORS[0], width=3), marker=dict(size=10)))
            fig.update_layout(title="Runs per Season", template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(dtick=1, title="Season"), yaxis=dict(title="Runs"))
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if not p_bat.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=p_bat['season'], y=p_bat['strike_rate'], mode='lines+markers',
                name='Strike Rate', line=dict(color=COLORS[2], width=3), marker=dict(size=10)))
            fig.update_layout(title="Strike Rate Trend", template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(dtick=1, title="Season"), yaxis=dict(title="SR"))
            st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        if not p_bowl.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=p_bowl['season'], y=p_bowl['wickets'], mode='lines+markers',
                name='Wickets', line=dict(color=COLORS[3], width=3), marker=dict(size=10)))
            fig.update_layout(title="Wickets per Season", template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(dtick=1, title="Season"), yaxis=dict(title="Wickets"))
            st.plotly_chart(fig, use_container_width=True)

    with col4:
        if not p_field.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=p_field['season'], y=p_field['dismissals'], mode='lines+markers',
                name='Dismissals', line=dict(color=COLORS[4], width=3), marker=dict(size=10)))
            fig.update_layout(title="Fielding Dismissals per Season", template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(dtick=1, title="Season"), yaxis=dict(title="Dismissals"))
            st.plotly_chart(fig, use_container_width=True)
