#!/usr/bin/env python
# coding: utf-8

# In[60]:


from gssutils import *
import pandas as pd
import json

def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

def mid(s, offset, amount):
    return s[offset:offset+amount]

#extract spread sheet from landing page
scraper = Scraper(seed="info.json")
scraper.distributions = [x for x in scraper.distributions if hasattr(x, "mediaType")]
scraper

# Add cubes class
cubes = Cubes("info.json")
#Add tracer to transform
trace = TransformTrace()


# In[61]:


# extract latest distribution and datasetTitle
distribution = scraper.distribution(latest = True)
datasetTitle = distribution.title
print(distribution.downloadURL)
print(datasetTitle)


# In[62]:


# Extract all the tabs from the spread sheet
tabs = {tab.name: tab for tab in distribution.as_databaker()}


# In[63]:


# List out all the tab name to cross verify with the spread sheet
for tab in tabs:
    print(tab)


# In[64]:


columns = ["Region", "Region Name", "Period", "Technology", "Installation", "Households", "Local Or Parliamentary Code",
           "Local Enterprise Partnerships", "Leps Authority", "Marker", "Unit"]


# In[65]:


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

    technology = cell.shift(0, -1).fill(RIGHT)#.is_not_blank().is_not_whitespace()
    trace.Technology("Taken from cell B6 right which is not blank")
    remove = households.filter('Total').shift(UP)
    technology = technology - remove

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
        HDim(period, "Period", CLOSEST, LEFT),
        HDimConst('Tab', tab.name)
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    savepreviewhtml(tidy_sheet,fname=tab.name + "Preview.html")
    trace.with_preview(tidy_sheet)
    trace.store("combined_dataframe", tidy_sheet.topandas())


# In[66]:


for name, tab in tabs.items():
    if 'Title' in name or 'Calculation' in name     or 'Latest Quarter - Region' in name or 'Latest Quarter - Region (kW)' in name     or 'Latest Quarter - LEPs' in name or 'Latest Quarter - LEPs (kW)' in name:
        continue
    print(tab.name)
    trace.start(datasetTitle, tab, columns, distribution.downloadURL)
    cell = tab.excel_ref("B7")

