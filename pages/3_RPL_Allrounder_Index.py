import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared_utils import apply_theme, load_batting, load_bowling, load_fielding, get_player_list, COLORS

st.set_page_config(page_title="All-Rounder Index | RPL", page_icon="🕸️", layout="wide")
apply_theme()

bat = load_batting()
bowl = load_bowling()
field = load_fielding()
players = get_player_list()

st.markdown("# :material/radar: All-Rounder Index")
st.markdown("Compare all-round performance using radar charts — normalized across all players")

with st.container(border=True):
    selected = st.multiselect("Select Players to Compare (up to 8)", players, placeholder="Choose players...")

if len(selected) < 1:
    st.info("Select at least 1 player to view their all-rounder profile", icon=":material/info:")
    st.stop()

st.divider()

# ── Compute aggregate stats for normalization ──
bat_agg = bat.groupby('player').agg(
    total_runs=('runs', 'sum'),
    avg_sr=('strike_rate', 'mean')
).reset_index()

bowl_agg = bowl.groupby('player').agg(
    total_wickets=('wickets', 'sum'),
    avg_econ=('economy', 'mean')
).reset_index()

field_agg = field.groupby('player').agg(
    total_dismissals=('dismissals', 'sum'),
    total_catches=('catches', 'sum')
).reset_index()

# Merge
all_stats = bat_agg.merge(bowl_agg, on='player', how='outer').merge(field_agg, on='player', how='outer').fillna(0)

# Normalize each metric to 0-100 percentile
def percentile_rank(series):
    if series.max() == 0:
        return series
    return (series.rank(pct=True) * 100).round(1)

# For economy, lower is better - invert
all_stats['runs_pct'] = percentile_rank(all_stats['total_runs'])
all_stats['wickets_pct'] = percentile_rank(all_stats['total_wickets'])
all_stats['sr_pct'] = percentile_rank(all_stats['avg_sr'])
all_stats['econ_pct'] = percentile_rank(all_stats['avg_econ'].max() - all_stats['avg_econ'])  # Invert
all_stats['fielding_pct'] = percentile_rank(all_stats['total_dismissals'])

categories = ['Runs', 'Wickets', 'Strike Rate', 'Economy', 'Fielding']

fig = go.Figure()

for i, p in enumerate(selected):
    row = all_stats[all_stats['player'] == p]
    if row.empty:
        continue
    r = row.iloc[0]
    values = [r['runs_pct'], r['wickets_pct'], r['sr_pct'], r['econ_pct'], r['fielding_pct']]
    values.append(values[0])  # Close the polygon
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories + [categories[0]],
        fill='toself',
        name=p,
        line=dict(color=COLORS[i % len(COLORS)], width=2),
        fillcolor=COLORS[i % len(COLORS)].replace(')', ',0.15)').replace('rgb', 'rgba') if 'rgb' in COLORS[i % len(COLORS)] else None,
        opacity=0.85
    ))

fig.update_layout(
    polar=dict(
        bgcolor='rgba(0,0,0,0)',
        radialaxis=dict(visible=True, range=[0, 100], showticklabels=True,
                       gridcolor='rgba(255,255,255,0.1)', linecolor='rgba(255,255,255,0.1)'),
        angularaxis=dict(gridcolor='rgba(255,255,255,0.1)', linecolor='rgba(255,255,255,0.1)')
    ),
    template='plotly_dark',
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    height=500,
    legend=dict(orientation='h', y=-0.1),
    title="All-Rounder Radar (Percentile Rankings)"
)
st.plotly_chart(fig, use_container_width=True)

# ── Summary Table ──
st.markdown("### Raw Stats Summary")
table_rows = []
for p in selected:
    row = all_stats[all_stats['player'] == p]
    if row.empty:
        continue
    r = row.iloc[0]
    # Compute a simple all-rounder score (average of percentiles)
    ar_score = np.mean([r['runs_pct'], r['wickets_pct'], r['sr_pct'], r['econ_pct'], r['fielding_pct']])
    table_rows.append({
        'Player': p,
        'Total Runs': int(r['total_runs']),
        'Total Wickets': int(r['total_wickets']),
        'Avg SR': f"{r['avg_sr']:.1f}",
        'Avg Econ': f"{r['avg_econ']:.2f}" if r['avg_econ'] > 0 else "-",
        'Dismissals': int(r['total_dismissals']),
        'AR Score': f"{ar_score:.1f}"
    })

if table_rows:
    df = pd.DataFrame(table_rows).sort_values('AR Score', ascending=False)
    st.dataframe(df, use_container_width=True, hide_index=True)
