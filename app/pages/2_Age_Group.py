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

price, selected_ages, years, categories = render_sidebar(df, 'age')
filtered_df = apply_filters(df, price, selected_ages, years, categories)

nav_bar('Age_Group')

# Header
c1, c2 = st.columns([1, 8])
c1.image("apple_logo.webp", width=70)
c2.markdown("<h1 style='margin-bottom:0;'>Customer age group</h1>", unsafe_allow_html=True)
c2.markdown("<p style='color:#86868b;margin-top:4px;'>Apple Global Product Sales</p>", unsafe_allow_html=True)
st.markdown("---")

# KPIs per age group
age_totals = filtered_df.groupby('customer_age_group')['unit_price_usd'].sum()
metrics = [(f"${v:,.0f}", k) for k, v in age_totals.items()]
kpi_row(metrics)

# Category × Age group faceted
st.markdown("### Customer age group by Category")
age_cat = filtered_df.groupby(['category', 'customer_age_group'])['unit_price_usd'].sum().reset_index()

fig_age_cat = px.bar(
    age_cat, x='customer_age_group', y='unit_price_usd',
    color='customer_age_group', facet_col='category',
    template='plotly_dark',
    color_discrete_sequence=['#5ac8fa', '#0a84ff', '#ff9f0a', '#ff3b30', '#34c759'],
    labels={'unit_price_usd': 'sum of unit_price_usd', 'customer_age_group': 'customer_age_group'}
)
fig_age_cat.update_layout(**PLOTLY_DARK, height=460, showlegend=True)
fig_age_cat.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
st.plotly_chart(fig_age_cat, use_container_width=True)

# Age group totals row
cols = st.columns(len(age_totals))
for col, (ag, val) in zip(cols, age_totals.items()):
    col.markdown(f"**{ag}:**  \n**{val:,.0f}**")

st.markdown("<br>", unsafe_allow_html=True)

# Payment method × Age group faceted
st.markdown("### Payment method by Age group")
pay_age = filtered_df.groupby(['payment_method', 'customer_age_group']).size().reset_index(name='count')

fig_pay_age = px.bar(
    pay_age, x='customer_age_group', y='count',
    color='payment_method', facet_col='payment_method',
    template='plotly_dark',
    color_discrete_sequence=['#5ac8fa', '#0a84ff', '#ff6b6b', '#ff3b30', '#34c759', '#30d158', '#ffd60a'],
    labels={'count': 'count', 'customer_age_group': 'customer_age_group'}
)
fig_pay_age.update_layout(**PLOTLY_DARK, height=440, showlegend=True)
fig_pay_age.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
st.plotly_chart(fig_pay_age, use_container_width=True)

# Year totals
years_list = sorted(filtered_df['sale_year'].unique())
yr_cols = st.columns(len(years_list))
for col, yr in zip(yr_cols, years_list):
    yr_total = len(filtered_df[filtered_df['sale_year'] == yr])
    col.markdown(f"**Total {yr}:** **{yr_total:,}**")
st.markdown(f"**All Years: {len(filtered_df):,}**")