import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Car MPG Dashboard", layout="wide")

# load data
@st.cache_data
def load_data():
    df = pd.read_csv("mpg.csv").dropna()
    df["origin"] = df["origin"].str.capitalize()
    df["model_year"] = df["model_year"].apply(lambda y: 1900 + y)
    return df

df = load_data()

st.title("Car Fuel Efficiency Dashboard")
st.write("Explore how car characteristics like weight, horsepower, and origin affect fuel efficiency across model years from 1970 to 1982.")

# sidebar filters
st.sidebar.header("Filters")

origins = st.sidebar.multiselect(
    "Country of Origin",
    options=sorted(df["origin"].unique()),
    default=sorted(df["origin"].unique())
)

cylinders = st.sidebar.multiselect(
    "Cylinders",
    options=sorted(df["cylinders"].unique()),
    default=sorted(df["cylinders"].unique())
)

year_range = st.sidebar.slider(
    "Model Year",
    min_value=int(df["model_year"].min()),
    max_value=int(df["model_year"].max()),
    value=(int(df["model_year"].min()), int(df["model_year"].max()))
)

if st.sidebar.button("Reset Filters"):
    st.rerun()

# apply filters
filtered = df[
    df["origin"].isin(origins) &
    df["cylinders"].isin(cylinders) &
    df["model_year"].between(*year_range)
]

st.caption(f"{len(filtered)} of {len(df)} cars shown")

# tabs
tab1, tab2, tab3 = st.tabs(["Overview", "Analysis", "Data"])

with tab1:
    # summary metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Average MPG", f"{filtered['mpg'].mean():.1f}")
    col2.metric("Best MPG", f"{filtered['mpg'].max():.1f}")
    col3.metric("Avg Horsepower", f"{filtered['horsepower'].mean():.0f}")
    col4.metric("Total Cars", len(filtered))

    st.divider()

    # MPG over time by origin
    trend = filtered.groupby(["model_year", "origin"])["mpg"].mean().reset_index()
    fig = px.line(trend, x="model_year", y="mpg", color="origin", markers=True,
                  title="Average MPG Over Time by Origin",
                  labels={"model_year": "Year", "mpg": "Avg MPG", "origin": "Origin"})
    st.plotly_chart(fig, use_container_width=True)

    # MPG by cylinders
    col1, col2 = st.columns(2)
    with col1:
        avg_cyl = filtered.groupby("cylinders")["mpg"].mean().reset_index()
        fig = px.bar(avg_cyl, x="cylinders", y="mpg",
                     title="Average MPG by Cylinders",
                     labels={"cylinders": "Cylinders", "mpg": "Avg MPG"})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.box(filtered, x="origin", y="mpg", color="origin",
                     title="MPG Distribution by Origin",
                     labels={"origin": "Origin", "mpg": "MPG"})
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    # scatter plots
    col1, col2 = st.columns(2)
    with col1:
        fig = px.scatter(filtered, x="weight", y="mpg", color="origin",
                         hover_data=["name", "model_year"],
                         title="Weight vs MPG",
                         labels={"weight": "Weight (lbs)", "mpg": "MPG", "origin": "Origin"},
                         opacity=0.7)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.scatter(filtered, x="horsepower", y="mpg", color="origin",
                         hover_data=["name", "model_year"],
                         title="Horsepower vs MPG",
                         labels={"horsepower": "Horsepower", "mpg": "MPG", "origin": "Origin"},
                         opacity=0.7)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    with st.expander("About this dataset"):
        st.write("""
            The Auto MPG dataset comes from the UCI Machine Learning Repository.
            It contains data on 398 cars from 1970 to 1982, with information on
            fuel efficiency, engine specs, weight, and country of origin.
            Rows with missing values have been dropped, leaving 392 cars.
        """)

    st.dataframe(filtered.reset_index(drop=True), use_container_width=True)

    csv = filtered.to_csv(index=False)
    st.download_button("Download filtered data as CSV", csv, "mpg_filtered.csv", "text/csv")
