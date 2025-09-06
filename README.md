# finish-mondial-kpis
Climate Change Mitigation KPI Calculator for FINISH Mondial

A Streamlit web application that calculates environmental impact metrics for sanitation projects, including CO₂ emissions saved, energy savings, and nutrient recovery.

## Prerequisites

- Python 3.8+ (recommended: Python 3.10)

## Setup Instructions

1. **Install Python:**
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

## Usage

**Run the Streamlit app:**
```bash
cd finish_mondial_kpis
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Project Structure

```
finish_mondial_kpis/
├── app.py                      # Main Streamlit application
├── calculations_and_mappings.py # Calculation definitions and data loading
├── data/
│   ├── constants.csv           # Calculation constants and parameters
│   ├── data_inputs.csv         # Data input definitions
│   └── projects/               # Pre-populated project data
│       └── custom.csv         # Custom project template
        └── ...
├── images/                     # Application images and icons
└── README.md
```

## Data Structure

### CSV File Format
The application uses a standardized CSV format for project data. This csv can be modified to add project-specific data.
The csv template can be downloaded within the streamlit application

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

## Dependencies

- **streamlit**: Web application framework
- **pandas**: Data manipulation and CSV handling
- **sympy**: Symbolic mathematics for equation generation
