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
cubes = Cubes("info.json")

#Add TransformTrace
trace = TransformTrace()
# -

distribution  = scraper.distribution(latest=True, title = lambda x:"2019 UK greenhouse gas emissions: final figures - data tables" in x)
datasetTitle = distribution.title
distribution

# Extract all the tabs and its content from the spread sheet
tabs = distribution.as_databaker()

# List out all the tab names to cross verify with spread sheet
for tab in tabs:
    print(tab.name)

columns = ["Period", "Gas", "dim", "nc_category_child", "nc_sub_sector_parent", "nc_sector_parent", "Unit"]

# Filtering the tabs which are required and start stage-1 transform
for tab in tabs:
    if tab.name == "1.1":
        print(tab.name)
        trace.start(datasetTitle, tab, columns, distribution.downloadURL)
        remove = tab.filter(contains_string("Footnotes")).expand(RIGHT).expand(DOWN)
#         savepreviewhtml(remove, fname=tab.name + "Preview.html")
        
        cell = tab.excel_ref("A1")

        period = cell.shift(0, 2).fill(RIGHT).is_not_blank().is_not_whitespace()
        trace.Period('Defined from cell B3 right')

        gas = cell.shift(0, 2).fill(DOWN).is_not_blank().is_not_whitespace()-remove
        trace.Gas("Defined from cell A4 down")
        
        unit = "Million tonnes carbon dioxide equivalent (MtCO2e)"
        trace.Unit("Hard coded as Million tonnes carbon dioxide equivalent (MtCO2e)")

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

tabs = distribution.as_databaker()

columns = ["Period", "Gas", "Nc_Category_Child", "Nc_Sub_Sector_Parent", "Nc_Sector_Parent", "Unit"]

# Filtering the tabs which are required and start stage-1 transform
tabs_i_want = ["1.2", "1.3", "1.4", "1.5", "1.6"]
tabs = [x for x in tabs if x.name in tabs_i_want]
for tab in tabs:
    print(tab.name)
    trace.start(datasetTitle, tab, columns, distribution.downloadURL)

    cell = tab.excel_ref("A1")

    period = cell.shift(1, 2).fill(RIGHT).is_not_blank().is_not_whitespace()
    trace.Period("Defined from cell C3 right")

    gas = "All"
    trace.Gas("Hardcoded as all")

    unit = "Million tonnes carbon dioxide equivalent (MtCO2e)"
    trace.Unit("Hardcoded as Million tonnes carbon dioxide equivalent (MtCO2e)")

    nc_category_child = cell.shift(1, 2).fill(DOWN)
    trace.Nc_Category_Child("Defined from cell B4 down")

    nc_sub_sector_parent = nc_category_child.shift(LEFT).is_not_blank()
    trace.Nc_Sub_Sector_Parent("Defined from cell A3 down which is not bold")

    nc_sector_parent = nc_category_child.shift(LEFT).shift(ABOVE).is_not_bold() - nc_category_child.shift(LEFT).is_not_bold()
    trace.Nc_Sector_Parent("Defined from cell A3 down which is bold")

    observations = period.waffle(nc_category_child).is_not_blank().is_not_whitespace()
    
    dimensions = [
        HDim(period, "Period", DIRECTLY, ABOVE),
        HDim(nc_category_child, "Nc Category Child", CLOSEST, ABOVE),
        HDim(nc_sub_sector_parent, "Nc Sub Sector Parent", CLOSEST, ABOVE),
        HDim(nc_sector_parent, "Nc Sector Parent", CLOSEST, ABOVE),
        HDimConst("Gas", "All"),
        HDimConst("Unit", "Million tonnes carbon dioxide equivalent (MtCO2e)")
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    # savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
    # trace.with_preview(tidy_sheet)
    trace.store("combined_dataframe", tidy_sheet.topandas())


columns = ["Period", "Geographic Coverage", "Inclusions-Exclusions", "Gas", "Year", "Value"]

tabs = distribution.as_databaker()
for tab in tabs:
    if tab.name == "3.1":
        
        trace.start(datasetTitle, tab, columns, distribution.downloadURL)
        
        remove = tab.filter(contains_string("Footnotes")).expand(RIGHT).expand(DOWN)
        cell = tab.excel_ref("A1")
    
        period = cell.shift(2, 2).fill(RIGHT).is_not_whitespace()
        trace.Period("Defined from cell D3 and right")

        gas = cell.shift(2, 2).fill(DOWN).is_not_whitespace()
        trace.Gas("Defined from cell C3 down")
        
        inclusions_exclusions = cell.shift(1, 2).fill(DOWN).is_not_whitespace()
        trace.Inclusions_Exclusions("Defined from cell B3 down")

        geographic_coverage = cell.shift(0, 2).fill(DOWN).is_not_whitespace()-remove
        trace.Geographic_Coverage("Defined from cell A3 down")
        
        observations = period.waffle(gas)-remove
        
        dimensions =[
            HDim(period, "Period", DIRECTLY, ABOVE),
            HDim(gas, "Gas", DIRECTLY, LEFT),
            HDim(inclusions_exclusions, "Inclusions Exclusions", CLOSEST, ABOVE),
            HDim(geographic_coverage, "Geographic Coverage", CLOSEST, ABOVE ),
            HDimConst("Unit", "TBD - needs investigating")
        ]
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
        trace.with_preview(tidy_sheet)
        trace.store("combined_dataframe", tidy_sheet.topandas())

df = trace.combine_and_trace(datasetTitle, "combined_dataframe").fillna('')
df.rename(columns = {'OBS': 'Value', 'DATAMARKER':'Marker'}, inplace = True)

# +
# replace the nans now we've confirmed they're where they should be
replace_nans = {
    "Marker": "",
    "Nc Category Child": "all",
    "Nc Sub Sector Parent": "all",
    "Nc Sector Parent": "all",
    "Inclusions Exclusions": "all",
    "Geographic Coverage": "all"
}
for col, na_val in replace_nans.items():
    df[col][df[col] == ""] = na_val

# confirm there's no blanks remaining where there shouldn't be blanks
for col in [x for x in df.columns.values if x not in ["Value", "Marker"]]:
    assert "" not in df[col].unique(), f'Column "{col}" has one or more blank entries and shouldn\'t. Got {df[col].unique()}'

df


# +
def left(s, amount):
    return s[:amount]
def date_time (date):
    if len(date) == 6:
        return 'year/' + left(date, 4)
    
df['Period'] =  df["Period"].apply(date_time)
# -

df.rename(columns = {'OBS': 'Value', 'DATAMARKER':'Marker'}, inplace = True)

# +
COLUMNS_TO_NOT_PATHIFY = ['Period', 'Value']

for col in df.columns.values.tolist():
    if col in COLUMNS_TO_NOT_PATHIFY:
        continue
    try:
        df[col] = df[col].apply(pathify)
    except Exception as err:
        raise Exception('Failed to pathify column "{}".'.format(col)) from err

df
# -

cubes.add_cube(scraper, df.drop_duplicates(), datasetTitle)
cubes.output_all()

trace.render("spec_v1.html")
