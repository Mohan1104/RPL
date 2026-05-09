import streamlit as st
import json, os, sys, html
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared_utils import apply_theme, load_rosters, load_results, load_auctions, TEAM_COLORS

st.set_page_config(page_title="Team Squads | RPL", page_icon="🏟️", layout="wide")
apply_theme()

# Removed redundant loaders

rosters = load_rosters()
results = load_results()
auctions = load_auctions()

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

TEAMS = list(TEAM_COLORS.keys())

def player_badge(p, captain, marquee, substitutes, accent, auction_price=None):
    badges = ""
    if p == captain:
        badges += f'<span style="background:{accent};color:#fff;font-size:0.62rem;font-weight:700;padding:2px 7px;border-radius:20px;margin-left:6px;">C</span>'
    if p == marquee:
        badges += f'<span style="background:#f59e0b;color:#000;font-size:0.62rem;font-weight:700;padding:2px 7px;border-radius:20px;margin-left:4px;">M</span>'
    if p in substitutes:
        badges += f'<span style="background:#64748b;color:#fff;font-size:0.62rem;font-weight:700;padding:2px 7px;border-radius:20px;margin-left:4px;">SUB</span>'
    
    price_html = f'<span style="color:#94a3b8;font-size:0.8rem;margin-left:auto;">{auction_price} pts</span>' if auction_price else ""
    return f'<div style="padding:5px 0;border-bottom:1px solid {accent}22;display:flex;align-items:center;">{html.escape(p)}{badges}{price_html}</div>'

def team_card(team_data, team, season_num=None, season_label=None, is_champion=False):
    accent = TEAM_COLORS.get(team, '#94a3b8')
    if team_data is None:
        label = season_label or team
        st.markdown(f"""
        <div class="glass-card" style="opacity: 0.4; border-color: {accent}33;">
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
    
    with st.container():
        st.markdown(f"""<div class="glass-card" style="border-left: 5px solid {accent};">""", unsafe_allow_html=True)
        
        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown(f"### {title} {'🏆' if is_champion else ''}")
        with c2:
            st.markdown(f"<div style='text-align:right; color:{accent}; font-weight:700;'>{team}</div>", unsafe_allow_html=True)

        m1, m2, m3 = st.columns(3)
        with m1:
            st.caption("CAPTAIN")
            st.markdown(f"**{captain}**")
            if captain != '—': st.markdown(f'<span style="background:{accent};color:#fff;font-size:0.62rem;font-weight:700;padding:2px 7px;border-radius:20px;">C</span>', unsafe_allow_html=True)
        with m2:
            st.caption("MARQUEE")
            st.markdown(f"**{marquee}**")
            if marquee != '—': st.markdown('<span style="background:#f59e0b;color:#000;font-size:0.62rem;font-weight:700;padding:2px 7px;border-radius:20px;">M</span>', unsafe_allow_html=True)
        with m3:
            st.caption("SQUAD")
            st.markdown(f"**{squad_label}**")

        st.markdown("<hr style='margin: 15px 0; border: none; border-top: 1px solid rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
        
        season_auctions = auctions.get(str(season_num), {}) if season_num else {}
        
        # Display players in a more compact grid/list
        for p in players:
            price = season_auctions.get(p)
            html_badge = player_badge(p, captain, marquee, substitutes, accent, auction_price=price)
            st.markdown(html_badge, unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)


# ── Page ──────────────────────────────────────────────────────────────────────
st.markdown("# :material/groups: Team Squads")
st.markdown("Rosters, captains and marquee players across all RPL seasons")

view = st.radio("View by", ["Season — all teams", "Team — all seasons"], horizontal=True)

# ── View 1: Season → all teams ───────────────────────────────────────────────
if view == "Season — all teams":
    season = st.selectbox("Select Season", [f"Season {s}" for s in range(1, 6)], key="global_season")
    season_num = str(int(season.split()[-1]))
    season_data = rosters[season_num]

    cols = st.columns(2)
    for i, team in enumerate(TEAMS):
        with cols[i % 2]:
            is_champ = team in champions.get(season_num, [])
            team_card(season_data.get(team), team, season_num=season_num, is_champion=is_champ)

# ── View 2: Team → all seasons ───────────────────────────────────────────────
else:
    team = st.selectbox("Select Team", TEAMS, key="global_team")
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
                    + f" | :material/workspace_premium: **{win_text}**")
        st.markdown("")

        cols = st.columns(2)
        for i, s in enumerate(range(1, 6)):
            s_data = rosters[str(s)].get(team)
            is_champ = team in champions.get(str(s), [])
            with cols[i % 2]:
                team_card(s_data, team, season_num=str(s), season_label=f"Season {s}", is_champion=is_champ)
