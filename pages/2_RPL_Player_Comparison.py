import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from RPL_data_utils import apply_theme, load_batting, load_bowling, load_fielding, get_player_list, COLORS

st.set_page_config(page_title="Player Comparison | RPL", page_icon="📊", layout="wide")
apply_theme()

bat = load_batting()
bowl = load_bowling()
field = load_fielding()
players = get_player_list()

st.markdown("# 📊 Player Comparison")
st.markdown("*Compare multiple players across key performance metrics*")
st.divider()

col1, col2 = st.columns([2, 1])
with col1:
    selected = st.multiselect("Select Players (up to 5)", players, max_selections=5)
with col2:
    metric = st.selectbox("Metric", ["Runs Scored", "Wickets Taken", "Fielding Dismissals"])

if len(selected) < 2:
    st.info("Select at least 2 players to compare")
    st.stop()

st.divider()

# ── Build comparison data ──
fig = go.Figure()

if metric == "Runs Scored":
    for i, p in enumerate(selected):
        p_data = bat[bat['player'] == p].sort_values('season')
        fig.add_trace(go.Bar(
            x=[f"S{s}" for s in p_data['season']],
            y=p_data['runs'], name=p,
            marker_color=COLORS[i % len(COLORS)],
            text=p_data['runs'], textposition='outside'
        ))
    fig.update_layout(title="Runs Scored per Season", yaxis_title="Runs")
    # Summary table
    rows = []
    for p in selected:
        d = bat[bat['player'] == p]
        rows.append({
            'Player': p, 'Total Runs': int(d['runs'].sum()),
            'Innings': int(d['innings'].sum()),
            'Best Avg': f"{d['average'].max():.2f}" if not d.empty and d['average'].max() else "-",
            'Best SR': f"{d['strike_rate'].max():.1f}" if not d.empty and d['strike_rate'].max() else "-",
            'Seasons': len(d)
        })

elif metric == "Wickets Taken":
    for i, p in enumerate(selected):
        p_data = bowl[bowl['player'] == p].sort_values('season')
        fig.add_trace(go.Bar(
            x=[f"S{s}" for s in p_data['season']],
            y=p_data['wickets'], name=p,
            marker_color=COLORS[i % len(COLORS)],
            text=p_data['wickets'], textposition='outside'
        ))
    fig.update_layout(title="Wickets Taken per Season", yaxis_title="Wickets")
    rows = []
    for p in selected:
        d = bowl[bowl['player'] == p]
        rows.append({
            'Player': p, 'Total Wickets': int(d['wickets'].sum()),
            'Overs': f"{d['overs'].sum():.1f}",
            'Best Econ': f"{d['economy'].min():.2f}" if not d.empty and d['economy'].min() else "-",
            'Best Figures': int(d['best_figures'].max()) if not d.empty and d['best_figures'].max() else "-",
            'Seasons': len(d)
        })

else:  # Fielding
    for i, p in enumerate(selected):
        p_data = field[field['player'] == p].sort_values('season')
        dismissals = p_data['dismissals'].fillna(0)
        fig.add_trace(go.Bar(
            x=[f"S{s}" for s in p_data['season']],
            y=dismissals, name=p,
            marker_color=COLORS[i % len(COLORS)],
            text=dismissals.astype(int), textposition='outside'
        ))
    fig.update_layout(title="Fielding Dismissals per Season", yaxis_title="Dismissals (Catches + Run Outs)")
    rows = []
    for p in selected:
        d = field[field['player'] == p]
        rows.append({
            'Player': p,
            'Total Dismissals': int(d['dismissals'].sum()) if not d.empty else 0,
            'Catches': int(d['catches'].sum()) if not d.empty else 0,
            'Run Outs': int(d['run_outs'].sum()) if not d.empty else 0,
            'Stumpings': int(d['stumpings'].sum()) if not d.empty else 0,
            'Seasons': len(d)
        })

fig.update_layout(
    barmode='group', template='plotly_dark',
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(title="Season"), legend=dict(orientation='h', y=-0.15),
    height=450
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("### Summary")
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
