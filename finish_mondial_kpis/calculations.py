"""
Consolidated calculation definitions that automatically generate both LaTeX equations and Python calculations.
This ensures perfect consistency by defining each calculation only once.
Also includes mapping dictionaries, display configurations, and data loading functions.
"""
from sympy import latex, Symbol
import pandas as pd
import os

class CustomSymbol(Symbol):
    """Custom Symbol class with LaTeX name support."""
    def __new__(cls, name, latex_name=None):
        obj = Symbol.__new__(cls, name)
        obj._latex_name = latex_name or name
        return obj
    
    def _latex(self, printer):
        return self._latex_name

def load_symbols_from_csv(url):
    df = pd.read_csv(url)
    return {
        row['name']: CustomSymbol(row['name'], row['latex_name']) 
        for _, row in df.iterrows()
    }

# Load data from GitHub repository
base_url = "https://raw.githubusercontent.com/dalyw/finish-mondial-kpis/refs/heads/main/finish_mondial_kpis/"
data_symbols = load_symbols_from_csv(f"{base_url}data/project_parameters.csv")
constant_symbols = load_symbols_from_csv(f"{base_url}data/global_parameters.csv")

# # Uncomment to load data from local files (temporarily for testing)
# data_symbols = load_symbols_from_csv("data/project_parameters.csv")
# constant_symbols = load_symbols_from_csv("data/global_parameters.csv")
sym = {**data_symbols, **constant_symbols}
sym['landfill_conversion_factor'] = CustomSymbol('landfill_conversion_factor', r'\text{Conversion Factor}')


CALCULATION_EXPRESSIONS = {
    'a': {
        'title': 'Part A: Carbon Emissions Saved Through Compost Production',
        'icon': 'circular-recycle.png',
        'equations': {
            'CO2 Saved [t]': {
                'expression': sym['total_compost'] * sym['landfill_conversion_factor'] * sym['co2_c_ratio'],
                'units': 'tCO2',
                'decimals': 0
            }
        }
    },
    
    'b': {
        'title': 'Part B: Fertilizer Replacement with Compost',
        'icon': 'circular-tractor.png',
        'equations': {
            'CO2 Saved [t]': {
                'expression': sym['n_production_emissions'] * sym['total_cocompost'] * 
                           (sym['n_content_compost'] + sym['p_content_compost'] + sym['k_content_compost']) / sym['kg_per_ton'],
                'units': 'tCO2',
                'decimals': 0
            }
        }
    },
    
    'c': {
        'title': 'Part C: Faecal Sludge Treatment',
        'icon': 'circular-man-bricks.png',
        'equations': {
            'CO2 Saved [t]': {
                'expression': sym['total_fs'] * sym['fs_conversion_factor'],
                'units': 'tCO2',
                'decimals': 0
            }
        }
    },
    'e': {
        'title': 'Part E: Nutrients (NPK) Recovery',
        'icon': 'circular-tractor.png',
        'equations': {
            'Total NPK Recovery': {
                'expression': sym['total_cocompost'] * (sym['n_recovery_content'] + 
                            sym['p2o5_recovery_content'] + sym['k2o_recovery_content']) / sym['kg_per_ton'],
                'units': 't',
                'decimals': 2
            }
        }
    },
    
    'f': {
        'title': 'Part F: Energy Saving Through Reduced Irrigation',
        'icon': 'circular-recycle.png',
        'equations': {
            'Total Energy Saved': {
                'expression': sym['land_coverage'] * sym['energy_per_liter_diesel'] * 
                           sym['diesel_per_acre'] * sym['water_reduction_percent'],
                'units': 'kWh',
                'decimals': 0
            }
        }
    },
    
    'g': {
        'title': 'Part G: CO2 Savings from Diesel Reduction',
        'icon': 'circular-truck.png',
        'equations': {
            'CO2 Saved [t]': {
                'expression': (sym['land_coverage'] * sym['co2_per_liter_diesel'] * 
                            sym['diesel_per_acre'] * sym['water_reduction_percent']) / sym['kg_per_ton'],
                'units': 'tCO2',
                'decimals': 0
            }
        }
    },
    
    'h': {
        'title': 'Part H: Plastic Burning Avoidance',
        'icon': 'circular-recycle.png',
        'equations': {
            'CO2 Saved [t]': {
                'expression': sym['total_recycle'] * sym['plastic_emission_factor'],
                'units': 'tCO2',
                'decimals': 0
            }
        }
    },
    
    'i': {
        'title': 'Part I: Plastic Recycling',
        'icon': 'circular-recycle.png',
        'equations': {
            'CO2 Saved [t]': {
                'expression': sym['total_recycle'] * (sym['new_plastic_emissions'] - sym['recycling_emissions']),
                'units': 'tCO2',
                'decimals': 0
            }
        }
    }
}


def generate_latex(calc_key):
    """Generate LaTeX equation from symbolic expression."""
    calc = CALCULATION_EXPRESSIONS[calc_key]
    equations = []
    mul_symbol = r' \times '
    for label, expr_data in calc['equations'].items():
        equation = expr_data['expression']
        equations.append(f"\\text{{{label}}} = {latex(equation, mul_symbol=mul_symbol)}")
    return "\\begin{align}\n" + " \\\\\n".join(equations) + "\n\\end{align}"


def calculate_and_display(calc_key, sums, const, landfill_conversion_factor, land_coverage, st):
    """Calculate and display results for a given calculation."""
    calc = CALCULATION_EXPRESSIONS[calc_key]
    result = {}
    # create substitution dict for symbol evalution
    subs = {sym[key]: (landfill_conversion_factor if key == 'landfill_conversion_factor' else 
                    land_coverage if key == 'land_coverage' else
                    sums[key] if key in sums else const[key]['value'])
        for key in sym}
        
    # Display icon, section title, and values
    col1, col2, col3 = st.columns([1, 12, 8])
    with col1:
        st.image(f"{base_url}images/{calc['icon']}", width=50)
    with col2:
        st.subheader(calc['title'])
    with col3:  
        for label, expr_data in calc['equations'].items():
            key = label.lower().replace(' ', '_')
            result[key] = float(expr_data['expression'].subs(subs))
            value = f"{result[key]:.{expr_data['decimals']}f} {expr_data['units']}"
            st.metric(label, value)
    
    # Display LaTeX equations
    st.latex(generate_latex(calc_key))
    
    return result