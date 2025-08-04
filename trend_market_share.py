import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Contoh data
data = {
    'Kategori': ['SARI ROTI', 'MY ROTI'],
    '2024': [86.82, 13.18],
    '2025': [91.09, 8.91],
    'Growth': [4.91, -32.35],
    'Gap': [4.26, -4.26]
}
df = pd.DataFrame(data)

# Buat chart
fig = go.Figure()

# Bar chart
fig.add_trace(go.Bar(x=df['Kategori'], y=df['2025'], name='2025', marker_color='gray'))
fig.add_trace(go.Bar(x=df['Kategori'], y=df['2024'], name='2024', marker_color='orange'))
fig.add_trace(go.Bar(x=df['Kategori'], y=df['Gap'], name='Gap', marker_color='green'))

# Line chart
fig.add_trace(go.Scatter(x=df['Kategori'], y=df['Growth'], name='Growth', mode='lines+markers', line=dict(color='blue')))

# Anotasi data (tabel di bawah kategori)
annotations = []
for i, row in df.iterrows():
    x = row['Kategori']
    annotations.append(dict(x=x, y=-5, text=f"2025: {row['2025']}%", showarrow=False, yanchor='top'))
    annotations.append(dict(x=x, y=-8, text=f"2024: {row['2024']}%", showarrow=False, yanchor='top'))
    annotations.append(dict(x=x, y=-11, text=f"Growth: {row['Growth']}%", showarrow=False, yanchor='top'))
    annotations.append(dict(x=x, y=-14, text=f"Gap: {row['Gap']}%", showarrow=False, yanchor='top'))

fig.update_layout(
    title="Market Share YTD Apr-25 (Sandwitch)",
    barmode='group',
    yaxis=dict(title='Market Share (%)'),
    yaxis2=dict(title='Growth (%)', overlaying='y', side='right'),
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
    annotations=annotations,
    height=500,
    margin=dict(b=150)  # tambahkan margin bawah agar tabel cukup
)

st.plotly_chart(fig, use_container_width=True)
