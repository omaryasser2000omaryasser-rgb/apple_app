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

price, selected_ages, years, categories, price_tiers = render_sidebar(df,'pay')


payment_methods = st.sidebar.multiselect(
    'Payment Methods',
    options=sorted(df['payment_method'].dropna().unique()),
    default=sorted(df['payment_method'].dropna().unique()),
    key='payment_methods'
)

filtered_df = apply_filters(df, price, selected_ages, years, categories,price_tiers)
filtered_df = filtered_df[filtered_df['payment_method'].isin(payment_methods)]

nav_bar('Payment')

# Header
c1, c2 = st.columns([1, 8])
c1.image("apple_logo.jfif", width=140)
c2.markdown("<h1 style='margin-bottom:0;'>Payment method by categories</h1>", unsafe_allow_html=True)
c2.markdown("<p style='color:#86868b;margin-top:4px;'>Apple Global Product Sales</p>", unsafe_allow_html=True)
st.markdown("---")

# KPIs
pay_totals = filtered_df.groupby('payment_method').size()
metrics = [(f"{v:,}", k) for k, v in pay_totals.items()]
kpi_row(metrics)

# Payment × Category faceted
st.markdown("### Payment method by categories")
pay_cat = filtered_df.groupby(['category', 'payment_method'])['unit_price_usd'].sum().reset_index()

fig_pay_cat = px.bar(
    pay_cat, x='payment_method', y='unit_price_usd',
    color='payment_method', facet_col='category',
    template='plotly_dark',
    color_discrete_sequence=['#5ac8fa', '#0a84ff', '#ff6b6b', '#ff3b30', '#34c759', '#30d158', '#ffd60a'],
    labels={'unit_price_usd': 'sum of unit_price_usd', 'payment_method': 'payment_method'}
)
fig_pay_cat.update_layout(**PLOTLY_DARK, height=460, showlegend=True)
fig_pay_cat.update_xaxes(tickangle=45)
fig_pay_cat.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
st.plotly_chart(fig_pay_cat, use_container_width=True)

# Payment totals
cols = st.columns(len(pay_totals))
for col, (pm, val) in zip(cols, pay_totals.items()):
    col.markdown(f"**{pm}:**  \n**{val:,}**")

st.markdown("<br>", unsafe_allow_html=True)

# Payment × Age group faceted
st.markdown("### Payment method by Age group")
pay_age = filtered_df.groupby(['customer_age_group', 'payment_method'])['unit_price_usd'].sum().reset_index()

fig_pay_age = px.bar(
    pay_age, x='payment_method', y='unit_price_usd',
    color='customer_age_group', facet_col='customer_age_group',
    template='plotly_dark',
    color_discrete_sequence=['#5ac8fa', '#0a84ff', '#ff9f0a', '#ff3b30', '#34c759'],
    labels={'unit_price_usd': 'sum of unit_price_usd'}
)
fig_pay_age.update_layout(**PLOTLY_DARK, height=440, showlegend=True)
fig_pay_age.update_xaxes(tickangle=45)
fig_pay_age.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
st.plotly_chart(fig_pay_age, use_container_width=True)

# Year totals
years_list = sorted(filtered_df['sale_year'].unique())
yr_cols = st.columns(len(years_list))
for col, yr in zip(yr_cols, years_list):
    yr_total = len(filtered_df[filtered_df['sale_year'] == yr])
    col.markdown(f"**Total {yr}:** **{yr_total:,}**")
st.markdown(f"**All Years: {len(filtered_df):,}**")