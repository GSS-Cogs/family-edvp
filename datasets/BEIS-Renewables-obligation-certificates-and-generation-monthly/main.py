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
    
    remove = tab.filter(contains_string("Data are sourced")).expand(RIGHT).expand(DOWN)
    cell = tab.excel_ref("A1")
    
    generation_type = cell.shift(1, 5).fill(DOWN).is_not_blank().is_not_whitespace()
    trace.Generation_Type("Defined from cell B6 below which is not blank")

    roc_per_mwh = cell.shift(2, 5).fill(DOWN)-remove
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
    
    technology_group = techno_group - tab.excel_ref("A").filter(contains_string("Summary Technology Group")) - remove
    trace.Technology_Group("Defined from cell A8 which is not blank")
    
    observations = cell.shift(3, 6).expand(RIGHT).expand(DOWN).is_not_whitespace() - element.expand(RIGHT)

    if tab.name == "Quarter": 
    
        dimensions = [
            HDim(technology_group, "Technology Group", CLOSEST, ABOVE),
            HDim(generation_type, "Generation Type", CLOSEST, ABOVE),
            HDim(roc_per_mwh, "Roc Per Mwh", DIRECTLY, LEFT, cellvalueoverride = {'' : 'all'}),
            HDim(period, "Period", CLOSEST, LEFT),
            HDim(element, "Element", CLOSEST, ABOVE),
            HDim(qtr, "Qtr", CLOSEST, LEFT)
        ]
        
    elif tab.name == "Month":
        
        dimensions = [
            HDim(technology_group, "Technology Group", CLOSEST, ABOVE),
            HDim(generation_type, "Generation Type", CLOSEST, ABOVE),
            HDim(roc_per_mwh, "Roc Per Mwh", DIRECTLY, LEFT, cellvalueoverride = {'' : 'all'}),
            HDim(period, "Period", CLOSEST, LEFT),
            HDim(element, "Element", CLOSEST, ABOVE),
            HDim(month, "Month", CLOSEST, LEFT)
        ]
    else:
            
        dimensions = [
            HDim(technology_group, "Technology Group", CLOSEST, ABOVE),
            HDim(generation_type, "Generation Type", CLOSEST, ABOVE),
            HDim(roc_per_mwh, "Roc Per Mwh", DIRECTLY, LEFT, cellvalueoverride = {'' : 'all'}),
            HDim(period, "Period", CLOSEST, LEFT),
            HDim(element, "Element", CLOSEST, ABOVE),

        ]
        
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
    trace.with_preview(tidy_sheet)
    trace.store("combined_dataframe", tidy_sheet.topandas())
# -

df = trace.combine_and_trace(datasetTitle, "combined_dataframe").fillna("NaN")
df


def left(s, amount):
    return s[:amount]
def right(s, amount):
    return s[-amount:]


df['Period'] = df.apply(lambda x: 'quarter/' + left(x['Period'], 4) + '-Q' + left(x['Qtr'], 1) if 'NaN' not in x['Qtr'] else x['Period'], axis =1 )

df = df.replace({'Month' : {'September' : '09',
                            'October'   : '10',
                            'November'  : '11',
                            'December'  : '12',
                            'January'   : '01',
                            'February'  : '02',
                            'March'     : '03',
                            'April'     : '04',
                            'May'       : '05',
                            'June'      : '06',
                            'July'      : '07',
                            'August'    : '08',
                            'October p' : '10'},
                 'Technology Group' : {'Total' : 'All'}})

df['Period'] = df.apply(lambda x: 'month/' + left(x['Period'], 4) + '-' + x['Month'] if 'NaN' not in x['Month'] else x['Period'], axis =1 )

df['Period'] = df.apply(lambda x: 'financial-year/' + left(x['Period'], 4) if 'NaN' in x['Qtr'] and 'NaN' in x['Month'] else x['Period'], axis = 1)

df = df.drop(columns=['Qtr', 'Month'])

df = df.rename(columns={'OBS' : 'Value'})

df = df[['Period', 'Technology Group', 'Generation Type', 'Roc Per Mwh', 'Value', 'Element']]

COLUMNS_TO_NOT_PATHIFY = ['Period', 'Value', 'Roc Per Mwh']

for col in df.columns.values.tolist():
    if col in COLUMNS_TO_NOT_PATHIFY:
        continue
    try:
        df[col] = df[col].apply(pathify)
    except Exception as err:
        raise Exception('Failed to pathify column "{}".'.format(col)) from err

df

cubes.add_cube(scraper, df.drop_duplicates(), datasetTitle)
cubes.output_all()

trace.render("spec_v1.html")