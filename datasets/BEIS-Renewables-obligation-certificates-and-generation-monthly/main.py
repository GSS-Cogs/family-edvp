#!/usr/bin/env python
# coding: utf-8

# In[1]:


from gssutils import *
import pandas as pd
import json

scraper = Scraper(seed="info.json")
scraper.distributions = [x for x in scraper.distributions if hasattr(x, "mediaType")]
scraper


# In[2]:


# Extract latest distribution  of the required dataset and datasetTitle
distribution  = scraper.distribution(latest=True, title = lambda x:"Renewables obligation: certificates and generation (monthly - Excel)" in x)
datasetTitle = distribution.title
distribution


# In[3]:


# Extract all the tabs and its content from the spread sheet
tabs = distribution.as_databaker()

# List out all the tab names to cross verify with spread sheet
for tab in tabs:
    print(tab.name)

columns = ["Technology Group", "Generation Type", "Roc Per Mwh", "Period", "Qtr", "Month", "Element"]


# In[4]:


# Filtering the tabs which are required and start stage-1 transform
#tabs_i_want = ["Financial Year", "Quarter", "FY-only sites", "Month"]
tabs_i_want = ["FY-only sites", "Month"]
#all data in financial year and quarter tabs are taken from month tab

tabs = [x for x in tabs if x.name in tabs_i_want]

tidy_tabs = []

for tab in tabs:
    print(tab.name)

    remove = tab.filter(contains_string("Data are sourced")).expand(RIGHT).expand(DOWN)
    cell = tab.excel_ref("A1")

    generation_type = cell.shift(1, 5).fill(DOWN).is_not_blank().is_not_whitespace()

    roc_per_mwh = cell.shift(2, 5).fill(DOWN)-remove

    period = cell.shift(2, 5).fill(RIGHT).is_not_blank().is_not_whitespace()

    techno_group = cell.shift(0, 5).fill(DOWN).is_not_blank().is_not_whitespace()

    technology_group = techno_group - tab.excel_ref("A").filter(contains_string("Summary Technology Group")) - remove

    observations = cell.shift(3, 6).expand(RIGHT).expand(DOWN).is_not_whitespace() - tab.filter(contains_string("Equivalent generation")).expand(RIGHT).expand(DOWN)

    if tab.name == "Month":

        dimensions = [
            HDim(technology_group, "Technology Group", CLOSEST, ABOVE),
            HDim(generation_type, "Generation Type", CLOSEST, ABOVE),
            HDim(roc_per_mwh, "Roc Per Mwh", DIRECTLY, LEFT, cellvalueoverride = {'' : 'all'}),
            HDim(period, "Period", CLOSEST, LEFT),
            HDim(period, "Month", CLOSEST, LEFT)
        ]
    else:

        dimensions = [
            HDim(technology_group, "Technology Group", CLOSEST, ABOVE),
            HDim(generation_type, "Generation Type", CLOSEST, ABOVE),
            HDim(roc_per_mwh, "Roc Per Mwh", DIRECTLY, LEFT, cellvalueoverride = {'' : 'all'}),
            HDim(period, "Period", CLOSEST, LEFT)

        ]

    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
    tidy_tabs.append(tidy_sheet.topandas())


# In[5]:


df = pd.concat(tidy_tabs).fillna("NaN")

def left(s, amount):
    return s[:amount]
def right(s, amount):
    return s[-amount:]

df.to_csv('test.csv', index=False)

df


# In[6]:



#df['Period'] = df.apply(lambda x: 'quarter/' + left(x['Period'], 4) + '-Q' + left(x['Qtr'], 1) if 'NaN' not in x['Qtr'] else x['Period'], axis =1 )
df['Month'] = df.apply(lambda x : x['Month'][5:] if x['Month'][:1] == '2' else x['Month'], axis = 1)


df = df.replace({'Month' : {'September'  : '09',
                            ' September'  : '09',
                            'October'    : '10',
                            'November'   : '11',
                            'December'   : '12',
                            'January'    : '01',
                            'February'   : '02',
                            'March'      : '03',
                            'April'      : '04',
                            'May'        : '05',
                            'June'       : '06',
                            'July'       : '07',
                            'August'     : '08'},
                 'Technology Group' : {'Total' : 'All'}})

indexNames = df[ df['Roc Per Mwh'] == 'ROCs per MWh' ].index
df.drop(indexNames, inplace = True)

df['Period'] = df.apply(lambda x: 'month/' + left(x['Period'], 4) + '-' + x['Month'] if 'NaN' not in x['Month'] else x['Period'], axis =1 )

df['Period'] = df.apply(lambda x: 'government-year/' + left(x['Period'], 4) if 'NaN' in x['Month'] else x['Period'], axis = 1)

df['Roc Per Mwh'] = df.apply(lambda x: round(float(x['Roc Per Mwh']), 2) if 'all' not in x['Roc Per Mwh'] else x['Roc Per Mwh'], axis = 1)

df = df.rename(columns={'OBS' : 'Value'})

df = df[['Period', 'Technology Group', 'Generation Type', 'Roc Per Mwh', 'Value']]

df['Value'] = df.apply(lambda x: int(x['Value']) if '.' in str(x['Value']) else x['Value'], axis = 1)

df


# In[7]:


scraper.dataset.title = 'Renewables obligation: certificates and generation'
scraper.dataset.comment = 'Data on the UK’s renewables sector. This data relates to certificates and generation associated with the renewables obligation scheme. Published monthly on the second Thursday of each month.'

df.to_csv('observations.csv', index=False)

catalog_metadata = scraper.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')


# In[8]:


from IPython.core.display import HTML
for col in df:
    if col not in ['Value']:
        df[col] = df[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(df[col].cat.categories)

