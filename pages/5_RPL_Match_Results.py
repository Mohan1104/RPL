import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from RPL_data_utils import apply_theme

st.set_page_config(page_title="Match Results | RPL", page_icon="📋", layout="wide")
apply_theme()

RESULTS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'match_results.json')

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
TEAMS = list(TEAM_COLORS.keys())

@st.cache_data
def load_results():
    with open(RESULTS_FILE) as f:
        return json.load(f)

results = load_results()

st.markdown("# 📋 Match Results & Standings")
st.markdown("*Season-by-season results, points tables and head-to-head records*")
st.divider()

tab1, tab2, tab3 = st.tabs(["📅 Match Results", "📊 Points Table", "🤝 Head-to-Head"])

# ── Tab 1: Match Results ─────────────────────────────────────────────────────
with tab1:
    season = st.selectbox("Season", [f"Season {s}" for s in range(1, 6)], key="res_season")
    snum = int(season.split()[-1])
    matches = [m for m in results if m['season'] == snum]

    for m in matches:
        t1, t2 = m['team1'], m['team2']
        c1 = TEAM_COLORS.get(t1, '#94a3b8')
        c2 = TEAM_COLORS.get(t2, '#94a3b8')
        w = m['winner']
        abandoned = w == 'Abandoned'

        type_badge_color = '#f59e0b' if m['match_type'] == 'Final' else '#3b82f6' if 'Qualifier' in m['match_type'] or 'Round' in m['match_type'] else '#64748b'

        t1_bold = "font-weight:800;" if w == t1 else "font-weight:400;opacity:0.7;"
        t2_bold = "font-weight:800;" if w == t2 else "font-weight:400;opacity:0.7;"
        if abandoned:
            t1_bold = t2_bold = "font-weight:400;opacity:0.6;"

        st.markdown(f"""
        <div style="border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:16px 20px;margin-bottom:12px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
            <div style="min-width:90px;">
                <span style="background:{type_badge_color};color:#fff;font-size:0.65rem;font-weight:700;padding:3px 10px;border-radius:20px;">{m['match_type']}</span>
            </div>
            <div style="flex:1;display:flex;align-items:center;justify-content:center;gap:12px;flex-wrap:wrap;">
                <div style="text-align:right;min-width:180px;">
                    <span style="color:{c1};{t1_bold}">{t1}</span>
                    <span style="margin-left:8px;font-weight:600;font-size:0.95rem;">{m['team1_score']}</span>
                    <span style="color:#94a3b8;font-size:0.8rem;"> ({m['team1_overs']})</span>
                </div>
                <span style="color:#64748b;font-weight:700;">vs</span>
                <div style="text-align:left;min-width:180px;">
                    <span style="color:{c2};{t2_bold}">{t2}</span>
                    <span style="margin-left:8px;font-weight:600;font-size:0.95rem;">{m['team2_score']}</span>
                    <span style="color:#94a3b8;font-size:0.8rem;"> ({m['team2_overs']})</span>
                </div>
            </div>
            <div style="min-width:200px;text-align:right;font-size:0.8rem;color:{'#94a3b8' if abandoned else '#10b981'};font-weight:600;">
                {m['result']}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── Tab 2: Points Table ──────────────────────────────────────────────────────
with tab2:
    season2 = st.selectbox("Season", [f"Season {s}" for s in range(1, 6)], key="pts_season")
    snum2 = int(season2.split()[-1])
    matches2 = [m for m in results if m['season'] == snum2]

    # Only count league matches for points
    league_matches = [m for m in matches2 if m['match_type'] == 'League']

    standings = {}
    for team in TEAMS:
        standings[team] = {'P': 0, 'W': 0, 'L': 0, 'A': 0, 'Pts': 0}

    for m in league_matches:
        t1, t2, w = m['team1'], m['team2'], m['winner']
        if t1 in standings:
            standings[t1]['P'] += 1
        if t2 in standings:
            standings[t2]['P'] += 1
        if w == 'Abandoned':
            if t1 in standings: standings[t1]['A'] += 1
            if t2 in standings: standings[t2]['A'] += 1
        elif w in standings:
            standings[w]['W'] += 1
            standings[w]['Pts'] += 2
            loser = t2 if w == t1 else t1
            if loser in standings:
                standings[loser]['L'] += 1

    rows = []
    for team, s in standings.items():
        if s['P'] > 0:
            rows.append({
                'Team': team, 'P': s['P'], 'W': s['W'], 'L': s['L'],
                'A': s['A'], 'Pts': s['Pts']
            })
    df = pd.DataFrame(rows).sort_values('Pts', ascending=False).reset_index(drop=True)
    df.index = df.index + 1

    st.dataframe(df, use_container_width=True, hide_index=False)

    # Champion badge
    finals = [m for m in matches2 if m['match_type'] == 'Final']
    if finals:
        f = finals[0]
        if f['winner'] != 'Abandoned':
            color = TEAM_COLORS.get(f['winner'], '#10b981')
            st.markdown(f"""
            <div style="text-align:center;margin-top:16px;padding:16px;border:2px solid {color};border-radius:14px;background:{color}11;">
                <div style="font-size:2rem;">🏆</div>
                <div style="font-size:1.2rem;font-weight:800;color:{color};">{f['winner']}</div>
                <div style="font-size:0.85rem;color:#94a3b8;">Season {snum2} Champions</div>
                <div style="font-size:0.8rem;color:#cbd5e1;margin-top:4px;">{f['result']}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info(f"Season {snum2} Final: {f['result']}")

    # Win distribution chart
    if rows:
        teams_with_data = [r['Team'] for r in rows if r['P'] > 0]
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[SHORT[t] for t in teams_with_data],
            y=[next(r['W'] for r in rows if r['Team'] == t) for t in teams_with_data],
            name='Wins', marker_color=[TEAM_COLORS[t] for t in teams_with_data],
            text=[next(r['W'] for r in rows if r['Team'] == t) for t in teams_with_data],
            textposition='outside'
        ))
        fig.update_layout(title="League Wins", template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(title="Wins"), height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# ── Tab 3: Head-to-Head ──────────────────────────────────────────────────────
with tab3:
    col1, col2 = st.columns(2)
    with col1:
        h2h_t1 = st.selectbox("Team A", TEAMS, index=0, key="h2h1")
    with col2:
        other = [t for t in TEAMS if t != h2h_t1]
        h2h_t2 = st.selectbox("Team B", other, index=0, key="h2h2")

    h2h_matches = [m for m in results
        if (m['team1'] in [h2h_t1, h2h_t2] and m['team2'] in [h2h_t1, h2h_t2])]

    if not h2h_matches:
        st.info("No head-to-head matches found")
    else:
        t1_wins = sum(1 for m in h2h_matches if m['winner'] == h2h_t1)
        t2_wins = sum(1 for m in h2h_matches if m['winner'] == h2h_t2)
        draws = sum(1 for m in h2h_matches if m['winner'] == 'Abandoned')

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Matches", len(h2h_matches))
        c2.metric(f"{SHORT[h2h_t1]} Wins", t1_wins)
        c3.metric(f"{SHORT[h2h_t2]} Wins", t2_wins)
        c4.metric("No Result", draws)

        # Pie chart
        fig = go.Figure(data=[go.Pie(
            labels=[SHORT[h2h_t1], SHORT[h2h_t2], 'No Result'],
            values=[t1_wins, t2_wins, draws],
            marker=dict(colors=[TEAM_COLORS[h2h_t1], TEAM_COLORS[h2h_t2], '#64748b']),
            hole=0.45, textinfo='label+value'
        )])
        fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
            height=300, showlegend=False, title="Win Distribution")
        st.plotly_chart(fig, use_container_width=True)

        # Match list
        st.markdown("### Match History")
        for m in h2h_matches:
            badge_color = '#f59e0b' if m['match_type'] == 'Final' else '#3b82f6' if 'Qualifier' in m['match_type'] or 'Round' in m['match_type'] else '#64748b'
            winner_color = TEAM_COLORS.get(m['winner'], '#94a3b8') if m['winner'] != 'Abandoned' else '#94a3b8'
            st.markdown(f"""
            <div style="border:1px solid rgba(255,255,255,0.06);border-radius:10px;padding:12px 16px;margin-bottom:8px;">
                <span style="background:{badge_color};color:#fff;font-size:0.6rem;font-weight:700;padding:2px 8px;border-radius:16px;">S{m['season']} {m['match_type']}</span>
                &nbsp;
                <span style="font-weight:600;">{SHORT[m['team1']]} {m['team1_score']}</span>
                <span style="color:#64748b;"> vs </span>
                <span style="font-weight:600;">{SHORT[m['team2']]} {m['team2_score']}</span>
                &nbsp;—&nbsp;
                <span style="color:{winner_color};font-size:0.85rem;font-weight:600;">{m['result']}</span>
            </div>
            """, unsafe_allow_html=True)
