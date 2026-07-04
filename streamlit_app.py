import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="World Happiness Dashboard",
    page_icon="😊",
    layout="wide"
)

# @st.cache_data prevents re-loading the CSV on every interaction
@st.cache_data
def load_data():
    df = pd.read_csv("happiness_report_standardized.csv")
    return df

df = load_data()

# Maps Region_Standardized → broader continent-level group
region_groups = {
    "Europe": [
        "Northern Europe", "Western Europe",
        "Southern Europe", "Eastern Europe"
    ],
    "Asia": [
        "Central Asia", "Eastern Asia", "South-eastern Asia",
        "Southern Asia", "Western Asia"
    ],
    "Africa": [
        "Northern Africa", "Eastern Africa", "Western Africa",
        "Southern Africa", "Middle Africa"
    ],
    "Latin America & Caribbean": [
        "Central America", "South America", "Caribbean"
    ],
    "North America": ["Northern America"],
    "Oceania": ["Australia and New Zealand"]
}

def assign_group(region):
    for group, regions in region_groups.items():
        if region in regions:
            return group
    return "Other"

df["Geographic_Group"] = df["Region_Standardized"].apply(assign_group)

# Consistent with EDA notebook colors
COLOR_PALETTE = {
    "Africa":                    "#E15759",
    "Asia":                      "#F28E2B",
    "Europe":                    "#4E79A7",
    "Latin America & Caribbean": "#59A14F",
    "North America":             "#76B7B2",
    "Oceania":                   "#B07AA1",
    "Global Average":            "#534AB7",
}

with st.sidebar:
    st.title("Filters")
    st.caption(
        "Select regions or countries to compare. "
        "Leave both empty to view the global average."
    )

    # Region filter
    all_regions = sorted(df["Geographic_Group"].dropna().unique().tolist())
    selected_regions = st.multiselect(
        "Geographic Group",
        options=all_regions,
        placeholder="All regions"
    )

    # Country filter — limited to countries in selected regions
    if selected_regions:
        country_pool = df[df["Geographic_Group"].isin(selected_regions)]
    else:
        country_pool = df

    all_countries = sorted(
        country_pool["Country_Standardized"].dropna().unique().tolist()
    )
    selected_countries = st.multiselect(
        "Country",
        options=all_countries,
        placeholder="All countries"
    )

st.title("How Has Happiness Changed Over Time?")
st.markdown("World Happiness Report · 2015 – 2024")
st.divider()

year_min = int(df["Year"].min())
year_max = int(df["Year"].max())

year_range = st.slider(
    "Year range",
    min_value=year_min,
    max_value=year_max,
    value=(year_min, year_max),
    step=1
)

# Apply year filter
df_filtered = df[df["Year"].between(year_range[0], year_range[1])]

# Flag: nothing selected in sidebar
nothing_selected = (len(selected_regions) == 0) and (len(selected_countries) == 0)

# Returns a faint dashed line + label for the global average
# Reused in Case 2, 3, 4 as a background reference
def make_global_baseline(df_filtered):
    df_global = (
        df_filtered
        .groupby("Year")["Happiness score"]
        .mean()
        .reset_index()
        .rename(columns={"Happiness score": "Avg Score"})
    )

    line = (
        alt.Chart(df_global)
        .mark_line(
            strokeWidth=1.5,
            color=COLOR_PALETTE["Global Average"],
            strokeDash=[4, 4],
            opacity=0.5
        )
        .encode(
            x=alt.X("Year:O"),
            y=alt.Y("Avg Score:Q", scale=alt.Scale(domain=[0, 10])),
            tooltip=[
                alt.Tooltip("Year:O", title="Year"),
                alt.Tooltip("Avg Score:Q", title="Global Avg", format=".2f")
            ]
        )
    )

    label = (
        alt.Chart(df_global.tail(1))
        .mark_text(align="left", dx=8, fontSize=11,
                   color=COLOR_PALETTE["Global Average"], opacity=0.7)
        .encode(
            x=alt.X("Year:O"),
            y=alt.Y("Avg Score:Q"),
            text=alt.value("Global Avg")
        )
    )

    return line, label


