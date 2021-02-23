# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.10.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
import json

import pandas as pd

from gssutils import *

scraper = Scraper(seed = "info.json")
scraper.distributions = [x for x in scraper.distributions if hasattr(x, "mediaType")]
scraper

#Add cubes class
# cubes = Cubes("info.json")

#Add TransformTrace
trace = TransformTrace()
# -

distribution  = scraper.distribution(latest=True, title = lambda x:"2019 UK greenhouse gas emissions: final figures - data tables" in x)
datasetTitle = distribution.title
distribution

# Extract all the tabs and its content from the spread sheet
tabs = distribution.as_databaker()

# +
# # List out all the tab names to cross verify with spread sheet
# for tab in tabs:
#     print(tab.name)
# -

columns = ["Period", "Gas", "dim", "nc_category_child", "nc_sub_sector_parent", "nc_sector_parent"]

# Filtering the tabs which are required and start stage-1 transform
# tabs_i_want = ["1.1"]
# tabs = [x for x in tabs if x.name in tabs_i_want]
for tab in tabs:
    if tab.name == "1.1":
        print(tab.name)
        trace.start(datasetTitle, tab, columns, distribution.downloadURL)

        cell = tab.excel_ref("A1")

        period = cell.shift(0, 2).fill(RIGHT).is_not_blank().is_not_whitespace()


        gas = cell.shift(0, 2).fill(DOWN).is_not_blank().is_not_whitespace()-tab.excel_ref("A").filter(contains_string("Footnotes:")).expand(DOWN).expand(RIGHT)

        unit = "Million tonnes carbon dioxide equivalent (MtCO2e)"
    #     unit = cell.shift(0, 1).expand(RIGHT).filter(lambda x:type(x.value) != "Million tonnes carbon dioxide equivalent (MtCO2e)" in x.value)

        observations = period.waffle(gas)

        dimensions = [
            HDim(period, "Period", DIRECTLY, ABOVE),
            HDim(gas, "Gas", DIRECTLY, LEFT),
            HDimConst("Unit", "Million tonnes carbon dioxide equivalent (MtCO2e)"),
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
        trace.with_preview(tidy_sheet)
        trace.store("combined_dataframe", tidy_sheet.topandas())

# +
# df = trace.combine_and_trace(datasetTitle, "combined_dataframe")
# df
# -

tabs = distribution.as_databaker()

columns = ["Period", "Gas", "dim", "nc_category_child", "nc_sub_sector_parent", "nc_sector_parent"]

# +
# Filtering the tabs which are required and start stage-1 transform
tabs_i_want = ["1.2", "1.3", "1.4", "1.5", "1.6"]
tabs = [x for x in tabs if x.name in tabs_i_want]
for tab in tabs:
    print(tab.name)
    trace.start(datasetTitle, tab, columns, distribution.downloadURL)
    
    cell = tab.excel_ref("A1")
    
    period = cell.shift(1, 2).fill(RIGHT).is_not_blank().is_not_whitespace()
    
    gas = "All"
    
    unit = "Million tonnes carbon dioxide equivalent (MtCO2e)"
    
    nc_category_child = cell.shift(1, 2).fill(DOWN).is_not_blank().is_not_whitespace()
    
    nc_sub_sector_parent = nc_category_child.shift(LEFT).is_not_blank()
    
    nc_sector_parent = nc_category_child.shift(LEFT).shift(ABOVE).is_not_bold() - nc_category_child.shift(LEFT).is_not_bold()

#     nc_sector = cell.shift(0, 2).fill(DOWN).is_not_blank().is_not_whitespace()-tab.excel_ref("A").filter(contains_string("Grand Total"))
#     savepreviewhtml(nc_sector, fname=tab.name + "Preview.html")

    observations = period.waffle(nc_category_child)|period.waffle(nc_sector_parent).is_not_blank().is_not_whitespace()

    dimensions = [
        HDim(period, "Period", DIRECTLY, ABOVE),
        HDim(nc_category_child, "Nc Category Child", CLOSEST, ABOVE),
        HDim(nc_sub_sector_parent, "Nc Sub Sector Parent", CLOSEST, ABOVE),
        HDim(nc_sector_parent, "Nc Sector Parent", CLOSEST, ABOVE),
        HDimConst("Gas", "All"),
        HDimConst("Unit", "Million tonnes carbon dioxide equivalent (MtCO2e)")
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
    trace.with_preview(tidy_sheet)
    trace.store("combined_dataframe", tidy_sheet.topandas())
# +
# df = trace.combine_and_trace(datasetTitle, "combined_dataframe")
# df

# +
# with pd.option_context('display.max_rows', None):
#     print(df[["Nc Category Child", "Nc Sub Sector Parent", "Nc Sector Parent"]])


# +
# df['Gas'].unique()

# +
# df['Nc Sector Parent'].unique()

# +
# df['Nc Sub Sector Parent'].unique()
# -

tabs = distribution.as_databaker()

columns = ["Geographic Coverage", "inclusions-exclusions", "Gas", "Year", "Value"]

# +
for tab in tabs:
    if tab.name == "3.1":
        
        trace.start(datasetTitle, tab, columns, distribution.downloadURL)
        
        remove = tab.filter(contains_string("Footnotes")).expand(RIGHT).expand(DOWN)
#         savepreviewhtml(remove, fname=tab.name + "Preview.html")
        cell = tab.excel_ref("A1")
    
        period = cell.shift(2, 2).fill(RIGHT).is_not_whitespace()
#         savepreviewhtml(period, fname=tab.name + "Preview.html")

        gas = cell.shift(2, 2).fill(DOWN).is_not_whitespace()
#         savepreviewhtml(gas, fname=tab.name + "Preview.html")
        
        inclusions_exclusions = cell.shift(1, 2).fill(DOWN).is_not_whitespace()
#         savepreviewhtml(inclusions_exclusions, fname=tab.name + "Preview.html")

# What to do with Total green house gas emissions at the bottom of dimension
        geographic_coverage = cell.shift(0, 2).fill(DOWN).is_not_whitespace()-remove
#         savepreviewhtml(geographic_coverage, fname=tab.name + "Preview.html")
        
# What to do with Total value(at the bottom) in observation
        observations = period.waffle(gas)
#         savepreviewhtml(observations, fname=tab.name + "Preview.html")
        
        dimensions =[
            HDim(period, "Period", DIRECTLY, ABOVE),
            HDim(gas, "Gas", DIRECTLY, LEFT),
            HDim(inclusions_exclusions, "Inclusions_Exclusions", CLOSEST, ABOVE),
            HDim(geographic_coverage, "Geographic Coverage", CLOSEST, ABOVE) 
        ]
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
        trace.with_preview(tidy_sheet)
        trace.store("combined_dataframe", tidy_sheet.topandas())
# -

df = trace.combine_and_trace(datasetTitle, "combined_dataframe")
df

# : 
df["DATAMARKER"].unique()


