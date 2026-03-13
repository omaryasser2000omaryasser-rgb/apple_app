import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title='Apple Sales Dashboard',
    page_icon='https://www.apple.com/favicon.ico',
    layout='wide'
)

# ── Shared CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }

[data-testid="stSidebar"] {
    background: #1c1c1e !important;
    border-right: 1px solid #2c2c2e;
}
[data-testid="stSidebar"] * { color: #f5f5f7 !important; }
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {
    background-color: #34c759 !important;
    color: #000 !important;
    border-radius: 20px;
    font-weight: 600;
}
[data-testid="stSidebar"] label { color: #86868b !important; font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; }

[data-testid="stAppViewContainer"] { background: #000 !important; }
[data-testid="stHeader"] { background: transparent; }
h1, h2, h3, h4 { color: #f5f5f7 !important; }
p, li, span { color: #a1a1a6 !important; }

.nav-pill {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 10px 24px; border-radius: 30px;
    font-size: 14px; font-weight: 600; cursor: pointer;
    transition: all 0.2s;
}
.nav-active  { background: #34c759; color: #000 !important; }
.nav-inactive { background: #2c2c2e; color: #f5f5f7 !important; }

.kpi-card {
    background: #1c1c1e;
    border-radius: 18px;
    padding: 24px 20px;
    border: 1px solid #2c2c2e;
    text-align: center;
}
.kpi-value { font-size: 28px; font-weight: 700; color: #34c759 !important; }
.kpi-label { font-size: 12px; color: #86868b !important; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 4px; }

.js-plotly-plot { background: transparent !important; }
</style>
""", unsafe_allow_html=True)


# ── Load data ────────────────────────────────────────────────────────────────
df = pd.read_csv('data/cleaned data/cleaned_data.csv')


# ── Sidebar ──────────────────────────────────────────────────────────────────
def render_sidebar(df):
    st.sidebar.markdown("##  Apple Sales")
    st.sidebar.markdown("---")

    price_min = float(df['unit_price_usd'].min())
    price_max = float(df['unit_price_usd'].max())
    price = st.sidebar.slider('Price', min_value=price_min, max_value=price_max,
                               value=(price_min, price_max), format='$%.2f')

    st.sidebar.markdown("**Select Age Groups:**")
    age_groups = df['customer_age_group'].dropna().unique().tolist()
    selected_ages = []
    for ag in sorted(age_groups):
        if st.sidebar.checkbox(ag, value=True, key=f'age_{ag}'):
            selected_ages.append(ag)

    years = st.sidebar.multiselect('Year', options=sorted(df['sale_year'].unique()),
                                    default=sorted(df['sale_year'].unique()))

    categories = st.sidebar.multiselect('Products',
                                         options=sorted(df['category'].unique()),
                                         default=sorted(df['category'].unique()))

    price_tiers = st.sidebar.multiselect('Price Tier',        # ← add this
                                          options=sorted(df['price_tier'].dropna().unique()),
                                          default=sorted(df['price_tier'].dropna().unique()))

    return price, selected_ages, years, categories, price_tiers

price, selected_ages, years, categories, price_tiers = render_sidebar(df)

filtered_df = df[
    (df['unit_price_usd'] >= price[0]) &
    (df['unit_price_usd'] <= price[1]) &
    (df['customer_age_group'].isin(selected_ages)) &
    (df['sale_year'].isin(years)) &
    (df['category'].isin(categories)) &
    (df['price_tier'].isin(price_tiers))
    ]

# ── Top Nav ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style='display:flex; gap:12px; padding: 16px 0 24px 0;'>
  <span class='nav-pill nav-active'>🏠 Category</span>
  <a href='/Continents' target='_self' style='text-decoration:none;'><span class='nav-pill nav-inactive'>🌐 Continents</span></a>
  <a href='/Age_Group' target='_self' style='text-decoration:none;'><span class='nav-pill nav-inactive'>👥 Age Group</span></a>
  <a href='/Payment' target='_self' style='text-decoration:none;'><span class='nav-pill nav-inactive'>💳 Payment</span></a>
</div>
""", unsafe_allow_html=True)


# ── Header ───────────────────────────────────────────────────────────────────
col_logo, col_title = st.columns([1, 8])
with col_logo:
    st.image("apple_logo.jfif", width=140)
with col_title:
    st.markdown("<h1 style='margin-bottom:0;'>Best-selling category products</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#86868b; margin-top:4px;'>Apple Global Product Sales</p>", unsafe_allow_html=True)

st.markdown("---")


# ── KPI Summary Cards ────────────────────────────────────────────────────────
cat_cols      = [c for c in filtered_df.columns if filtered_df[c].dtype == 'object' and filtered_df[c].nunique() < 30]
total_records = len(filtered_df)
total_products = filtered_df['product_name'].nunique() if 'product_name' in filtered_df.columns \
                 else (filtered_df[cat_cols[0]].nunique() if cat_cols else 'N/A')

geo_col        = next((c for c in filtered_df.columns if 'country' in c or 'region' in c), None)
total_countries = filtered_df[geo_col].nunique() if geo_col else 'N/A'

rev_col  = next((c for c in filtered_df.columns if 'revenue' in c.lower() or 'sales' in c.lower()), None)
rev_sum  = filtered_df[rev_col].sum() if rev_col else None
if rev_sum is not None:
    total_rev = f'${rev_sum/1e9:.2f}B' if rev_sum >= 1e9 else f'${rev_sum/1e6:.1f}M' if rev_sum >= 1e6 else f'${rev_sum:,.0f}'
else:
    total_rev = f'${filtered_df["unit_price_usd"].sum()/1e6:.1f}M'

units_col = next((c for c in filtered_df.columns if 'unit' in c.lower() and 'price' not in c.lower()
                   or 'quantity' in c.lower() or 'sold' in c.lower()), None)
if units_col:
    u = filtered_df[units_col].sum()
    total_units = f'{u/1e6:.2f}M' if u >= 1e6 else f'{u:,.0f}'
else:
    total_units = f'{total_records:,}'

avg_price  = filtered_df['unit_price_usd'].mean() if 'unit_price_usd' in filtered_df.columns else None
avg_rating = filtered_df['customer_rating'].mean() if 'customer_rating' in filtered_df.columns else None

metrics = [
    ('🖥️', str(total_products),                          'Products'),
    ('🌍', str(total_countries),                         'Countries'),
    ('💰', total_rev,                                    'Total Revenue'),
    ('📱', total_units,                                  'Units Sold'),
    ('💵', f'${avg_price:,.2f}' if avg_price else 'N/A', 'Avg. Price'),
    ('⭐', f'{avg_rating:.1f}'  if avg_rating else 'N/A', 'Avg. Rating'),
]

kpi_cols = st.columns(len(metrics))
for col, (icon, val, label) in zip(kpi_cols, metrics):
    col.markdown(f"""
    <div class='kpi-card'>
        <div style='font-size:22px;'>{icon}</div>
        <div class='kpi-value'>{val}</div>
        <div class='kpi-label'>{label}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ── Category Bar Chart ────────────────────────────────────────────────────────
cat_summary = filtered_df.groupby('category')['units_sold'].sum().reset_index() \
    if 'units_sold' in filtered_df.columns else \
    filtered_df.groupby('category').size().reset_index(name='units_sold')

best_cats = ', '.join(cat_summary.nlargest(6, 'units_sold')['category'].tolist())
st.markdown(f"**Best-selling category products:**  \n{best_cats}")

color_map = {
    'AirPods': '#5ac8fa', 'Accessories': '#0a84ff', 'Apple Watch': '#ff6b6b',
    'Mac': '#ff3b30', 'iPhone': '#34c759', 'iPad': '#30d158'
}

fig_cat = px.bar(
    cat_summary, x='category', y='units_sold', color='category',
    color_discrete_map=color_map,
    template='plotly_dark',
    labels={'units_sold': 'sum of units_sold', 'category': 'category'}
)
fig_cat.update_layout(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(28,28,30,0.8)',
    showlegend=True, height=420,
    font=dict(color='#a1a1a6'),
    xaxis=dict(gridcolor='#2c2c2e'), yaxis=dict(gridcolor='#2c2c2e'),
    legend=dict(font=dict(color='#ffffff'))
)
st.plotly_chart(fig_cat, use_container_width=True)


# ── Per-category totals row ───────────────────────────────────────────────────
top_cats = cat_summary.nlargest(6, 'units_sold')
cat_cols_display = st.columns(len(top_cats))
for col, (_, row) in zip(cat_cols_display, top_cats.iterrows()):
    col.markdown(f"**{row['category']}:**  \n**{int(row['units_sold']):,}**")

st.markdown("<br>", unsafe_allow_html=True)


# ── Most sold products bar chart ──────────────────────────────────────────────
st.markdown("### Most sold products")

prod_summary = filtered_df.groupby('product_name')['unit_price_usd'].sum().reset_index()
prod_summary.columns = ['product_name', 'sum_price']

fig_prod = px.bar(
    prod_summary, x='product_name', y='sum_price', color='product_name',
    template='plotly_dark',
    labels={'sum_price': 'sum of unit_price_usd', 'product_name': 'product_name'}
)
fig_prod.update_layout(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(28,28,30,0.8)',
    showlegend=True, height=400,
    font=dict(color='#eeeef7'),
    yaxis=dict(gridcolor='#2c2c2e',),
    legend=dict(font=dict(color='#ffffff'))
)
fig_prod.update_xaxes(tickangle=45, gridcolor='#2c2c2e')
st.plotly_chart(fig_prod, use_container_width=True)


# ── Year totals ───────────────────────────────────────────────────────────────
years_list = sorted(filtered_df['sale_year'].unique())
yr_cols = st.columns(len(years_list))
for col, yr in zip(yr_cols, years_list):
    yr_total = len(filtered_df[filtered_df['sale_year'] == yr])
    col.markdown(f"**Total {yr}:**  \n**{yr_total:,}**")

st.markdown(f"**All Years: {len(filtered_df):,}**")