# Shows when nothing is selected in the sidebar
if nothing_selected:

    df_global = (
        df_filtered
        .groupby("Year")["Happiness score"]
        .mean()
        .reset_index()
        .rename(columns={"Happiness score": "Avg Score"})
    )

    line = (
        alt.Chart(df_global)
        .mark_line(strokeWidth=3, color=COLOR_PALETTE["Global Average"], point=True)
        .encode(
            x=alt.X("Year:O", title="Year"),
            y=alt.Y("Avg Score:Q", title="Average Happiness Score",
                     scale=alt.Scale(domain=[0, 10])),
            tooltip=[
                alt.Tooltip("Year:O", title="Year"),
                alt.Tooltip("Avg Score:Q", title="Global Avg", format=".2f")
            ]
        )
    )

    label = (
        alt.Chart(df_global.tail(1))
        .mark_text(align="left", dx=8, fontSize=12, color=COLOR_PALETTE["Global Average"])
        .encode(x=alt.X("Year:O"), y=alt.Y("Avg Score:Q"), text=alt.value("Global Average"))
    )

    chart = alt.layer(line, label).properties(width="container", height=450)

elif len(selected_regions) > 0 and len(selected_countries) == 0:

    global_line, global_label = make_global_baseline(df_filtered)

    df_region = (
        df_filtered[df_filtered["Geographic_Group"].isin(selected_regions)]
        .groupby(["Year", "Geographic_Group"])["Happiness score"]
        .mean().reset_index()
        .rename(columns={"Happiness score": "Avg Score"})
    )

    region_line = (
        alt.Chart(df_region)
        .mark_line(strokeWidth=2.5, point=True, strokeDash=[6, 3])
        .encode(
            x=alt.X("Year:O", title="Year"),
            y=alt.Y("Avg Score:Q", title="Average Happiness Score",
                     scale=alt.Scale(domain=[0, 10])),
            color=alt.Color(
                "Geographic_Group:N", title="Region",
                # Only show selected regions in the legend
                scale=alt.Scale(
                    domain=selected_regions,
                    range=[COLOR_PALETTE.get(r, "#999999") for r in selected_regions]
                )
            ),
            tooltip=[
                alt.Tooltip("Year:O", title="Year"),
                alt.Tooltip("Geographic_Group:N", title="Region"),
                alt.Tooltip("Avg Score:Q", title="Avg Score", format=".2f")
            ]
        )
    )

    chart = (
        alt.layer(global_line, global_label, region_line)
        .properties(width="container", height=450)
    )

elif len(selected_regions) == 0 and len(selected_countries) > 0:

    global_line, global_label = make_global_baseline(df_filtered)

    df_country = (
        df_filtered[df_filtered["Country_Standardized"].isin(selected_countries)]
        .rename(columns={"Happiness score": "Avg Score"})
    )

    country_line = (
        alt.Chart(df_country)
        .mark_line(strokeWidth=2, point=True)
        .encode(
            x=alt.X("Year:O", title="Year"),
            y=alt.Y("Avg Score:Q", title="Average Happiness Score",
                     scale=alt.Scale(domain=[0, 10])),
            # Only selected countries appear in legend
            color=alt.Color("Country_Standardized:N", title="Country"),
            tooltip=[
                alt.Tooltip("Year:O", title="Year"),
                alt.Tooltip("Country_Standardized:N", title="Country"),
                alt.Tooltip("Geographic_Group:N", title="Region"),
                alt.Tooltip("Avg Score:Q", title="Score", format=".2f")
            ]
        )
    )

    chart = (
        alt.layer(global_line, global_label, country_line)
        .properties(width="container", height=450)
    )

elif len(selected_regions) == 0 and len(selected_countries) > 0:

    global_line, global_label = make_global_baseline(df_filtered)

    df_country = (
        df_filtered[df_filtered["Country_Standardized"].isin(selected_countries)]
        .rename(columns={"Happiness score": "Avg Score"})
    )

    country_line = (
        alt.Chart(df_country)
        .mark_line(strokeWidth=2, point=True)
        .encode(
            x=alt.X("Year:O", title="Year"),
            y=alt.Y("Avg Score:Q", title="Average Happiness Score",
                     scale=alt.Scale(domain=[0, 10])),
            # Only selected countries appear in legend
            color=alt.Color("Country_Standardized:N", title="Country"),
            tooltip=[
                alt.Tooltip("Year:O", title="Year"),
                alt.Tooltip("Country_Standardized:N", title="Country"),
                alt.Tooltip("Geographic_Group:N", title="Region"),
                alt.Tooltip("Avg Score:Q", title="Score", format=".2f")
            ]
        )
    )

    chart = (
        alt.layer(global_line, global_label, country_line)
        .properties(width="container", height=450)
    )

else:

    global_line, global_label = make_global_baseline(df_filtered)

    df_region = (
        df_filtered[df_filtered["Geographic_Group"].isin(selected_regions)]
        .groupby(["Year", "Geographic_Group"])["Happiness score"]
        .mean().reset_index()
        .rename(columns={"Happiness score": "Avg Score"})
    )
    df_region["Label"] = df_region["Geographic_Group"]

    df_country = (
        df_filtered[df_filtered["Country_Standardized"].isin(selected_countries)]
        .rename(columns={"Happiness score": "Avg Score"})
    )
    df_country["Label"] = df_country["Country_Standardized"]

    # Combine region + country into one color domain → one legend
    combined_labels = selected_regions + selected_countries
    combined_colors = (
        [COLOR_PALETTE.get(r, "#999999") for r in selected_regions]
        + ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
           "#9467bd", "#8c564b", "#e377c2", "#7f7f7f",
           "#bcbd22", "#17becf"][:len(selected_countries)]
    )

    region_line = (
        alt.Chart(df_region)
        .mark_line(strokeWidth=2.5, point=True, strokeDash=[6, 3])
        .encode(
            x=alt.X("Year:O", title="Year"),
            y=alt.Y("Avg Score:Q", title="Average Happiness Score",
                     scale=alt.Scale(domain=[0, 10])),
            color=alt.Color("Label:N", title="Region / Country",
                             scale=alt.Scale(domain=combined_labels, range=combined_colors)),
            tooltip=[
                alt.Tooltip("Year:O", title="Year"),
                alt.Tooltip("Label:N", title="Region"),
                alt.Tooltip("Avg Score:Q", title="Avg Score", format=".2f")
            ]
        )
    )

    country_line = (
        alt.Chart(df_country)
        .mark_line(strokeWidth=2, point=True)
        .encode(
            x=alt.X("Year:O", title="Year"),
            y=alt.Y("Avg Score:Q", scale=alt.Scale(domain=[0, 10])),
            color=alt.Color("Label:N", title="Region / Country",
                             scale=alt.Scale(domain=combined_labels, range=combined_colors)),
            tooltip=[
                alt.Tooltip("Year:O", title="Year"),
                alt.Tooltip("Label:N", title="Country"),
                alt.Tooltip("Geographic_Group:N", title="Region"),
                alt.Tooltip("Avg Score:Q", title="Score", format=".2f")
            ]
        )
    )

    chart = (
        alt.layer(global_line, global_label, region_line, country_line)
        .properties(width="container", height=450)
    )

# Render chart
st.altair_chart(
    chart.configure_axis(labelFontSize=12, titleFontSize=13)
         .configure_legend(labelFontSize=12, titleFontSize=13),
    use_container_width=True
)