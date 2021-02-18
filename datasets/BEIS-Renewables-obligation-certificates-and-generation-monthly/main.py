#!/usr/bin/env python
# coding: utf-8
# +
from gssutils import *
import pandas as pd
import json

scraper = Scraper(seed="info.json")
scraper.distributions = [x for x in scraper.distributions if hasattr(x, "mediaType")]
scraper

#Add cubes class
cubes = Cubes("info.json")

#Add TransformTrace
trace = TransformTrace()
# -

# Extract latest distribution  of the required dataset and datasetTitle
distribution  = scraper.distribution(latest=True, title = lambda x:"Renewables obligation: certificates and generation (monthly)" in x)
datasetTitle = distribution.title
distribution

# Extract all the tabs and its content from the spread sheet 
tabs = distribution.as_databaker()

# List out all the tab names to cross verify with spread sheet
for tab in tabs:
    print(tab.name)

columns = ["Technology Group", "Generation Type", "Roc Per Mwh", "Period", "Qtr", "Month", "Element"]

# +
# Filtering the tabs which are required and start stage-1 transform
tabs_i_want = ["Financial Year", "Quarter", "FY-only sites", "Month"]

tabs = [x for x in tabs if x.name in tabs_i_want]
for tab in tabs:
    print(tab.name)
    
    trace.start(datasetTitle, tab, columns, distribution.downloadURL)
    cell = tab.excel_ref("A1")
    
    generation_type = cell.shift(1, 5).fill(DOWN).is_not_blank().is_not_whitespace()
    trace.Generation_Type("Defined from cell B6 below which is not blank")

    roc_per_mwh = cell.shift(2, 5).fill(DOWN).is_not_blank().is_not_whitespace()
    trace.Roc_Per_Mwh("Defined from cell C6 below which is not blank")
    
    if tab.name == "Quarter":
        qtr = cell.shift(2, 5).fill(RIGHT).is_not_blank().is_not_whitespace()
        trace.Qtr("Defined from cell D6 and right which is not blank")
        period = cell.shift(2, 4).fill(RIGHT).is_not_blank().is_not_whitespace()
        trace.Period("Defined from cell D5 and right which is not blank")
    elif tab.name == "Month":
        month = cell.shift(2, 5).fill(RIGHT).is_not_blank().is_not_whitespace()
        trace.Month("Defined from cell D6 and right which is not blank")
        period = cell.shift(2, 4).fill(RIGHT).is_not_blank().is_not_whitespace()
        trace.Period("Defined from cell D5 and right which is not blank")
    else:
        period = cell.shift(2, 5).fill(RIGHT).is_not_blank().is_not_whitespace()
        trace.Period("Defined from cell D6 and right which is not blank")

    element = tab.one_of(["Certificates", "Equivalent Generation"])
    trace.Element("Defined cell A7, A132, A257 and A275")

    techno_group = cell.shift(0, 5).fill(DOWN).is_not_blank().is_not_whitespace()-element
    
    technology_group = techno_group - tab.excel_ref("A").filter(contains_string("Summary Technology Group"))
    trace.Technology_Group("Defined from cell A8 which is not blank")
    
    observations = cell.shift(3, 6).expand(RIGHT).expand(DOWN).is_not_whitespace()
# ROCs and MWh needs to be removed from the observation which is getting caught in DATAMARKER.
# true_observations = observations.filter(lambda x: type(x.value) != "ROCs" not in x.value)

    if tab.name == "Quarter": 
    
        dimensions = [
            HDim(technology_group, "Technology Group", CLOSEST, ABOVE),
            HDim(generation_type, "Generation Type", CLOSEST, ABOVE),
            HDim(roc_per_mwh, "Roc Per Mwh", CLOSEST, ABOVE),
            HDim(period, "Period", CLOSEST, LEFT),
            HDim(element, "Element", CLOSEST, ABOVE),
            HDim(qtr, "Qtr", CLOSEST, LEFT)
        ]
        
    elif tab.name == "Month":
        
        dimensions = [
            HDim(technology_group, "Technology Group", CLOSEST, ABOVE),
            HDim(generation_type, "Generation Type", CLOSEST, ABOVE),
            HDim(roc_per_mwh, "Roc Per Mwh", CLOSEST, ABOVE),
            HDim(period, "Period", CLOSEST, LEFT),
            HDim(element, "Element", CLOSEST, ABOVE),
            HDim(month, "Month", CLOSEST, LEFT)
        ]
    else:
            
        dimensions = [
            HDim(technology_group, "Technology Group", CLOSEST, ABOVE),
            HDim(generation_type, "Generation Type", CLOSEST, ABOVE),
            HDim(roc_per_mwh, "Roc Per Mwh", CLOSEST, ABOVE),
            HDim(period, "Period", CLOSEST, LEFT),
            HDim(element, "Element", CLOSEST, ABOVE),

        ]
        
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
    trace.with_preview(tidy_sheet)
    trace.store("combined_dataframe", tidy_sheet.topandas())
# -

df = trace.combine_and_trace(datasetTitle, "combined_dataframe")
df

df["DATAMARKER"].unique()

df["Element"].unique()

cubes.add_cube(scraper, df.drop_duplicates(), datasetTitle)
cubes.output_all()

trace.render("spec_v1.html")