# Datamarker is catching footer values from Latest Quarter - LA and Latest Quarter - LA (kW) tabs
    footer = tab.filter(contains_string("Notes")).expand(RIGHT).expand(DOWN)

    #datamarker is catching weired values from footer so footer is caught and deleted
    local_or_parliamentary_code = cell.fill(DOWN)-footer
    trace.Local_Or_Parliamentary_Code("Taken from cell B7 down excluding footer")

    regionName = local_or_parliamentary_code.shift(RIGHT)
    trace.Region_Name("Taken from cell B7 down excluding footer")

    households = cell.shift(1, 0).fill(RIGHT).is_not_blank().is_not_whitespace()
    trace.Households("Taken from cell B7 right")

    technology = cell.shift (0, -1).fill(RIGHT)#.is_not_blank().is_not_whitespace()
    trace.Technology("Taken from cell B6 right which is not blank")
    remove = households.filter('Total').shift(UP)
    technology = technology - remove

    #installation may potentially become measure type. A word from DM is awaited.
    installation = cell.shift (0, -2).fill(RIGHT).is_not_blank().is_not_whitespace()
    trace.Installation("Taken from cell B5 right which is not blank")

    period = cell.shift(0, -4).fill(RIGHT).is_not_blank().is_not_whitespace()
    trace.Period("taken from cell B3 right which is not blank")

    #datamarker is catching weired values from footer so footer is caught and deleted
    observations = households.fill(DOWN).is_not_blank().is_not_whitespace()-footer

    dimensions = [
        HDim(local_or_parliamentary_code, "Local Or Parliamentary Code", DIRECTLY, LEFT),
        HDim(regionName, "Region Name", DIRECTLY, LEFT),
        HDim(households, "Households", CLOSEST, LEFT),
        HDim(technology, "Technology", CLOSEST, LEFT),
        HDim(installation, "Installation", CLOSEST, LEFT),
        HDim(period, "Period", CLOSEST, LEFT),
        HDimConst('Tab', tab.name)
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    savepreviewhtml(tidy_sheet,fname=tab.name + "Preview.html")
    trace.with_preview(tidy_sheet)
    trace.store("combined_dataframe", tidy_sheet.topandas())

# # changes in local authority code to be implemented in post processing
# # changes in local authority name to be implemented in post processing


# In[67]:


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

    technology = cell.shift (0, -1).fill(RIGHT)#.is_not_blank().is_not_whitespace()
    trace.Technology("Taken from cell B6 right which is not blank")
    remove = households.filter('Total').shift(UP)
    technology = technology - remove

    #installation may potentially become measure type. A word from DM is awaited.
    installation = cell.shift (0, -2).fill(RIGHT).is_not_blank().is_not_whitespace()
    trace.Installation("Taken from cell B5 right which is not blank")

    period = cell.shift(0, -4).fill(RIGHT).is_not_blank().is_not_whitespace()
    trace.Period("taken from cell B3 right which is not blank")

    observations = leps_authority.fill(RIGHT).is_not_blank().is_not_whitespace()-footer

    if 'LEPs (kW)' in tab.name:
        dimensions = [
            HDim(local_enterprise_partnerships, "Local Enterprise Partnerships", CLOSEST, ABOVE),
            HDim(leps_authority, "Leps_Authority", CLOSEST, ABOVE),
            HDim(households, "Households", CLOSEST, LEFT),
            HDim(technology, "Technology", CLOSEST, LEFT),
            HDim(installation, "Installation", CLOSEST, LEFT, cellvalueoverride = {'Cumulative number of installations 2' : 'Cumulative installed capacity (kW) 2'}),
            HDim(period, "Period", CLOSEST, LEFT),
            HDimConst('Tab', tab.name)
        ]
    else:
        dimensions = [
            HDim(local_enterprise_partnerships, "Local Enterprise Partnerships", CLOSEST, ABOVE),
            HDim(leps_authority, "Leps_Authority", CLOSEST, ABOVE),
            HDim(households, "Households", CLOSEST, LEFT),
            HDim(technology, "Technology", CLOSEST, LEFT),
            HDim(installation, "Installation", CLOSEST, LEFT),
            HDim(period, "Period", CLOSEST, LEFT),
            HDimConst('Tab', tab.name)
        ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    savepreviewhtml(tidy_sheet,fname=tab.name + "Preview.html")
    trace.with_preview(tidy_sheet)
    trace.store("combined_dataframe", tidy_sheet.topandas())


# In[68]:


import numpy as np

def get_code(input, reference):
    ind = reference[reference['Name']==input]
    if ind['Code'].empty:
        pass
    else:
        return ind['Code'].iloc[0]

df = trace.combine_and_trace(datasetTitle, "combined_dataframe").fillna('')

indexNames = df[df['Households'] == 'Estimated number of households3' ].index
df.drop(indexNames, inplace = True)

df['Period'] = df.apply(lambda x: 'quarter/'+ left(x['Period'], 4) + '-Q1', axis =1) #need to change to include quarter values from tabs

df = df.rename(columns={'Technology' : 'Technology Type', 'Households' : 'Building Type', 'Installation' : 'Measure Type', 'OBS' : 'Value', 'DATAMARKER' : 'Marker'})

df['Technology Type'] = df.apply(lambda x: 'All' if x['Technology Type'] == '' else x['Technology Type'], axis = 1)

df = df.replace({'Building Type' : {'Total Non-Domestic' : 'Non-Domestic', 'Total Domestic' : 'Domestic'},
                 'Measure Type' : {'Cumulative number of installations 2' : 'cumulative installations',
                                   'Cumulative installed capacity (kW) 2' : 'cumulative installed capacity',
                                   'Cumulative installed capacity 2' : 'cumulative installed capacity',
                                   'Installations per 10,000 households': 'installations per 10000 households'},
                 'Region' :        {'East of England' : 'E12000006',
                                    'East Midlands' : 'E12000004',
                                    'London' : 'E12000007',
                                    'North East' : 'E12000001',
                                    'North West' : 'E12000002',
                                    'South East' : 'E12000008',
                                    'South West' : 'E12000009',
                                    'West Midlands' : 'E12000005',
                                    'Yorkshire and The Humber' : 'E12000003',
                                    'Total for England' : 'E92000001',
                                    'Wales' : 'W92000004',
                                    'Scotland' : 'S92000003',
                                    'Grand Total' : 'K03000001'}})
#Check that Grand Total is fine as Great Britain

df['Region'] = df.apply(lambda x: 'K03000001' if x['Region Name'] in ['Total', 'Grand Total'] else ('Unallocated' if 'Unallocated' in x['Region Name'] else x['Region']), axis = 1)

df['Area'] = df['Region'] + df['Local Or Parliamentary Code'] + df['Leps_Authority']

df = df.replace({'Area' : {'Stoke-on-trent' : 'Stoke-on-Trent'}})

regions = df[['Local Or Parliamentary Code', 'Region Name']]
dfLA = regions.copy()
dfLA['Region Name'].replace('', np.nan, inplace=True)
dfLA.dropna(subset=['Region Name'], inplace=True)
dfLA = dfLA.drop_duplicates()
dfLA = dfLA.rename(columns={'Local Or Parliamentary Code' : 'Code', 'Region Name' : 'Name'})

df['Area Code'] = df.apply(lambda x: get_code(x['Area'], dfLA), axis = 1)
df['Area Code'] = df.apply(lambda x: x['Area'] if x['Area Code'] is None else x['Area Code'], axis = 1)

df = df.replace({'Area Code' : {'Somerset West and Taunton Deane' : 'E07000246',
                                        'Kingston upon Hull, city of': 'E06000010'}})

df['Area Code'] = df.apply(lambda x: 'Unallocated' if 'Unallocated' in x['Region'] or 'Unallocated' in x['Region Name'] else x['Area Code'], axis = 1)

df['Unit'] = df.apply(lambda x: 'kilowatt' if 'capacity' in ['Measure Type'] else 'installation', axis = 1)

indexNames = df[ (df['Region'] == '') & (df['Region Name'] == '') & (df['Value'] == 0)].index
df.drop(indexNames, inplace = True)

df = df.drop(['Region'], axis=1)

df = df.rename(columns={'Area Code' : 'Region'})

indexNames = df[ df['Region'].isin(['K03000001', 'Unallocated']) ].index
df.drop(indexNames, inplace = True)

#I cant find anyway to accurately represent the unallocated values in the dataset, and therefore the "grand total" (all areas including unallocated)
#so I have removed them, this will not be an issue as this is currently being used for proof of concept, will need to be addressed at some point in the future

df = df[['Period', 'Region', 'Technology Type', 'Building Type', 'Value', 'Marker', 'Measure Type', 'Unit']]

COLUMNS_TO_NOT_PATHIFY = ['Period', 'Region', 'Value']

for col in df.columns.values.tolist():
	if col in COLUMNS_TO_NOT_PATHIFY:
		continue
	try:
		df[col] = df[col].apply(pathify)
	except Exception as err:
		raise Exception('Failed to pathify column "{}".'.format(col)) from err

df['Value'] = df['Value'].apply(lambda x: round(x, 2))
#having to round to 2 decimal places to fix some duplicate issues, should fix at later date but should be fine for proof of concept EDV stuff

df = df.drop_duplicates()

df


# In[69]:


cubes.add_cube(scraper, df.drop_duplicates(), datasetTitle)
cubes.output_all()
trace.render("spec_v1.html")


# In[70]:


from IPython.core.display import HTML
for col in df:
    if col not in ['Value']:
        df[col] = df[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(df[col].cat.categories)


# In[71]:




