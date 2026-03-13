import pandas as pd
import plotly.express as px
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils import DARK_CSS, render_sidebar, apply_filters, nav_bar, kpi_row, PLOTLY_DARK

st.set_page_config(
    page_title='Apple Sales Dashboard',
    page_icon='https://www.apple.com/favicon.ico',
    layout='wide'
)

st.markdown(DARK_CSS, unsafe_allow_html=True)

df = pd.read_csv('data/cleaned data/cleaned_data.csv')

price, selected_ages, years, categories, price_tiers = render_sidebar(df, 'cont')
filtered_df = apply_filters(df, price, selected_ages, years, categories, price_tiers)

nav_bar('Continents')

# Header
c1, c2 = st.columns([1, 8])
c1.image("apple_logo.jfif", width=140)
c2.markdown("<h1 style='margin-bottom:0;'>Continent sold by amount</h1>", unsafe_allow_html=True)
c2.markdown("<p style='color:#86868b;margin-top:4px;'>Apple Global Product Sales</p>", unsafe_allow_html=True)
st.markdown("---")

# KPIs
region_totals = filtered_df.groupby('region')['unit_price_usd'].sum()
metrics = [(f"${v:,.0f}", k) for k, v in region_totals.nlargest(5).items()]
kpi_row(metrics)

# Continent bar
st.markdown("### Continent sold by amount")
region_df = filtered_df.groupby('region')['unit_price_usd'].sum().reset_index()

fig_region = px.bar(
    region_df, x='region', y='unit_price_usd', color='region',
    template='plotly_dark',
    labels={'unit_price_usd': 'sum of unit_price_usd', 'region': 'region'}
)
fig_region.update_layout(**PLOTLY_DARK, height=420, showlegend=True)
st.plotly_chart(fig_region, use_container_width=True)

# Region totals
cols_r = st.columns(4)
for i, (reg, val) in enumerate(region_totals.items()):
    cols_r[i % 4].markdown(f"**{reg}:**  \n**{val:,.0f}**")

st.markdown("<br>", unsafe_allow_html=True)

# Country bar
st.markdown("### Solid Product by Countries")
country_df = filtered_df.groupby('country')['unit_price_usd'].sum().reset_index()

fig_country = px.bar(
    country_df, x='country', y='unit_price_usd', color='country',
    template='plotly_dark',
    labels={'unit_price_usd': 'sum of unit_price_usd'}
)
fig_country.update_layout(**PLOTLY_DARK, height=420, showlegend=True)
fig_country.update_xaxes(tickangle=45)
st.plotly_chart(fig_country, use_container_width=True)

# Customer segment faceted
st.markdown("### Sales by Country & Customer Segment")
seg_country = filtered_df.groupby(['country', 'customer_segment'])['unit_price_usd'].sum().reset_index()

fig_seg = px.bar(
    seg_country, x='country', y='unit_price_usd',
    color='customer_segment', facet_col='customer_segment',
    template='plotly_dark',
    color_discrete_sequence=['#0a84ff', '#5ac8fa', '#ff6b6b', '#ff3b30']
)
fig_seg.update_layout(**PLOTLY_DARK, height=440, showlegend=True)
fig_seg.update_xaxes(tickangle=45)
fig_seg.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
st.plotly_chart(fig_seg, use_container_width=True)

# Year totals
yr_cols = st.columns(4)
for i, yr in enumerate(sorted(filtered_df['sale_year'].unique())):
    yr_total = len(filtered_df[filtered_df['sale_year'] == yr])
    yr_cols[i % 4].markdown(f"**Total {yr}:** **{yr_total:,}**")
st.markdown(f"**All Years: {len(filtered_df):,}**")