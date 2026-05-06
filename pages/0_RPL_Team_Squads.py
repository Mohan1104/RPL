import streamlit as st
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from RPL_data_utils import apply_theme

st.set_page_config(page_title="Team Squads | RPL", page_icon="🏟️", layout="wide")
apply_theme()

ROSTERS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'team_rosters.json')
RESULTS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'match_results.json')

@st.cache_data
def load_rosters():
    with open(ROSTERS_FILE) as f:
        return json.load(f)

@st.cache_data
def load_results():
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE) as f:
            return json.load(f)
    return []

rosters = load_rosters()
results = load_results()

# Determine champions per season
champions = {}
for r in results:
    if r['match_type'] == 'Final':
        s = str(r['season'])
        w = r['winner']
        if w == 'Abandoned':
            # Shared title
            champions[s] = [r['team1'], r['team2']]
        else:
            champions[s] = [w]

TEAMS = ['Gully Boyz', 'Ryland Challengers Birmingham', 'Ryland Super Kings', 'Ryland Royals']
TEAM_COLORS = {
    'Gully Boyz':                    '#10b981',
    'Ryland Challengers Birmingham': '#f43f5e',
    'Ryland Super Kings':            '#f59e0b',
    'Ryland Royals':                 '#8b5cf6',
}

def player_badge(p, captain, marquee, substitutes, accent):
    badges = ""
    if p == captain:
        badges += f'<span style="background:{accent};color:#fff;font-size:0.62rem;font-weight:700;padding:2px 7px;border-radius:20px;margin-left:6px;">C</span>'
    if p == marquee:
        badges += f'<span style="background:#f59e0b;color:#000;font-size:0.62rem;font-weight:700;padding:2px 7px;border-radius:20px;margin-left:4px;">M</span>'
    if p in substitutes:
        badges += f'<span style="background:#64748b;color:#fff;font-size:0.62rem;font-weight:700;padding:2px 7px;border-radius:20px;margin-left:4px;">SUB</span>'
    return f'<div style="padding:5px 0;border-bottom:1px solid {accent}22;display:flex;align-items:center;">{p}{badges}</div>'

def team_card(team_data, team, season_label=None, is_champion=False):
    accent = TEAM_COLORS.get(team, '#94a3b8')
    if team_data is None:
        label = season_label or team
        st.markdown(f"""
        <div style="border:1px solid {accent}33;border-radius:14px;padding:18px;margin-bottom:20px;opacity:0.4;">
            <div style="font-size:1rem;font-weight:700;color:{accent};">{label}</div>
            <div style="color:#94a3b8;font-size:0.85rem;margin-top:4px;">Not present this season</div>
        </div>""", unsafe_allow_html=True)
        return

    captain     = team_data.get('captain')     or '—'
    marquee     = team_data.get('marquee')     or '—'
    players     = team_data.get('players',     [])
    substitutes = team_data.get('substitutes', [])
    core_count  = len(players) - len(substitutes)
    squad_label = f"{core_count} players" + (f" + {len(substitutes)} sub" if substitutes else "")
    title       = season_label or team
    
    title_html = f"{title}"
    if is_champion:
        title_html += f' <span title="Season Champion" style="margin-left:8px;font-size:1.1rem;">🏆</span>'

    rows = "".join(player_badge(p, captain, marquee, substitutes, accent) for p in players)

    marquee_html = (
        f'<span style="color:#94a3b8;">—</span>'
        if marquee == '—'
        else f'{marquee} <span style="background:#f59e0b;color:#000;font-size:0.62rem;font-weight:700;padding:2px 7px;border-radius:20px;margin-left:4px;">M</span>'
    )

    st.markdown(f"""
    <div style="border:1px solid {accent}55;border-radius:14px;padding:20px;margin-bottom:24px;background:{accent}08;">
        <div style="font-size:1.1rem;font-weight:800;color:{accent};margin-bottom:12px;">{title_html}</div>
        <div style="display:flex;gap:24px;margin-bottom:14px;flex-wrap:wrap;">
            <div>
                <div style="font-size:0.62rem;text-transform:uppercase;letter-spacing:0.08em;color:#94a3b8;font-weight:600;">Captain</div>
                <div style="font-weight:700;font-size:0.9rem;margin-top:2px;">{captain}
                    <span style="background:{accent};color:#fff;font-size:0.62rem;font-weight:700;padding:2px 7px;border-radius:20px;margin-left:6px;">C</span>
                </div>
            </div>
            <div>
                <div style="font-size:0.62rem;text-transform:uppercase;letter-spacing:0.08em;color:#94a3b8;font-weight:600;">Marquee</div>
                <div style="font-weight:700;font-size:0.9rem;margin-top:2px;">{marquee_html}</div>
            </div>
            <div>
                <div style="font-size:0.62rem;text-transform:uppercase;letter-spacing:0.08em;color:#94a3b8;font-weight:600;">Squad</div>
                <div style="font-weight:700;font-size:0.9rem;margin-top:2px;">{squad_label}</div>
            </div>
        </div>
        <div style="font-size:0.85rem;color:#cbd5e1;">{rows}</div>
    </div>""", unsafe_allow_html=True)


# ── Page ──────────────────────────────────────────────────────────────────────
st.markdown("# 🏟️ Team Squads")
st.markdown("*Rosters, captains and marquee players*")
st.divider()

view = st.radio("View by", ["Season — all teams", "Team — all seasons"], horizontal=True)
st.divider()

# ── View 1: Season → all teams ───────────────────────────────────────────────
if view == "Season — all teams":
    season = st.selectbox("Select Season", [f"Season {s}" for s in range(1, 6)])
    season_num = str(int(season.split()[-1]))
    season_data = rosters[season_num]

    cols = st.columns(2)
    for i, team in enumerate(TEAMS):
        with cols[i % 2]:
            is_champ = team in champions.get(season_num, [])
            team_card(season_data.get(team), team, is_champion=is_champ)

# ── View 2: Team → all seasons ───────────────────────────────────────────────
else:
    team = st.selectbox("Select Team", TEAMS)
    accent = TEAM_COLORS[team]

    seasons_found = []
    for s in range(1, 6):
        s_data = rosters[str(s)].get(team)
        if s_data:
            seasons_found.append(s)

    if not seasons_found:
        st.info(f"{team} did not participate in any recorded season.")
    else:
        total_wins = sum(0.5 if len(champions.get(str(s), [])) > 1 else 1 for s in champions if team in champions[s])
        win_text = f"{int(total_wins)} Titles" if total_wins.is_integer() else f"{total_wins} Titles"
        
        st.markdown(f"**{team}** participated in **{len(seasons_found)}** season(s): "
                    + ", ".join(f"S{s}" for s in seasons_found)
                    + f" | 🏆 **{win_text}**")
        st.markdown("")

        cols = st.columns(2)
        for i, s in enumerate(range(1, 6)):
            s_data = rosters[str(s)].get(team)
            is_champ = team in champions.get(str(s), [])
            with cols[i % 2]:
                team_card(s_data, team, season_label=f"Season {s}", is_champion=is_champ)
