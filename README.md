# finish-mondial-kpis
Climate Change Mitigation KPI Calculator for FINISH Mondial

A Streamlit web application that calculates environmental impact metrics for sanitation projects, including CO₂ emissions saved, energy savings, and nutrient recovery.

## Instructions for Using the Web App

### Deployed version
A version of the web app is deployed at https://finish-mondial-lca.streamlit.app

### CSV File Format
The application uses a standardized CSV format for project data, downloadable within the streamlit application. This csv can be modified to add project-specific data.

```
Climate ("temperate_wet" "tropical_wet" or "dry"),,,,
tropical_wet,,,
,,,
Landfill depth ("shallow" if <5m or "deep" if >5m),,,,
deep,,,
,,,
Land Coverage (acres),,,,
500,,,
,,,
# Quarterly Data
Category,Y1Q1,Y1Q2,Y1Q3,Y1Q4
Compost (tonnes),0.0,0.0,0.0,0.0
Co-Compost (tonnes),0.0,0.0,0.0,0.0
Faecal Sludge (m³),0.0,0.0,0.0,0.0
```

## Project Structure

```
finish_mondial_kpis/
├── app.py                      # Main Streamlit application
├── calculations.py             # Calculation definitions and data loading
├── mappings.py                 # Climate and landfill option mappings
├── data/
│   ├── global_parameters.csv  # Non-project-specific parameters
│   ├── project_parameters.csv # Names and symbols for project-specific parameters
│   └── projects/              # Data for project-specific parameters
│       └── custom.csv         # Custom project template
        └── ...
├── images/                    # App images and icons
└── README.md
```

## Instructions for Modifying the App and Underlying Calculations

1. **Install Python 3.9+:**
   - Download from [python.org](https://www.python.org/downloads/) or use your system package manager

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the project:**
   ```bash
   pip install -e .
   ```

4. **Run the Streamlit app:**
```bash
cd finish_mondial_kpis
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

4. **Modify the calculations and parameters:**

   The application automatically generates LaTeX equations from the calculation definitions. To modify calculations and parameters, edit these files:

   **Calculation Formulas** (`finish_mondial_kpis/calculations.py`):
   - Contains all calculation expressions for Parts A-I
   - Defines symbolic equations using SymPy
   - LaTeX formulas are automatically generated from these expressions
   - Modify the `CALCULATION_EXPRESSIONS` dictionary to change calculations

   **Global Parameters** (`finish_mondial_kpis/data/global_parameters.csv`):
   - Contains all parameters and conversion factors (e.g. emission factors, land-use factors, and material properties), organized by calculation section (A-I)
   - Changes are imported to the application

   **Project-Specific Data** (`finish_mondial_kpis/data/projects/*.csv`):
   - Contains quarterly data for each project for compost, co-compost, faecal sludge, and plastic recycling
   - Also includes climate conditions, landfill depth, and land coverage
   - Add new projects by creating additional CSV files in this directory

   **Project-Specific Symbols** (`finish_mondial_kpis/data/project_parameters.csv`):
   - Defines symbolic variables used in calculations
   - Maps variable names to LaTeX representations
   - Used for automatic equation generation

## Dependencies

- **streamlit**: Web application framework
- **pandas**: Data manipulation and CSV handling
- **sympy**: Symbolic mathematics for equation generation
