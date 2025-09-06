# Define data categories and field mappings
DATA_CATEGORIES = {
    'compost': 'Compost (t)',
    'cocompost': 'Co-Compost (t)',
    'fs': 'Faecal Sludge (m³)', 
    'recycle': 'Plastic Recycling (t)'
}
DATA_FIELDS = ['Q'] + [f"{key}_q" for key in DATA_CATEGORIES]
QUARTERS = range(1, 5)

# Climate and landfill options
CLIMATE_OPTIONS = {
    "Tropical wet climate": "tropical_wet",
    "Temperate wet climate": "temperate_wet",
    "Dry Climate": "dry_climate"
}
LANDFILL_OPTIONS = {
    "Landfill depth > 5m": "deep",
    "Landfill depth < 5m": "shallow"
}
DISPLAY_MAP = {
    v: k for k, v in {**CLIMATE_OPTIONS, **LANDFILL_OPTIONS}.items()
    }
