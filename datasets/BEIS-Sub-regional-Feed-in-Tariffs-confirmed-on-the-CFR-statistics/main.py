#!/usr/bin/env python
# coding: utf-8
# %%
from gssutils import *
import pandas as pd
import json

#extract spread sheet from landing page
scraper = Scraper(seed="info.json")
scraper.distributions = [x for x in scraper.distributions if hasattr(x, "mediaType")]
scraper

# Add cubes class
cubes = Cubes("info.json")
#Add tracer to transform
trace = TransformTrace()


# %%
# extract latest distribution and datasetTitle
distribution = scraper.distribution(latest = True)
datasetTitle = distribution.title
print(distribution.downloadURL)
print(datasetTitle)


# %%
# Extract all the tabs from the spread sheet
tabs = {tab.name: tab for tab in distribution.as_databaker()}


# %%
# List out all the tab name to cross verify with the spread sheet
for tab in tabs:
    print(tab)


# %%
columns = ["Region", "Period", "Technology", "Installation", "Households", "Local Or Parliamentary Code",
           "Local Enterprise Partnerships", "Leps Authority", "Marker", "Unit"]


# %%
# Filtering out the tabs which are not required and start the transform 
for name, tab in tabs.items():
    if 'Title' in name or 'Calculation' in name     or'Latest Quarter - LA' in name or 'Latest Quarter - LA (kW)' in name     or 'Latest Quarter - PC' in name or 'Latest Quarter - PC (kW)' in name     or 'Latest Quarter - LEPs' in name or 'Latest Quarter - LEPs (kW)' in name:
        continue
    print(tab.name)
    trace.start(datasetTitle, tab, columns, distribution.downloadURL)
        
    cell = tab.excel_ref("B7")
    
    footer = tab.filter(contains_string("Notes")).expand(RIGHT).expand(DOWN)
    
    region = cell.fill(DOWN).is_not_blank().is_not_whitespace()-footer
    trace.Region("Taken from cell B7 down excluding footer")
        
    households = cell.fill(RIGHT).is_not_blank().is_not_whitespace()
    trace.Households("Taken from cell B7 right")
        
    technology = cell.shift(0, -1).fill(RIGHT).is_not_blank().is_not_whitespace()
    trace.Technology("Taken from cell B6 right which is not blank")

    #installation may potentially become measure type. A word from DM is awaited.    
    installation = cell.shift(0, -2).fill(RIGHT).is_not_blank().is_not_whitespace()
    trace.Installation("Taken from cell B5 right which is not blank")

    period = cell.shift(0, -4).fill(RIGHT).is_not_blank().is_not_whitespace()
    trace.Period("taken from cell B3 right which is not blank")

    observations = region.fill(RIGHT).is_not_blank().is_not_whitespace()-footer

    dimensions = [
        HDim(region, "Region", DIRECTLY, LEFT),
        HDim(households, "Households", CLOSEST, LEFT),
        HDim(technology, "Technology", CLOSEST, LEFT),
        HDim(installation, "Installation", CLOSEST, LEFT),
        HDim(period, "Period", CLOSEST, LEFT)
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    savepreviewhtml(tidy_sheet,fname=tab.name + "Preview.html")
    trace.with_preview(tidy_sheet)
    trace.store("combined_dataframe", tidy_sheet.topandas())


# %%
for name, tab in tabs.items():
    if 'Title' in name or 'Calculation' in name     or 'Latest Quarter - Region' in name or 'Latest Quarter - Region (kW)' in name     or 'Latest Quarter - LEPs' in name or 'Latest Quarter - LEPs (kW)' in name:
        continue
    print(tab.name)
    trace.start(datasetTitle, tab, columns, distribution.downloadURL)   
    cell = tab.excel_ref("B7")
    
# Datamarker is catching footer values from Latest Quarter - LA and Latest Quarter - LA (kW) tabs
    footer = tab.filter(contains_string("Notes")).expand(RIGHT).expand(DOWN)
    
    #datamarker is catching weired values from footer so footer is caught and deleted    
    local_or_parliamentary_code = cell.fill(DOWN).is_not_blank().is_not_whitespace()-footer
    trace.Local_Or_Parliamentary_Code("Taken from cell B7 down excluding footer")

    households = cell.shift(1, 0).fill(RIGHT).is_not_blank().is_not_whitespace()
    trace.Households("Taken from cell B7 right")
        
    technology = cell.shift (0, -1).fill(RIGHT).is_not_blank().is_not_whitespace()
    trace.Technology("Taken from cell B6 right which is not blank")
    
    #installation may potentially become measure type. A word from DM is awaited.
    installation = cell.shift (0, -2).fill(RIGHT).is_not_blank().is_not_whitespace()
    trace.Installation("Taken from cell B5 right which is not blank")

    period = cell.shift(0, -4).fill(RIGHT).is_not_blank().is_not_whitespace()
    trace.Period("taken from cell B3 right which is not blank")

    #datamarker is catching weired values from footer so footer is caught and deleted
    observations = households.fill(DOWN).is_not_blank().is_not_whitespace()-footer

    dimensions = [
        HDim(local_or_parliamentary_code, "Local Or Parliamentary Code", CLOSEST, ABOVE),
        HDim(households, "Households", CLOSEST, LEFT),
        HDim(technology, "Technology", CLOSEST, LEFT),
        HDim(installation, "Installation", CLOSEST, LEFT),
        HDim(period, "Period", CLOSEST, LEFT)
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    savepreviewhtml(tidy_sheet,fname=tab.name + "Preview.html")
    trace.with_preview(tidy_sheet)
    trace.store("combined_dataframe", tidy_sheet.topandas())

# # changes in local authority code to be implemented in post processing
# # changes in local authority name to be implemented in post processing


# %%
for name, tab in tabs.items():
    if 'Title' in name or 'Calculation' in name     or 'Latest Quarter - Region' in name or 'Latest Quarter - Region (kW)' in name     or 'Latest Quarter - LA' in name or 'Latest Quarter - LA (KW)' in name     or 'Latest Quarter - PC' in name or 'Latest Quarter - PC (kW)' in name:
        continue
    print(tab.name)
    trace.start(datasetTitle, tab, columns, distribution.downloadURL)
        
    cell = tab.excel_ref("B7")
    
    footer = tab.filter(contains_string("Notes")).expand(RIGHT).expand(DOWN)
        
    local_enterprise_partnerships = cell.fill(DOWN).is_not_blank().is_not_whitespace()-footer
    trace.Local_Enterprise_Partnerships("Taken from cell B7 down excluding footer")

    leps_authority = cell.shift(1, 0).fill(DOWN).is_not_blank().is_not_whitespace()
    trace.Leps_Authority("Taken from cell C7 down")

    households = cell.shift(1, 0).fill(RIGHT).is_not_blank().is_not_whitespace()
    trace.Households("Taken from cell C7 right")
        
    technology = cell.shift (0, -1).fill(RIGHT).is_not_blank().is_not_whitespace()
    trace.Technology("Taken from cell B6 right which is not blank")

    #installation may potentially become measure type. A word from DM is awaited.
    installation = cell.shift (0, -2).fill(RIGHT).is_not_blank().is_not_whitespace()
    trace.Installation("Taken from cell B5 right which is not blank")

    period = cell.shift(0, -4).fill(RIGHT).is_not_blank().is_not_whitespace()
    trace.Period("taken from cell B3 right which is not blank")

    observations = leps_authority.fill(RIGHT).is_not_blank().is_not_whitespace()-footer

    dimensions = [
        HDim(local_enterprise_partnerships, "Local Enterprise Partnerships", CLOSEST, ABOVE),
        HDim(leps_authority, "Leps_Authority", CLOSEST, ABOVE),
        HDim(households, "Households", CLOSEST, LEFT),
        HDim(technology, "Technology", CLOSEST, LEFT),
        HDim(installation, "Installation", CLOSEST, LEFT),
        HDim(period, "Period", CLOSEST, LEFT)
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    savepreviewhtml(tidy_sheet,fname=tab.name + "Preview.html")
    trace.with_preview(tidy_sheet)
    trace.store("combined_dataframe", tidy_sheet.topandas())


# %%
df = trace.combine_and_trace(datasetTitle, "combined_dataframe")
df


# %%
df['DATAMARKER'].unique()


# %%
cubes.add_cube(scraper, df.drop_duplicates(), datasetTitle)
cubes.output_all()


# %%
trace.render("spec_v1.html")

