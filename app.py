import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------ CONFIG ------------------
st.set_page_config(page_title="Sri Lanka Industrial Data", layout="wide")

DATA_URL = "processed_industry_data.csv"

# ------------------ DATA ------------------
@st.cache_data
def get_data(path):
    return pd.read_csv(path)

df = get_data(DATA_URL)

# ------------------ SIDEBAR ------------------
def sidebar_navigation():
    return st.sidebar.selectbox("Select Page", ["Introduction", "Dashboard", "Filter Data"])

# ------------------ HELPERS ------------------
def format_year_axis(fig):
    years = sorted(df["Year"].unique())
    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=years,
            ticktext=[str(y) for y in years],
            title="Year"
        ),
        yaxis_title="Number of Employees"
    )
    return fig

# ------------------ INTRO PAGE ------------------
def render_intro():
    st.markdown("""
        <style>
        .intro {
            background-image: url('https://i.pinimg.com/736x/80/72/7a/80727a88eed6332612b325b6ef8b437c.jpg');
            background-size: cover;
            padding: 4rem;
            border-radius: 10px;
            background-color: rgba(255,255,255,0.85);
        }
        </style>
        <div class="intro">
        <h1 style="color:#C9DFFF;">Sri Lanka Industrial Employment Dashboard</h1>
        <p style="color:#ADD9E0;">Interactive insights into industrial workforce trends.</p>
        <ul>
            <li>Trend analysis</li>
            <li>Industry comparisons</li>
            <li>Category distributions</li>
            <li>Downloadable filters</li>
        </ul>
        </div>
    """, unsafe_allow_html=True)

# ------------------ KPI BLOCK ------------------
def render_kpis(data, year):
    st.subheader("Key Metrics")

    total = data["Number of Employees"].sum()
    avg = data["Number of Employees"].mean()

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Employees", f"{total:,.2f}")
    c2.metric("Average Employees", f"{avg:,.2f}")
    c3.metric("Selected Scope", "Overall" if year == "Overall" else year)

# ------------------ DASHBOARD ------------------
def render_dashboard():
    st.title("Industrial Data Dashboard")

    # toggles
    if st.sidebar.checkbox("Raw Data"):
        st.dataframe(df)

    if st.sidebar.checkbox("Summary Stats"):
        st.write(df.describe())

    # year filter
    years = ["Overall"] + sorted(df["Year"].unique())
    selected_year = st.sidebar.selectbox("KPI Year", years)

    filtered = df if selected_year == "Overall" else df[df["Year"] == selected_year]

    render_kpis(filtered, selected_year)

    tabs = st.tabs([
        "Trend", "Industry", "Distribution",
        "Cumulative", "Category", "Bubble"
    ])

    # --- Trend ---
    with tabs[0]:
        temp = df.groupby("Year")["Number of Employees"].sum().reset_index()
        fig = px.line(temp, x="Year", y="Number of Employees", markers=True)
        st.plotly_chart(format_year_axis(fig), use_container_width=True)

    # --- Industry ---
    with tabs[1]:
        agg = df.groupby("ISIC Rev 3")["Number of Employees"].sum().reset_index()
        fig = px.bar(agg, x="ISIC Rev 3", y="Number of Employees")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

        selected = st.sidebar.multiselect(
            "Industries",
            sorted(df["ISIC Rev 3"].unique()),
            default=sorted(df["ISIC Rev 3"].unique())[:5]
        )

        sub = filtered[filtered["ISIC Rev 3"].isin(selected)]
        fig2 = px.bar(sub, x="ISIC Rev 3", y="Number of Employees")
        st.plotly_chart(fig2, use_container_width=True)

    # --- Distribution ---
    with tabs[2]:
        cats = st.multiselect(
            "Categories",
            df["Industry_Category"].unique(),
            default=df["Industry_Category"].unique()
        )

        pie_df = filtered[filtered["Industry_Category"].isin(cats)]
        pie_df = pie_df.groupby("Industry_Category")["Number of Employees"].sum().reset_index()

        fig = px.pie(pie_df, values="Number of Employees", names="Industry_Category")
        st.plotly_chart(fig, use_container_width=True)

    # --- Cumulative ---
    with tabs[3]:
        cum = filtered.groupby("Year")["Number of Employees"].sum().cumsum().reset_index()
        fig = px.area(cum, x="Year", y="Number of Employees")
        st.plotly_chart(format_year_axis(fig), use_container_width=True)

    # --- Category ---
    with tabs[4]:
        cat = filtered.groupby("Industry_Category")["Number of Employees"].sum().reset_index()
        fig = px.bar(cat, x="Industry_Category", y="Number of Employees")
        st.plotly_chart(fig, use_container_width=True)

    # --- Bubble ---
    with tabs[5]:
        fig = px.scatter(
            filtered,
            x="Year",
            y="Number of Employees",
            size="Number of Employees",
            color="Industry_Category",
            hover_name="ISIC Rev 3",
            size_max=60
        )
        st.plotly_chart(format_year_axis(fig), use_container_width=True)
    
    # ------------------ FILTER PAGE ------------------
def render_filter():
    st.title("Filter & Export")

    year = st.sidebar.selectbox("Year", sorted(df["Year"].unique()))
    industry = st.sidebar.selectbox("Industry", sorted(df["ISIC Rev 3"].unique()))

    df_year = df[df["Year"] == year]
    df_ind = df[df["ISIC Rev 3"] == industry]

    st.subheader(f"Year: {year}")
    st.dataframe(df_year)

    st.subheader(f"Industry: {industry}")
    st.dataframe(df_ind)

    st.download_button(
        "Download Year Data",
        df_year.to_csv(index=False),
        f"year_{year}.csv"
    )

    st.download_button(
        "Download Industry Data",
        df_ind.to_csv(index=False),
        f"industry_{industry}.csv"
    )
    
# ------------------ ROUTER ------------------
page = sidebar_navigation()

if page == "Introduction":
    render_intro()
elif page == "Dashboard":
    render_dashboard()
else:
    render_filter()
    
