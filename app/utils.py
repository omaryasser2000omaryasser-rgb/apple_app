import streamlit as st
import pandas as pd


DARK_CSS = """
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
.nav-inactive{ background: #2c2c2e; color: #f5f5f7 !important; }

.kpi-card {
    background: #1c1c1e;
    border-radius: 18px;
    padding: 24px 20px;
    border: 1px solid #2c2c2e;
    text-align: center;
}
.kpi-value { font-size: 28px; font-weight: 700; color: #34c759 !important; }
.kpi-label { font-size: 12px; color: #86868b !important; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 4px; }
</style>
"""


def render_sidebar(df, page_key=""):
    """Renders the shared sidebar and returns the active filters."""
    st.sidebar.markdown("## 🍎 Apple Sales")
    st.sidebar.markdown("---")

    price_min = float(df['unit_price_usd'].min())
    price_max = float(df['unit_price_usd'].max())
    price = st.sidebar.slider('Price', min_value=price_min, max_value=price_max,
                               value=(price_min, price_max), format='$%.2f',
                               key=f'price_{page_key}')

    st.sidebar.markdown("**Select Age Groups:**")
    age_groups = sorted(df['customer_age_group'].dropna().unique().tolist())
    selected_ages = []
    for ag in age_groups:
        if st.sidebar.checkbox(ag, value=True, key=f'age_{ag}_{page_key}'):
            selected_ages.append(ag)

    years = st.sidebar.multiselect('Year',
                                    options=sorted(df['sale_year'].unique()),
                                    default=sorted(df['sale_year'].unique()),
                                    key=f'years_{page_key}')

    categories = st.sidebar.multiselect('Products',
                                         options=sorted(df['category'].unique()),
                                         default=sorted(df['category'].unique()),
                                         key=f'cats_{page_key}')

    return price, selected_ages, years, categories


def apply_filters(df, price, selected_ages, years, categories):
    return df[
        (df['unit_price_usd'] >= price[0]) &
        (df['unit_price_usd'] <= price[1]) &
        (df['customer_age_group'].isin(selected_ages)) &
        (df['sale_year'].isin(years)) &
        (df['category'].isin(categories))
    ]


def nav_bar(active: str):
    pages = {
        'Category':   ('🏠', '/'),
        'Continents': ('🌐', '/Continents'),
        'Age_Group':  ('👥', '/Age_Group'),
        'Payment':    ('💳', '/Payment'),
    }
    pills = ""
    for name, (icon, href) in pages.items():
        cls = 'nav-active' if name == active else 'nav-inactive'
        if name == active:
            pills += f"<span class='nav-pill {cls}'>{icon} {name}</span>"
        else:
            pills += f"<a href='{href}' target='_self' style='text-decoration:none;'><span class='nav-pill {cls}'>{icon} {name}</span></a>"
    st.markdown(f"<div style='display:flex; gap:12px; padding:16px 0 24px 0;'>{pills}</div>",
                unsafe_allow_html=True)


def kpi_row(metrics: list):
    """metrics = list of (value_str, label_str)"""
    cols = st.columns(len(metrics))
    for col, (val, label) in zip(cols, metrics):
        col.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-value'>{val}</div>
            <div class='kpi-label'>{label}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


PLOTLY_DARK = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(28,28,30,0.8)',
    font=dict(color='#ffffff'),        # ← this controls ALL text including legend
    xaxis=dict(gridcolor='#2c2c2e',),
    yaxis=dict(gridcolor='#2c2c2e'),
    legend=dict(font=dict(color='#ffffff')),  # ← explicit legend override
)
