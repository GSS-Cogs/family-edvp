#!/usr/bin/env python
# coding: utf-8

# ## BEIS-Final-UK-greenhouse-gas-emissions-national-statistics-1990-to-2019

# In[116]:


import json
import pandas as pd
from gssutils import *


# In[117]:


metadata = Scraper(seed="info.json")


# In[118]:


distribution = metadata.distribution(
    latest=True,
    mediaType="application/vnd.oasis.opendocument.spreadsheet",
    title=lambda x: "UK greenhouse gas emissions: final figures - data tables (alternative ODS format)"
    in x,
)


# In[119]:


tabs = distribution.as_databaker()
tabs = [
    tab for tab in tabs if tab.name in ["1_1", "1_2", "1_3", "1_4", "1_5", "1_6", "3_1"]
]


# In[120]:


tidied_sheets = []
for tab in tabs:
    if tab.name == "1_1":

        cell = tab.excel_ref("A1")
        period = cell.shift(0, 5).fill(RIGHT).is_not_blank().is_not_whitespace()
        gas = cell.shift(0, 5).fill(DOWN).is_not_blank().is_not_whitespace()
        unit = "Million of tonnes of carbon dioxide equivalent (MtCO2e)"
        observations = period.waffle(gas)
        dimensions = [
            HDim(period, "Period", DIRECTLY, ABOVE),
            HDim(gas, "Gas", DIRECTLY, LEFT),
            HDimConst("Unit", unit),
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        df = tidy_sheet.topandas()
        tidied_sheets.append(df)
        print(tab.name)

    elif tab.name in ["1_2", "1_3", "1_4", "1_5"]:
        cell = tab.filter("NC Sector")
        period = cell.shift(RIGHT).fill(RIGHT).is_not_blank().is_not_whitespace()
        gas = "All"
        unit = "Million of tonnes of carbon dioxide equivalent (MtCO2e)"
        stop_cell = tab.filter("Grand Total")
        nc_category = tab.filter("NC Category").fill(DOWN)
        nc_sector = nc_category.is_blank().shift(LEFT)
        nc_sub_sector = nc_category.shift(LEFT).is_not_blank()

        if tab.name == "1_2":
            gas = "All"
        elif tab.name == "1_3":
            gas = "Carbon Dioxide CO2"
        elif tab.name == "1_4":
            gas = "Methane CH4"
        elif tab.name == "1_5":
            gas = "Nitrous Oxide N2O"

        observations = period.waffle(nc_category).is_not_blank().is_not_whitespace()

        dimensions = [
            HDim(period, "Period", DIRECTLY, ABOVE),
            HDim(nc_category, "NC Category", DIRECTLY, LEFT),
            HDim(nc_sector, "NC Sector", CLOSEST, ABOVE),
            HDim(nc_sub_sector, "NC Sub Sector", CLOSEST, ABOVE),
            HDimConst("Gas", gas),
            HDimConst("Unit", unit),
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        df = tidy_sheet.topandas()
        tidied_sheets.append(df)
        print(tab.name)

    elif tab.name == "1_6":
        cell = tab.filter("NC Sector")
        period = cell.shift(RIGHT).fill(RIGHT).is_not_blank().is_not_whitespace()
        gas = "All"
        unit = "Million of tonnes of carbon dioxide equivalent (MtCO2e)"

        stop_cell = tab.filter("Grand Total")
        nc_category = tab.filter("NC Category").fill(DOWN)
        nc_sector = nc_category.is_blank().shift(LEFT)

        gas = "Fluorinated Gases F Gases"

        observations = period.waffle(nc_category).is_not_blank().is_not_whitespace()

        dimensions = [
            HDim(period, "Period", DIRECTLY, ABOVE),
            HDim(nc_category, "NC Category", DIRECTLY, LEFT),
            HDim(nc_sector, "NC Sector", CLOSEST, ABOVE),
            HDimConst("Gas", gas),
            HDimConst("Unit", unit),
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        df = tidy_sheet.topandas()
        tidied_sheets.append(df)
        print(tab.name)

    if tab.name == "3_1":
        cell = tab.filter("Geographic coverage")

        period = cell.shift(2).fill(RIGHT).is_not_whitespace()
        gas = cell.shift(2).fill(DOWN).is_not_whitespace()
        inclusions = cell.shift(1).fill(DOWN).is_not_whitespace()

        geographic_coverage = cell.fill(DOWN).is_not_whitespace()

        observations = period.waffle(gas)
        unit = "Million of tonnes of carbon dioxide equivalent (MtCO2e)"

        dimensions = [
            HDim(period, "Period", DIRECTLY, ABOVE),
            HDim(gas, "Gas", DIRECTLY, LEFT),
            HDim(inclusions, "Inclusions-Exclusions", CLOSEST, ABOVE),
            HDim(geographic_coverage, "Geographic Coverage", CLOSEST, ABOVE),
            HDimConst("Unit", unit),
        ]
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        df = tidy_sheet.topandas()
        tidied_sheets.append(df)
        print(tab.name)


# In[121]:


df = pd.concat(tidied_sheets, sort=False).fillna("")


# In[122]:


df.rename(
    columns={
        "OBS": "Value",
        "DATAMARKER": "Marker",
        "Inclusions-Exclusions": "Breakdown",
    },
    inplace=True,
)


# In[123]:


df["Value"] = pd.to_numeric(df["Value"], errors="raise", downcast="float")
df["Value"] = df["Value"].astype(float).round(3)
df["Period"] = df["Period"].astype(float).astype(int)


# In[124]:


df["NC Sub Sector"] = df.apply(
    lambda x: "All" if x["NC Sub Sector"] == x["NC Sector"] else x["NC Sub Sector"],
    axis=1,
)


# In[125]:


badInheritance = [
    "Aviation between UK and Crown Dependencies",
    "Shipping between UK and Crown Dependencies",
    "Aviation between the Crown Dependencies and Overseas Territories",
]

df["Breakdown"] = df.apply(
    lambda x: "" if x["Geographic Coverage"] in badInheritance else x["Breakdown"],
    axis=1,
)
df["Breakdown"] = df.apply(
    lambda x: "None"
    if "" in x["Breakdown"] and x["Geographic Coverage"] == "United Kingdom"
    else x["Breakdown"],
    axis=1,
)
df["Breakdown"] = df.apply(
    lambda x: "None" if x["Geographic Coverage"] in badInheritance else x["Breakdown"],
    axis=1,
)

df["Measure Type"] = "Gas Emissions"
df = df.replace(
    {
        "Gas": {"Total": "All"},
        "Geographic Coverage": {"United Kingdom only": "United Kingdom"},
    }
)

indexNames = df[df["Breakdown"] == "Net emissions/removals from LULUCF"].index
df.drop(indexNames, inplace=True)


# In[126]:


df = df.replace(
    {
        "Geographic Coverage": {"": "United Kingdom"},
        "NC Category": {"": "All"},
        "NC Sub Sector": {"": "All"},
        "NC Sector": {"": "All"},
        "Breakdown": {"": "All"},
    }
)


# In[127]:


df = df.replace({'Gas' : {'Nitrous Oxide N2O' : 'Nitrous oxide (N2O)',
                          'Methane CH4' : 'Methane (CH4)',
                          'Carbon Dioxide CO2' :'Carbon dioxide (CO2)'},
                 'NC Category' : {'Drainage, rewetting and other management of organic and mineral soils - Wetland' : 'Drainage, rewetting and other management of organic and mineral soils - wetland',
                                  'Drainage, rewetting and other management of organic and mineral soils - Settlements' : 'Drainage, rewetting and other management of organic and mineral soils - settlements',
                                  'Drainage, rewetting and other management of organic and mineral soils - Grassland' : 'Drainage, rewetting and other management of organic and mineral soils - grassland'},
                 'NC Sector' : {'Waste Management' : 'Waste management'}})


# In[128]:


COLUMNS_TO_PATHIFY = ["Measure Type", "Unit"]

for col in df.columns.values.tolist():
    if col not in COLUMNS_TO_PATHIFY:
        continue
    try:
        df[col] = df[col].apply(pathify)
    except Exception as err:
        raise Exception('Failed to pathify column "{}".'.format(col)) from err


# In[129]:


df["NC Category"] = df["NC Category"].str.replace("/", "-")
df["Breakdown"] = df["Breakdown"].str.replace("/", "-")

df = df.replace(
    {
        "Breakdown": {
            "excluding-net-emissions-removals-from-land-use-land-use-change-and-forestry-lulucf": "excluding-net-emissions-removals-from-lulucf"
        },
        'Unit' : {'million-of-tonnes-of-carbon-dioxide-equivalent-mtco2e' : 'million-of-tonnes-of-carbon-dioxide-equivalent'}
    }
)


# In[130]:


df = df[
    [
        "Period",
        "Geographic Coverage",
        "NC Sector",
        "NC Sub Sector",
        "NC Category",
        "Gas",
        "Breakdown",
        "Value",
        "Measure Type",
        "Unit"
    ]
]


# In[131]:


df.to_csv("observations.csv", index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file("catalog-metadata.json")


# In[132]:


from IPython.core.display import HTML
for col in df:
    if col not in ['Value']:
        df[col] = df[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(df[col].cat.categories)

