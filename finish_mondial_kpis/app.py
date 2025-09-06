import streamlit as st
import pandas as pd
import io
import os
import glob
import time
import base64
import requests
import streamlit.components.v1 as components

from mappings import (
    DATA_CATEGORIES, CLIMATE_OPTIONS, LANDFILL_OPTIONS, DISPLAY_MAP, QUARTERS
    )
from calculations import calculate_and_display, base_url

st.set_page_config(
    page_title="Safe Sanitation and Climate Mitigation Calculator",
    page_icon="🌱",
    layout="wide"
)

# CSS for left-aligned LaTeX equations and non-clickable images
# Generated with Claude 
st.markdown("""
<style>
.katex-display {
    text-align: left !important;
    margin-left: 0 !important;
}
.katex {
    text-align: left !important;
}
div[data-testid="stMarkdownContainer"] .katex-display {
    text-align: left !important;
    margin-left: 0 !important;
}
div[data-testid="stMarkdownContainer"] .katex {
    text-align: left !important;
}
/* Hide fullscreen button */
button[title="Fullscreen"] {
    display: none !important;
}
button[aria-label="Fullscreen"] {
    display: none !important;
}
.stButton > button[title="Fullscreen"] {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

def parse_csv_file(content):
    """Parse CSV file in the known format and return project data."""
    lines = content.strip().split('\n')
    climate_setting = lines[1].split(',')[0].strip()
    landfill_setting = lines[4].split(',')[0].strip()
    land_coverage = float(lines[7].split(',')[0].strip())
    
    # Parse quarterly data (starts at line 10, skip the comment line)
    data_content = "\n".join(lines[10:])  # Start from line 11 (index 10) to skip "# Quarterly Data"
    df = pd.read_csv(io.StringIO(data_content), index_col=0)
    
    # Convert to project data format
    project_data = {}
    for category, var_name in DATA_CATEGORIES.items():
        for quarter in QUARTERS:
            project_data[f'{category}_q{quarter}'] = df.loc[var_name, f'Y1Q{quarter}']
    project_data['climate'] = climate_setting
    project_data['landfill_depth'] = landfill_setting
    project_data['land_coverage'] = land_coverage
    
    return project_data


def create_quarterly_dataframe(project_data, num_years, quarterly_cols):
    """Create quarterly data DataFrame from project data and number of years."""    
    # Build data rows
    data = []
    for category_key, category_name in DATA_CATEGORIES.items():
        row = [category_name]  # initialize row
        for year in range(1, num_years + 1):
            for quarter in QUARTERS:
                row.append(project_data.get(f'{category_key}_q{quarter}', 0.0))
        data.append(row)
    
    df = pd.DataFrame(data, columns=[''] + quarterly_cols)
    df = df.set_index('')
    
    # Convert numeric columns
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    return df

@st.cache_data
def load_projects_cached():
    """Load all project data with caching."""
    projects = {}
    # List of project files from GitHub
    project_files = ["arrp","coonoor_mcc", "custom", "krrp"]
    for project_file in project_files:
        project_name = project_file.replace('_', ' ').upper()
        response = requests.get(f"{base_url}data/projects/{project_file}.csv")
        project_data = parse_csv_file(response.text)
        projects[project_name] = project_data
    return projects

@st.cache_data
def load_constants_cached():
    """Load constants from CSV and return as dictionary."""
    constants_df = pd.read_csv(f"{base_url}data/global_parameters.csv")
    return {row['name']: {
        'value': row['value'], 
        'units': row['units'], 
        'source': row['source'], 
        'section': row['section'],
        'latex_name': row['latex_name']
    } for _, row in constants_df.iterrows()}

def get_quarterly_colnames(num_years):
    """Generate quarterly column names for a given number of years."""
    return [f"Y{year}Q{quarter}" for year in range(1, num_years + 1) for quarter in QUARTERS]

def create_csv_template(num_years):
    """Create CSV template in the new format."""
    lines = [
        'Climate ("temperate_wet" "tropical_wet" or "dry"),,,,',
        'tropical_wet,,,',
        ',,,',
        'Landfill depth ("shallow" if <5m or "deep" if >5m),,,,',
        'deep,,,',
        ',,,',
        'Land Coverage (acres),,,,',
        '500,,,',
        ',,,',
        "# Quarterly Data",
        ",".join(["Category"] + get_quarterly_colnames(num_years))
    ]
    
    # Add data rows
    for category_name in DATA_CATEGORIES.values():
        row = [category_name] + ["0.0"] * len(get_quarterly_colnames(num_years))
        lines.append(",".join(row))
    
    return "\n".join(lines)

# Load data
const = load_constants_cached()
projects = load_projects_cached()

# Sidebar
with st.sidebar:
    st.image("https://raw.githubusercontent.com/dalyw/finish-mondial-kpis/refs/heads/main/finish_mondial_kpis/images/logo_finish-wit-retina.png", width=200)
    st.markdown("---")
    
    st.header("About FINISH Mondial")
    st.markdown("""
    [FINISH Mondial](https://finishmondial.org) works with all stakeholders—communities, businesses, financial institutions, and governments—along the entire water and sanitation value chain to create robust ecosystems capable of delivering sustainable and inclusive water and sanitation services.
    """)
    
    st.divider()
    st.subheader("About This Tool")
    st.markdown("""
    This Climate Change Mitigation KPI Calculator helps measure the environmental impact of FINISH Mondial's sanitation projects, including:
    
    - CO₂ emissions saved through compost production, reduced irrigation, and plastic waste reduction and recycling
    - Nutrient recovery from organic waste
    """)

# Main content
response = requests.get(f"{base_url}images/hqdefault.jpg")
img_base64 = base64.b64encode(response.content).decode()
st.markdown(
    f"""
    <div style="position: relative; width: 100%; height: 200px; margin-bottom: -300px;">
        <img src="data:image/jpeg;base64,{img_base64}" 
                style="position: absolute; top: 0; left: 0; width: 100%; height: 150px; 
                    object-fit: cover; opacity: 0.4; z-index: 0;" />
        <div style="position: absolute; top: 20px; left: 0; width: 100%; 
                    text-align: right; z-index: 1;">
        </div>
    </div>
    <br>
    """,
    unsafe_allow_html=True,
)
st.title("Safe Sanitation and Climate Mitigation Calculator")


def switch_tab(tab):
    """Switch to the specified tab (0 for Data Input, 1 for Calculations & Results)."""
    script_placeholder = st.empty()
    components.html(f"""
    <script>
    var tabGroup = window.parent.document.getElementsByClassName("stTabs")[0]
    var tab = tabGroup.getElementsByTagName("button")
    tab[{tab}].click()
    </script>
    """, height=0)
    time.sleep(0.1)
    script_placeholder.empty()


tab1, tab2 = st.tabs(["Data Input", "Calculations & Results"])

with tab1:   # Project data inputs
    col1, col2 = st.columns([2, 1])
    with col1:
        upload_option = st.radio(
            "Data input method:",
            ["Pre-populated project data", "Upload CSV file"],
            horizontal=True
        )
    with col2:
        num_years = st.number_input("Number of Years", min_value=1, max_value=10, value=1, step=1)
        quarterly_cols = get_quarterly_colnames(num_years)

    if upload_option == "Pre-populated project data":
        # Pre-propulate climate conditions, landfill, and quarterly data from selected project
        project_names = list(projects.keys())
        selected_project = st.selectbox("Select Project", project_names)
        project_climate = projects[selected_project]['climate']
        project_landfill = projects[selected_project]['landfill_depth']

    # Quarterly Data Section
    st.subheader("Quarterly Data and Climate")
    if upload_option == "Upload CSV file":
        col1, col2 = st.columns([2, 1])
        with col1:
            uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
        with col2:
            csv_content = create_csv_template(num_years)
            st.download_button(
                label=f"📥 Download CSV Template ({num_years}-year)",
                data=csv_content,
                file_name=f"sample_quarterly_data_{num_years}years.csv",
                mime="text/csv",
            )
        
        if uploaded_file is not None:
            # Read and parse the uploaded CSV
            content = uploaded_file.read().decode('utf-8')
            project_data = parse_csv_file(content)        
            project_climate = project_data['climate']
            project_landfill = project_data['landfill_depth']
            df = create_quarterly_dataframe(project_data, num_years, quarterly_cols)
        else:
            st.info("Please upload a CSV file to continue")
            st.stop()
    else:
        # Drop-down selected project data
        project_data = projects[selected_project]
        df = create_quarterly_dataframe(project_data, num_years, quarterly_cols)

    # Climate and Landfill Conditions (after data loading from csv or project list)
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_climate = st.selectbox("Select Climate Condition", list(CLIMATE_OPTIONS.keys()),
                                    index=list(CLIMATE_OPTIONS.keys()).index(DISPLAY_MAP[project_climate]))
    with col2:
        selected_landfill = st.selectbox("Select Landfill Depth", list(LANDFILL_OPTIONS.keys()),
                                        index=list(LANDFILL_OPTIONS.keys()).index(DISPLAY_MAP[project_landfill]))

    with col3:
        # Get conversion factor based on climate and landfill depth combination
        climate_key = CLIMATE_OPTIONS[selected_climate]
        landfill_key = LANDFILL_OPTIONS[selected_landfill]
        landfill_conversion_factor = const[f"{climate_key}_{landfill_key}"]['value']
        st.metric("Conversion Factor", f"{landfill_conversion_factor:.2f}")

    # Land Coverage Input
    land_coverage = st.number_input(
        "Land Coverage (acres)",
        min_value=0.0, value=float(project_data['land_coverage']), step=5.0, format="%.0f"
    )

    # Display editable table
    column_config = {
        col: st.column_config.NumberColumn(col, min_value=0.0, step=0.1)
        for col in get_quarterly_colnames(num_years)
    } 
    st.write("Edit the values below:")
    edited_df = st.data_editor(df, column_config=column_config)

    # Extract values from edited DataFrame
    sums = {
        f'total_{category}': sum(
            (lambda x: 0 if pd.isna(x) else x)(
                pd.to_numeric(edited_df.loc[category_name][col], errors='coerce')
            )
            for col in quarterly_cols
        )
        for category, category_name in DATA_CATEGORIES.items()
    }

    # Collapsible constants section
    with st.expander("🔧 Adjust Parameters", expanded=False):
        st.write("Modify calculation parameters below. Changes will be applied to all calculations.")
        
        # Group constants by section (excluding Conversions)
        sections = sorted({data['section'] for data in const.values() if data['section'] != 'Conversions'})
        for section in sections:
            st.subheader(f"Part {section} Parameters")
            section_constants = [(name, data) for name, data in const.items() if data['section'] == section]
            cols = st.columns(3)
            
            for i, (name, data) in enumerate(section_constants):
                with cols[i % 3]:
                    const[name]['value'] = st.number_input(
                        f"{name.replace('_', ' ').title()}",
                        value=data['value'],
                        help=f"{data['units']} - Source: {data['source']}",
                        key=f"const_{name}"
                    )
    
    st.divider()
    if st.button("View Results", type="primary"):
        switch_tab(1)

with tab2:
    # Calculate and display results for parts a - i
    results = {}
    for calc_key in ['a', 'b', 'c', 'e', 'f', 'g', 'h', 'i']:
        results[calc_key] = calculate_and_display(calc_key, sums, const, landfill_conversion_factor, land_coverage, st)
        st.divider()

    # Summary
    st.header("Summary")
    col1, col2 = st.columns(2)
    co2_sections = [key for key in results.keys() 
                    if 'co2_saved_[t]' in results[key]]
    total_co2_saved = sum(results[section]['co2_saved_[t]'] for section in co2_sections)
    with col1:
        st.metric("Total CO2 Saved", f"{total_co2_saved:.0f} tCO2e")
        st.metric("Total Compost Generated", f"{sums['total_compost']:.0f} t")
    with col2:
        st.metric("Total Energy Saved", f"{results['f']['total_energy_saved']:.0f} kWh")
        st.metric("Total NPK Recovery", f"{results['e']['total_npk_recovery']:.2f} t")
    
    if st.button("← Back to Data Input", type="secondary"):
        switch_tab(0)
