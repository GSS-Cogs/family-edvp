#!/usr/bin/env python
# coding: utf-8

# In[67]:


from gssutils import *
import json
import re
from datetime import datetime
import copy
import glob
import os
import numpy as np

def cellCont(cell):
    return re.findall(r"'([^']*)'", str(cell))[0]

def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month

def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


# In[68]:


scraper = Scraper(seed="rhi-deployment-data-capacity-mw-info.json")
scraper


# In[69]:


dist = [x for x in scraper.distributions if "Excel" in x.title][0]
dist


# In[70]:


unneeded_tabs = ['Title', 'Contents', 'Key Statistics', 'Glossary', 'Scheme background',
                 '1.5', 'S1.1', 'S1.2', 'S1.3', '2.5', '2.6', 'S2.1', 'S2.2',
                 'S2.3', 'S2.4', 'S2.5', 'S2.6', 'S2.7']

tabs = { tab: tab for tab in dist.as_databaker() if tab.name not in unneeded_tabs }

for i in tabs:
    print(i.name)


# In[71]:


out = Path('previews')
out.mkdir(exist_ok=True)

tidied_sheets = {}

for tab in tabs:

    if tab.name in ['1.1', '1.2', '1.3']:

        print(tab.name)

        pivot = tab.filter(contains_string(tab.name))

        if tab.name == '1.2':
            remove = tab.filter('Source:').expand(RIGHT).expand(DOWN)
        else:
            remove = tab.filter('Notes:').expand(RIGHT).expand(DOWN)

        period = cellCont(pivot).split(',')[-1:][0].strip()

        period_start = period.split(' ')[1] + '-' + period.split(' ')[0]
        period_end = period.split(' ')[4] + '-' + period.split(' ')[3]

        if tab.name != '1.3':
            geography = cellCont(pivot).split(',')[-2:][0].strip()
        if tab.name == '1.2':
            application_status = pivot.shift(0, 3).fill(DOWN) - remove
        elif tab.name == '1.3':
            geography = pivot.shift(1, 3).fill(DOWN).is_not_blank().shift(LEFT) - remove
        else:
            technology_type = pivot.shift(0, 3).fill(DOWN) - remove

        application_type = pivot.shift(1, 2).expand(RIGHT).is_not_blank()

        measure_type = application_type.shift(DOWN)

        if tab.name == '1.2':
            observations = application_status.fill(RIGHT).is_not_blank() - tab.filter(contains_string('%')).expand(DOWN)
        elif tab.name == '1.3':
            observations = geography.shift(RIGHT).fill(RIGHT).is_not_blank() - tab.filter(contains_string('%')).expand(DOWN) - tab.filter(contains_string('Total')).fill(RIGHT)
        else:
            observations = technology_type.fill(RIGHT).is_not_blank() - tab.filter(contains_string('%')).expand(DOWN) - tab.filter(contains_string('Total')).fill(RIGHT)

        if tab.name == '1.2':
            dimensions = [
                HDimConst('Geography', geography),
                HDimConst('Period Start', period_start),
                HDimConst('Period End', period_end),
                HDim(application_status, 'Application Status', DIRECTLY, LEFT),
                HDimConst('SIC', 'total'),
                HDimConst('Technology Type', 'total'),
                HDim(application_type, 'Application Type', DIRECTLY, ABOVE),
                HDim(measure_type, 'Measure Type', DIRECTLY, ABOVE)
                ]
        elif tab.name == '1.3':
            dimensions = [
                HDim(geography, 'Geography', DIRECTLY, LEFT),
                HDimConst('Period Start', period_start),
                HDimConst('Period End', period_end),
                HDimConst('Application Status', 'all'),
                HDimConst('SIC', 'total'),
                HDimConst('Technology Type', 'total'),
                HDim(application_type, 'Application Type', DIRECTLY, ABOVE),
                HDim(measure_type, 'Measure Type', DIRECTLY, ABOVE)
                ]
        else:
            dimensions = [
                HDimConst('Geography', geography),
                HDimConst('Period Start', period_start),
                HDimConst('Period End', period_end),
                HDimConst('Application Status', 'all'),
                HDimConst('SIC', 'total'),
                HDim(technology_type, 'Technology Type', DIRECTLY, LEFT),
                HDim(application_type, 'Application Type', DIRECTLY, ABOVE),
                HDim(measure_type, 'Measure Type', DIRECTLY, ABOVE)
                ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        tidied_sheet = tidy_sheet.topandas()
        savepreviewhtml(tidy_sheet, fname=out / f'{tab.name} Preview.html')

        tidied_sheets[tab.name] = tidied_sheet

    elif tab.name in ['1.4']:

        pivot = tab.filter(contains_string(tab.name))

        remove = tab.filter('Notes:').expand(RIGHT).expand(DOWN)

        period = cellCont(pivot).split(',')[-1:][0].strip()

        period_start = period.split(' ')[1] + '-' + period.split(' ')[0]
        period_end = period.split(' ')[4] + '-' + period.split(' ')[3]

        geography = pivot.shift(0, 2).fill(DOWN) - remove

        application_type = pivot.shift(4, 2).expand(RIGHT).is_not_blank()

        observations = geography.shift(3, 0).fill(RIGHT).is_not_blank() - tab.filter(contains_string('Total')).fill(RIGHT)

        dimensions = [
                HDim(geography, 'Geography', DIRECTLY, LEFT),
                HDimConst('Period Start', period_start),
                HDimConst('Period End', period_end),
                HDimConst('Application Status', 'all'),
                HDimConst('SIC', 'total'),
                HDimConst('Technology Type', 'total'),
                HDim(application_type, 'Application Type', DIRECTLY, ABOVE)
                ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        tidied_sheet = tidy_sheet.topandas()
        savepreviewhtml(tidy_sheet, fname=out / f'{tab.name} Preview.html')

        tidied_sheets[tab.name] = tidied_sheet

    elif tab.name in ['1.6']:

        pivot = tab.filter(contains_string(tab.name))

        remove = tab.filter('Notes:').expand(RIGHT).expand(DOWN)

        period = cellCont(pivot).split(',')[-1:][0].split('-')[-1:][0]

        geography = cellCont(pivot).split(',')[-2:][0].strip()

        technology_type = pivot.shift(0, 5).fill(DOWN).is_not_blank() - remove

        application_type = pivot.shift(1, 5).expand(RIGHT).is_not_blank()

        measure_type = application_type.shift(DOWN)

        observations = technology_type.fill(RIGHT).is_not_blank() - tab.filter(contains_string('%')).expand(DOWN) - tab.filter(contains_string('Total')).fill(RIGHT)

        dimensions = [
                HDimConst('Geography', geography),
                HDimConst('Period', period),
                HDimConst('Application Status', 'all'),
                HDimConst('SIC', 'total'),
                HDim(technology_type, 'Technology Type', DIRECTLY, LEFT),
                HDim(application_type, 'Application Type', DIRECTLY, ABOVE),
                HDim(measure_type, 'Measure Type', DIRECTLY, ABOVE)
                ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        tidied_sheet = tidy_sheet.topandas()
        savepreviewhtml(tidy_sheet, fname=out / f'{tab.name} Preview.html')

        tidied_sheets[tab.name] = tidied_sheet

    elif tab.name in ['1.7']:

        pivot = tab.filter(contains_string(tab.name))

        remove = tab.filter('Notes:').expand(RIGHT).expand(DOWN)

        period = cellCont(pivot).split(',')[-1:][0].strip()

        period_start = period.split(' ')[1] + '-' + period.split(' ')[0]
        period_end = period.split(' ')[4] + '-' + period.split(' ')[3]

        geography = cellCont(pivot).split(',')[-2:][0].strip()

        SIC = pivot.shift(0, 2).fill(DOWN).is_not_blank() - remove

        application_type = pivot.shift(2, 2).expand(RIGHT).is_not_blank()

        measure_type = application_type.shift(DOWN)

        observations = SIC.shift(RIGHT).fill(RIGHT).is_not_blank() - tab.filter(contains_string('%')).expand(DOWN) - tab.filter(contains_string('Total')).fill(RIGHT)

        dimensions = [
                HDimConst('Geography', 'Great Britain'),
                HDimConst('Period Start', period_start),
                HDimConst('Period End', period_end),
                HDimConst('Application Status', 'all'),
                HDimConst('Technology Type', 'total'),
                HDim(SIC, 'SIC', DIRECTLY, LEFT),
                HDim(application_type, 'Application Type', DIRECTLY, ABOVE),
                HDim(measure_type, 'Measure Type', DIRECTLY, ABOVE)
                ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        tidied_sheet = tidy_sheet.topandas()
        savepreviewhtml(tidy_sheet, fname=out / f'{tab.name} Preview.html')

        tidied_sheets[tab.name] = tidied_sheet

    elif tab.name in ['M1.1', 'M1.2', 'M1.3', 'M1.4', 'Q1.1', 'M2.1']:

        if tab.name in ['M1.4']:
            pivot = tab.filter(contains_string(tab.name + 'a'))
        else:
            pivot = tab.filter(contains_string(tab.name))

        remove = tab.filter(contains_string('Note')).expand(RIGHT).expand(DOWN)

        period_year = pivot.shift(0, 3).expand(DOWN).is_not_blank() - remove

        period_month = pivot.shift(1, 3).expand(DOWN) - remove

        period_total = cellCont(pivot).split(',')[-1:][0].strip()

        period_start = period_total.split(' ')[1] + '-' + period_total.split(' ')[0]
        period_end = period_total.split(' ')[4] + '-' + period_total.split(' ')[3]

        geography = cellCont(pivot).split(',')[-2:][0].strip()

        if tab.name in ['M1.2', 'M1.3', 'M1.4']:
            technology_type = pivot.shift(3, 2).expand(RIGHT).is_not_blank()
        else:
            application_type = pivot.shift(3, 2).expand(RIGHT).is_not_blank()

        if tab.name in ['M1.2']:
            application_type = 'Number of full applications (by date of first submission)'
        elif tab.name in ['M1.3']:
            application_type = 'Capacity of full applications (MW) (by date of first submission)'
        elif tab.name in ['M1.4']:
            application_type = pivot.expand(RIGHT).is_not_blank()

        if tab.name in ['M1.4']:
            observations = technology_type.fill(DOWN).is_not_blank() - remove - tab.filter(contains_string('Total')).fill(RIGHT) - tab.filter(contains_string('Total')).fill(RIGHT)
        elif tab.name in ['M2.1']:
            observations = period_month.shift(RIGHT).fill(RIGHT).is_not_blank() - tab.filter(contains_string('Cumulative')).expand(DOWN) - tab.filter(contains_string('Total')).fill(RIGHT)
        elif tab.name in ['M1.2']:
            observations = period_month.shift(RIGHT).fill(RIGHT).is_not_blank() - tab.filter(contains_string('Cumulative')).expand(DOWN) - tab.filter(contains_string('Total')).fill(DOWN) - tab.filter(contains_string('Total')).fill(RIGHT)
        else:
            observations = period_month.shift(RIGHT).fill(RIGHT).is_not_blank() - tab.filter(contains_string('Total')).fill(RIGHT) - tab.filter(contains_string('Total')).fill(RIGHT)

        if tab.name in ['M1.2', 'M1.3']:
            dimensions = [
                    HDimConst('Geography', 'Great Britain'),
                    HDim(period_year, 'Period Year', CLOSEST, ABOVE),
                    HDim(period_month, 'Period Month', DIRECTLY, LEFT),
                    HDimConst('Period Start', period_start),
                    HDimConst('Period End', period_end),
                    HDimConst('Application Status', 'all'),
                    HDim(technology_type, 'Technology Type', DIRECTLY, ABOVE),
                    HDimConst('SIC', 'total'),
                    HDimConst('Application Type', application_type)
                    ]
        elif tab.name in ['M1.4']:
            dimensions = [
                    HDimConst('Geography', 'Great Britain'),
                    HDim(period_year, 'Period Year', CLOSEST, ABOVE),
                    HDim(period_month, 'Period Month', DIRECTLY, LEFT),
                    HDimConst('Period Start', period_start),
                    HDimConst('Period End', period_end),
                    HDimConst('Application Status', 'all'),
                    HDim(technology_type, 'Technology Type', DIRECTLY, ABOVE),
                    HDimConst('SIC', 'total'),
                    HDim(application_type, 'Application Type', CLOSEST, LEFT)
                    ]
        else:
            dimensions = [
                    HDimConst('Geography', 'Great Britain'),
                    HDim(period_year, 'Period Year', CLOSEST, ABOVE),
                    HDim(period_month, 'Period Month', DIRECTLY, LEFT),
                    HDimConst('Period Start', period_start),
                    HDimConst('Period End', period_end),
                    HDimConst('Application Status', 'all'),
                    HDimConst('Technology Type', 'total'),
                    HDimConst('SIC', 'total'),
                    HDim(application_type, 'Application Type', DIRECTLY, ABOVE)
                    ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        tidied_sheet = tidy_sheet.topandas()
        savepreviewhtml(tidy_sheet, fname=out / f'{tab.name} Preview.html')

        tidied_sheets[tab.name] = tidied_sheet

    elif tab.name in ['2.1']:

        pivot = tab.filter(contains_string(tab.name))

        period = cellCont(pivot).split(',')[-1:][0].split('-')[-1:][0].strip()

        period_start = period.split(' ')[1] + '-' + period.split(' ')[0]
        period_end = period.split(' ')[4] + '-' + period.split(' ')[3]

        remove = tab.filter(contains_string('method')).expand(RIGHT).expand(DOWN)

        application_type = tab.filter('Technology').fill(RIGHT).is_not_blank()

        measure_type = application_type.shift(DOWN)

        observations = application_type.shift(DOWN).fill(DOWN).is_not_blank() - tab.filter(contains_string('%')).expand(DOWN) - tab.filter(contains_string('MW')).expand(DOWN) - remove - measure_type - application_type - tab.filter(contains_string('Total')).fill(RIGHT)

        technology_type = observations.fill(LEFT).is_not_blank() - observations - tab.filter(contains_string('%')).expand(DOWN)

        installation = application_type.shift(-1, -1).is_not_blank()

        dimensions = [
                HDimConst('Period Start', period_start),
                HDimConst('Period End', period_end),
                HDim(application_type, 'Application Type', DIRECTLY, ABOVE),
                HDim(measure_type, 'Measure Type', DIRECTLY, ABOVE),
                HDim(technology_type, 'Technology Type', DIRECTLY, LEFT),
                HDim(installation, 'Installation', CLOSEST, ABOVE),
                HDimConst('Application Status', 'all'),
                HDimConst('Geography', 'Great Britain')
                ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        tidied_sheet = tidy_sheet.topandas()
        savepreviewhtml(tidy_sheet, fname=out / f'{tab.name} Preview.html')

        tidied_sheets[tab.name] = tidied_sheet

    elif tab.name in ['2.2']:

        pivot = tab.filter(contains_string(tab.name + ' - '))

        remove = tab.filter('Notes:').expand(RIGHT).expand(DOWN)

        period = cellCont(pivot).split(',')[-1:][0].split('-')[-1:][0].strip()

        period_start = period.split(' ')[1] + '-' + period.split(' ')[0]
        period_end = period.split(' ')[4] + '-' + period.split(' ')[3]

        remove = tab.filter(contains_string('method')).expand(RIGHT).expand(DOWN)

        application_status = pivot.shift(2, 3).expand(RIGHT)

        technology_type = pivot.shift(0, 3).fill(DOWN).is_not_blank() - remove

        measure_type = technology_type.shift(RIGHT)

        observations = technology_type.shift(RIGHT).fill(RIGHT).is_not_blank() - tab.filter(contains_string('Total')).fill(RIGHT)

        dimensions = [
                HDimConst('Period Start', period_start),
                HDimConst('Period End', period_end),
                HDimConst('Application Type', 'all'),
                HDim(measure_type, 'Measure Type', DIRECTLY, LEFT),
                HDim(technology_type, 'Technology Type', CLOSEST, ABOVE),
                HDim(application_status, 'Application Status', DIRECTLY, ABOVE),
                HDimConst('Geography', 'Great Britain')
                ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        tidied_sheet = tidy_sheet.topandas()
        savepreviewhtml(tidy_sheet, fname=out / f'{tab.name} Preview.html')

        tidied_sheets[tab.name] = tidied_sheet

    elif tab.name in ['2.3']:

        pivot = tab.filter(contains_string(tab.name))

        remove = tab.filter(contains_string('Source:')).expand(RIGHT).expand(DOWN)

        period = cellCont(pivot).split(',')[-1:][0].split('-')[-1:][0].strip()

        period_start = period.split(' ')[1] + '-' + period.split(' ')[0]
        period_end = period.split(' ')[4] + '-' + period.split(' ')[3]

        remove = tab.filter(contains_string('method')).expand(RIGHT).expand(DOWN)

        geography = pivot.shift(1, 3).fill(DOWN).is_not_blank().shift(LEFT) - remove

        technology_type = pivot.shift(2, 2).expand(RIGHT).is_not_blank()

        measure_type = technology_type.shift(0, 2).expand(RIGHT)

        application_type = measure_type.shift(UP)

        observations = geography.shift(RIGHT).fill(RIGHT).is_not_blank() - tab.filter(contains_string('%')).expand(DOWN) - tab.filter(contains_string('Total')).fill(RIGHT)

        dimensions = [
                HDimConst('Period Start', period_start),
                HDimConst('Period End', period_end),
                HDim(application_type, 'Application Type', DIRECTLY, ABOVE),
                HDim(measure_type, 'Measure Type', DIRECTLY, ABOVE),
                HDim(technology_type, 'Technology Type', CLOSEST, LEFT),
                HDimConst('Application Status', 'all'),
                HDim(geography, 'Geography', DIRECTLY, LEFT, cellvalueoverride={'' : 'Great Britain'})
                ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        tidied_sheet = tidy_sheet.topandas()
        savepreviewhtml(tidy_sheet, fname=out / f'{tab.name} Preview.html')

        tidied_sheets[tab.name] = tidied_sheet

    elif tab.name in ['2.4']:

        pivot = tab.filter(contains_string(tab.name))

        remove = tab.filter(contains_string('Notes:')).expand(RIGHT).expand(DOWN)

        period = cellCont(pivot).split(',')[-1:][0].split('-')[-1:][0].strip()

        period_start = period.split(' ')[1] + '-' + period.split(' ')[0]
        period_end = period.split(' ')[4] + '-' + period.split(' ')[3]

        remove = tab.filter(contains_string('method')).expand(RIGHT).expand(DOWN)

        geography = tab.filter('Area Codes').fill(DOWN).is_not_blank() - remove

        observations = tab.filter(contains_string('accredited installations')).fill(DOWN).is_not_blank()

        dimensions = [
                HDimConst('Period Start', period_start),
                HDimConst('Period End', period_end),
                HDimConst('Application Type', 'Number of accredited installations'),
                HDimConst('Measure Type', 'applications'),
                HDimConst('Technology Type', 'total'),
                HDimConst('Application Status', 'all'),
                HDim(geography, 'Geography', DIRECTLY, LEFT)
                ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        tidied_sheet = tidy_sheet.topandas()
        savepreviewhtml(tidy_sheet, fname=out / f'{tab.name} Preview.html')

        tidied_sheets[tab.name] = tidied_sheet

    elif tab.name in ['M2.2', 'Q2.2']:

        pivot = tab.filter(contains_string(tab.name))

        remove = tab.filter(contains_string('Note')).expand(RIGHT).expand(DOWN)

        period_year = pivot.shift(0, 4).expand(DOWN).is_not_blank() - remove

        period_month = pivot.shift(1, 4).expand(DOWN) - remove

        period_total = cellCont(pivot).split(',')[-1:][0].strip()

        period_start = period_total.split(' ')[1] + '-' + period_total.split(' ')[0]
        period_end = period_total.split(' ')[4] + '-' + period_total.split(' ')[3]

        geography = cellCont(pivot).split(',')[-2:][0].strip()

        application_type = pivot.shift(3, 2).expand(RIGHT).is_not_blank()

        technology_type = pivot.shift(3, 3).expand(RIGHT).is_not_blank()

        observations = period_month.shift(RIGHT).fill(RIGHT).is_not_blank() - tab.filter(contains_string('Total')).fill(RIGHT)

        dimensions = [
                HDimConst('Geography', 'Great Britain'),
                HDim(period_year, 'Period Year', CLOSEST, ABOVE),
                HDim(period_month, 'Period Month', DIRECTLY, LEFT),
                HDimConst('Period Start', period_start),
                HDimConst('Period End', period_end),
                HDimConst('Application Status', 'all'),
                HDim(technology_type, 'Technology Type', DIRECTLY, ABOVE),
                HDim(application_type, 'Application Type', CLOSEST, LEFT)
                ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        tidied_sheet = tidy_sheet.topandas()
        savepreviewhtml(tidy_sheet, fname=out / f'{tab.name} Preview.html')

        tidied_sheets[tab.name] = tidied_sheet

    elif tab.name in ['Q2.1']:

        pivot = tab.filter(contains_string(tab.name))

        remove = tab.filter(contains_string('Note')).expand(RIGHT).expand(DOWN)

        period_year = pivot.shift(0, 3).expand(DOWN).is_not_blank() - remove

        period_month = pivot.shift(1, 3).expand(DOWN) - remove

        period_total = cellCont(pivot).split(',')[-1:][0].strip()

        period_start = period_total.split(' ')[1] + '-' + period_total.split(' ')[0]
        period_end = period_total.split(' ')[4] + '-' + period_total.split(' ')[3]

        geography = cellCont(pivot).split(',')[-2:][0].strip()

        application_type = pivot.shift(3, 2).expand(RIGHT).is_not_blank()

        observations = period_month.shift(RIGHT).fill(RIGHT).is_not_blank() - tab.filter(contains_string('Cumulative')).expand(DOWN) - tab.filter(contains_string('Total')).fill(RIGHT)

        dimensions = [
                HDimConst('Geography', 'Great Britain'),
                HDim(period_year, 'Period Year', CLOSEST, ABOVE),
                HDim(period_month, 'Period Month', DIRECTLY, LEFT),
                HDimConst('Period Start', period_start),
                HDimConst('Period End', period_end),
                HDimConst('Application Status', 'all'),
                HDimConst('Technology Type', 'all'),
                HDim(application_type, 'Application Type', DIRECTLY, ABOVE)
                ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        tidied_sheet = tidy_sheet.topandas()
        savepreviewhtml(tidy_sheet, fname=out / f'{tab.name} Preview.html')

        tidied_sheets[tab.name] = tidied_sheet


tidied_sheet


# In[72]:


formatted_sheets = {}


# In[73]:


try:
    df = tidied_sheets['1.1']

    df = df.replace({'Measure Type' : {'Number' : 'applications',
                                       'MW' : 'mw',
                                       'Capacity' : 'mw'}})

    df['Period Start'] = df['Period Start'].str.replace('November' , '11')
    df['Period Start'] = df.apply(lambda x: datetime.strptime(x['Period Start'], '%Y-%m'), axis = 1)
    df['Period End'] = df['Period End'].str.replace('March' , '03')
    df['Period End'] = df.apply(lambda x: datetime.strptime(x['Period End'], '%Y-%m'), axis = 1)

    df['Period'] = df.apply(lambda x: 'gregorian-interval/' + str(x['Period Start'])[:10] + 'T00:00:00/P' + str(diff_month(x['Period End'], x['Period Start'])) + 'M', axis = 1)

    df = df.drop(columns=['Period Start', 'Period End'])

    df = df.rename(columns={'OBS' : 'Value', 'DATAMARKER' : 'Marker'})

    indexNames = df[ df['Marker'].fillna('').str.contains('N/A')].index
    df.drop(indexNames, inplace = True)

    if len(df['Marker'].unique().tolist()) == 1:
        df = df.drop(columns=['Marker'])
        df = df[['Period', 'Geography', 'Technology Type', 'Application Type', 'Application Status', 'SIC', 'Value', 'Measure Type']]
    else:
        df = df[['Period', 'Geography', 'Technology Type', 'Application Type', 'Application Status', 'SIC', 'Value', 'Marker', 'Measure Type']]

    formatted_sheets['1.1'] = df

except Exception as err:
    raise Exception('Above Error found in Tab 1.1') from err

df


# In[74]:


try:
    df = tidied_sheets['1.2']

    df = df.replace({'Measure Type' : {'Number' : 'applications'}})

    df['Period Start'] = df['Period Start'].str.replace('November' , '11')
    df['Period Start'] = df.apply(lambda x: datetime.strptime(x['Period Start'], '%Y-%m'), axis = 1)
    df['Period End'] = df['Period End'].str.replace('March' , '03')
    df['Period End'] = df.apply(lambda x: datetime.strptime(x['Period End'], '%Y-%m'), axis = 1)

    df['Period'] = df.apply(lambda x: 'gregorian-interval/' + str(x['Period Start'])[:10] + 'T00:00:00/P' + str(diff_month(x['Period End'], x['Period Start'])) + 'M', axis = 1)

    df = df.drop(columns=['Period Start', 'Period End'])

    df = df.rename(columns={'OBS' : 'Value', 'DATAMARKER' : 'Marker'})

    indexNames = df[ df['Marker'].fillna('').str.contains('N/A')].index
    df.drop(indexNames, inplace = True)

    df['Value'] = df.apply(lambda x: '0' if '-' in str(x['Marker']) else x['Value'], axis = 1)
    df['Marker'] = df.apply(lambda x: None if '-' in str(x['Marker']) else x['Marker'], axis = 1)

    # All of the other '-' values on the sheet are 0, for some reason this is the only one which has the string '-' instead
    # This is assumed to be a mistake, the total values line up with this assumption

    if len(df['Marker'].unique().tolist()) == 1:
        df = df.drop(columns=['Marker'])
        df = df[['Period', 'Geography', 'Technology Type', 'Application Type', 'Application Status', 'SIC', 'Value', 'Measure Type']]
    else:
        df = df[['Period', 'Geography', 'Technology Type', 'Application Type', 'Application Status', 'SIC', 'Value', 'Marker', 'Measure Type']]

    formatted_sheets['1.2'] = df

except Exception as err:
    raise Exception('Above Error found in Tab 1.2') from err

df


# In[75]:


try:
    df = tidied_sheets['1.3']

    df = df.replace({'Measure Type' : {'Number' : 'applications',
                                       'MW' : 'mw'}})

    df['Period Start'] = df['Period Start'].str.replace('November' , '11')
    df['Period Start'] = df.apply(lambda x: datetime.strptime(x['Period Start'], '%Y-%m'), axis = 1)
    df['Period End'] = df['Period End'].str.replace('March' , '03')
    df['Period End'] = df.apply(lambda x: datetime.strptime(x['Period End'], '%Y-%m'), axis = 1)

    df['Period'] = df.apply(lambda x: 'gregorian-interval/' + str(x['Period Start'])[:10] + 'T00:00:00/P' + str(diff_month(x['Period End'], x['Period Start'])) + 'M', axis = 1)

    df['Geography'] = df['Geography'].replace('','Great Britain')

    df = df.drop(columns=['Period Start', 'Period End'])

    df = df.rename(columns={'OBS' : 'Value'})

    df['Value'] = df.apply(lambda x: str(int(x['Value'])) if 'Capacity' not in x['Application Type'] else x['Value'], axis = 1)

    df = df[['Period', 'Geography', 'Technology Type', 'Application Type', 'Application Status', 'SIC', 'Value', 'Measure Type']]

    formatted_sheets['1.3'] = df

except Exception as err:
    raise Exception('Above Error found in Tab 1.3') from err

df


# In[76]:


try:
    df = tidied_sheets['1.4']

    df['Measure Type'] = df.apply(lambda x: 'applications' if 'MW' not in x['Application Type'] else 'mw', axis = 1)

    df['Period Start'] = df['Period Start'].str.replace('November' , '11')
    df['Period Start'] = df.apply(lambda x: datetime.strptime(x['Period Start'], '%Y-%m'), axis = 1)
    df['Period End'] = df['Period End'].str.replace('March' , '03')
    df['Period End'] = df.apply(lambda x: datetime.strptime(x['Period End'], '%Y-%m'), axis = 1)

    df['Period'] = df.apply(lambda x: 'gregorian-interval/' + str(x['Period Start'])[:10] + 'T00:00:00/P' + str(diff_month(x['Period End'], x['Period Start'])) + 'M', axis = 1)

    df = df.drop(columns=['Period Start', 'Period End'])

    df = df.rename(columns={'OBS' : 'Value', 'DATAMARKER' : 'Marker'})

    df = df.replace({'Marker' : {'#' : 'suppressed',
                                 '^' : 'suppressed'}})

    df = df[['Period', 'Geography', 'Technology Type', 'Application Type', 'Application Status', 'SIC', 'Value', 'Measure Type', 'Marker']]

    formatted_sheets['1.4'] = df

except Exception as err:
    raise Exception('Above Error found in Tab 1.4') from err

df


# In[77]:


try:
    df = tidied_sheets['1.6']

    df = df.replace({'Measure Type' : {'Number' : 'applications',
                                       'Capacity' : 'mw'}})

    df['Period'] = df.apply(lambda x: 'gregorian-instant/' + str(datetime.strptime(pathify(x['Period'].replace('March' , '03')), '%m-%Y'))[:10], axis = 1)

    df = df.rename(columns={'OBS' : 'Value', 'DATAMARKER' : 'Marker'})

    indexNames = df[ df['Marker'].fillna('').str.contains('N/A')].index
    df.drop(indexNames, inplace = True)

    df = df[['Period', 'Geography', 'Technology Type', 'Application Type', 'Application Status', 'SIC', 'Value', 'Measure Type', 'Marker']]

    formatted_sheets['1.6'] = df

except Exception as err:
    raise Exception('Above Error found in Tab 1.6') from err

df


# In[78]:


try:
    df = tidied_sheets['1.7']

    df = df.replace({'Measure Type' : {'Number' : 'applications',
                                       'MW' : 'mw'}})

    df['Period Start'] = df['Period Start'].str.replace('November' , '11')
    df['Period Start'] = df.apply(lambda x: datetime.strptime(x['Period Start'], '%Y-%m'), axis = 1)
    df['Period End'] = df['Period End'].str.replace('March' , '03')
    df['Period End'] = df.apply(lambda x: datetime.strptime(x['Period End'], '%Y-%m'), axis = 1)

    df['Period'] = df.apply(lambda x: 'gregorian-interval/' + str(x['Period Start'])[:10] + 'T00:00:00/P' + str(diff_month(x['Period End'], x['Period Start'])) + 'M', axis = 1)

    indexNames = df[ df['Application Type'].str.contains('Heat paid for')].index
    df.drop(indexNames, inplace = True)

    df = df.replace({'DATAMARKER' : {'.' : 'Remove'}})

    indexNames = df[ df['DATAMARKER'].fillna('').str.contains('Remove')].index
    df.drop(indexNames, inplace = True)

    df['SIC'] = df.apply(lambda x: x['SIC'].split('.')[0], axis = 1)

    df = df.drop(columns=['Period Start', 'Period End'])

    df = df.rename(columns={'OBS' : 'Value', 'DATAMARKER' : 'Marker'})

    df = df.replace({'Marker' : {'#' : 'suppressed',
                                 '^' : 'suppressed'}})

    df = df[['Period', 'Geography', 'Technology Type', 'Application Type', 'Application Status', 'SIC', 'Value', 'Measure Type', 'Marker']]

    formatted_sheets['1.7'] = df

except Exception as err:
    raise Exception('Above Error found in Tab 1.7') from err

df


# In[79]:


try:
    df = tidied_sheets['M1.1']

    df['Measure Type'] = df.apply(lambda x: 'mw' if 'capacity' in x['Application Type'].lower() else 'applications', axis = 1)

    df['Period Start'] = df['Period Start'].str.replace('November' , '11')
    df['Period Start'] = df.apply(lambda x: datetime.strptime(x['Period Start'], '%Y-%m'), axis = 1)
    df['Period End'] = df['Period End'].str.replace('March' , '03')
    df['Period End'] = df.apply(lambda x: datetime.strptime(x['Period End'], '%Y-%m'), axis = 1)

    df['Period'] = df.apply(lambda x: 'month/' + x['Period Year'][:4] + '-' + x['Period Month'] if 'Total' not in x['Period Year'] else 'gregorian-interval/' + str(x['Period Start'])[:10] + 'T00:00:00/P' + str(diff_month(x['Period End'], x['Period Start'])) + 'M', axis = 1)

    df = df.rename(columns={'OBS' : 'Value'})

    df = df.replace({'Marker' : {'#' : 'suppressed',
                                 '^' : 'suppressed'}})

    df['Value'] = df.apply(lambda x: str(int(x['Value'])) if 'mw' not in x['Measure Type'] else x['Value'], axis = 1)

    df = df[['Period', 'Geography', 'Technology Type', 'Application Type', 'Application Status', 'SIC', 'Value', 'Measure Type']]

    formatted_sheets['M1.1'] = df

except Exception as err:
    raise Exception('Above Error found in Tab M1.1') from err

df


# In[80]:


try:
    df = tidied_sheets['M1.2']

    df['Measure Type'] = df.apply(lambda x: 'mw' if 'capacity' in x['Application Type'].lower() else 'applications', axis = 1)

    df['Period Start'] = df['Period Start'].str.replace('November' , '11')
    df['Period Start'] = df.apply(lambda x: datetime.strptime(x['Period Start'], '%Y-%m'), axis = 1)
    df['Period End'] = df['Period End'].str.replace('March' , '03')
    df['Period End'] = df.apply(lambda x: datetime.strptime(x['Period End'], '%Y-%m'), axis = 1)

    df['Period'] = df.apply(lambda x: 'month/' + x['Period Year'][:4] + '-' + x['Period Month'] if 'Total' not in x['Period Year'] else 'gregorian-interval/' + str(x['Period Start'])[:10] + 'T00:00:00/P' + str(diff_month(x['Period End'], x['Period Start'])) + 'M', axis = 1)

    df = df.rename(columns={'OBS' : 'Value'})

    df = df.replace({'Marker' : {'#' : 'suppressed',
                                 '^' : 'suppressed'}})

    df['Value'] = df.apply(lambda x: str(int(x['Value'])) if 'mw' not in x['Measure Type'] else x['Value'], axis = 1)

    df = df[['Period', 'Geography', 'Technology Type', 'Application Type', 'Application Status', 'SIC', 'Value', 'Measure Type']]

    formatted_sheets['M1.2'] = df

except Exception as err:
    raise Exception('Above Error found in Tab M1.2') from err

df


# In[81]:


try:
    df = tidied_sheets['M1.3']

    df['Measure Type'] = df.apply(lambda x: 'mw' if 'capacity' in x['Application Type'].lower() else 'applications', axis = 1)

    df['Period Start'] = df['Period Start'].str.replace('November' , '11')
    df['Period Start'] = df.apply(lambda x: datetime.strptime(x['Period Start'], '%Y-%m'), axis = 1)
    df['Period End'] = df['Period End'].str.replace('March' , '03')
    df['Period End'] = df.apply(lambda x: datetime.strptime(x['Period End'], '%Y-%m'), axis = 1)

    df['Period'] = df.apply(lambda x: 'month/' + x['Period Year'][:4] + '-' + x['Period Month'] if 'Total' not in x['Period Year'] else 'gregorian-interval/' + str(x['Period Start'])[:10] + 'T00:00:00/P' + str(diff_month(x['Period End'], x['Period Start'])) + 'M', axis = 1)

    df = df.rename(columns={'OBS' : 'Value', 'DATAMARKER' : 'Marker'})

    df = df.replace({'Marker' : {'#' : 'suppressed',
                                 '^' : 'suppressed'}})

    df = df[['Period', 'Geography', 'Technology Type', 'Application Type', 'Application Status', 'SIC', 'Value', 'Measure Type', 'Marker']]

    formatted_sheets['M1.3'] = df

except Exception as err:
    raise Exception('Above Error found in Tab M1.3') from err

df


# In[82]:


try:
    df = tidied_sheets['M1.4']

    df['Measure Type'] = df.apply(lambda x: 'mw' if 'capacity' in x['Application Type'].lower() else 'applications', axis = 1)

    df['Period Start'] = df['Period Start'].str.replace('November' , '11')
    df['Period Start'] = df.apply(lambda x: datetime.strptime(x['Period Start'], '%Y-%m'), axis = 1)
    df['Period End'] = df['Period End'].str.replace('March' , '03')
    df['Period End'] = df.apply(lambda x: datetime.strptime(x['Period End'], '%Y-%m'), axis = 1)

    df['Period'] = df.apply(lambda x: 'month/' + x['Period Year'][:4] + '-' + x['Period Month'] if 'Total' not in x['Period Year'] else 'gregorian-interval/' + str(x['Period Start'])[:10] + 'T00:00:00/P' + str(diff_month(x['Period End'], x['Period Start'])) + 'M', axis = 1)

    df = df.replace({'Application Type' : {'Table M1.4a - Number of TG applications1 (by date of first submission), by technology, per month, Great Britain, November 2011 to March 2021' : 'Number of Tariff Guarantee Applications',
                                           'Table M1.4b - Number of TG granted2 (by date of when the TG was granted), by technology, per month, Great Britain, November 2011 to March 2021' : 'Number of Tariff Guarantee Granted',
                                           'Table M1.4c - Number of TG stage 3 applications3 (by date of stage 3 application), by technology, per month, Great Britain, November 2011 to March 2021' : 'Number of Stage 3 Tariff Guarantee Applications'}})

    df = df.rename(columns={'OBS' : 'Value'})

    df = df[['Period', 'Geography', 'Technology Type', 'Application Type', 'Application Status', 'SIC', 'Value', 'Measure Type']]

    formatted_sheets['M1.4'] = df

except Exception as err:
    raise Exception('Above Error found in Tab M1.4') from err

df


# In[83]:


try:
    df = tidied_sheets['Q1.1']

    df['Measure Type'] = df.apply(lambda x: 'mw' if 'capacity' in x['Application Type'].lower() else 'applications', axis = 1)

    df['Period Start'] = df['Period Start'].str.replace('November' , '11')
    df['Period Start'] = df.apply(lambda x: datetime.strptime(x['Period Start'], '%Y-%m'), axis = 1)
    df['Period End'] = df['Period End'].str.replace('March' , '03')
    df['Period End'] = df.apply(lambda x: datetime.strptime(x['Period End'], '%Y-%m'), axis = 1)

    df['Period'] = df.apply(lambda x: 'quarter/' + x['Period Year'][:4] + '-' + x['Period Month'] if 'Total' not in x['Period Year'] else 'gregorian-interval/' + str(x['Period Start'])[:10] + 'T00:00:00/P' + str(diff_month(x['Period End'], x['Period Start'])) + 'M', axis = 1)

    df = df.rename(columns={'OBS' : 'Value'})

    df['Value'] = df.apply(lambda x: str(int(x['Value'])) if 'mw' not in x['Measure Type'] else x['Value'], axis = 1)

    df = df[['Period', 'Geography', 'Technology Type', 'Application Type', 'Application Status', 'SIC', 'Value', 'Measure Type']]

    formatted_sheets['Q1.1'] = df

except Exception as err:
    raise Exception('Above Error found in Tab Q1.1') from err

df


# In[84]:


try:
    df = tidied_sheets['2.1']

    df = df.replace({'Measure Type' : {'Number' : 'applications',
                                       'MW' : 'mw'}})

    df['Period Start'] = df['Period Start'].str.replace('April' , '04')
    df['Period Start'] = df.apply(lambda x: datetime.strptime(x['Period Start'], '%Y-%m'), axis = 1)
    df['Period End'] = df['Period End'].str.replace('March' , '03')
    df['Period End'] = df.apply(lambda x: datetime.strptime(x['Period End'], '%Y-%m'), axis = 1)

    df['Period'] = df.apply(lambda x: 'gregorian-interval/' + str(x['Period Start'])[:10] + 'T00:00:00/P' + str(diff_month(x['Period End'], x['Period Start'])) + 'M', axis = 1)

    df = df.rename(columns={'OBS' : 'Value'})

    df['Value'] = df.apply(lambda x: str(int(x['Value'])) if 'mw' not in x['Measure Type'] else x['Value'], axis = 1)

    df = df[['Period', 'Geography', 'Installation', 'Technology Type', 'Application Type', 'Application Status', 'Value', 'Measure Type']]

    formatted_sheets['2.1'] = df

except Exception as err:
    raise Exception('Above Error found in Tab 2.1') from err

df


# In[85]:


try:
    df = tidied_sheets['2.2']

    df = df.replace({'Measure Type' : {'Number' : 'applications',
                                       'MW' : 'mw'}})

    df['Period Start'] = df['Period Start'].str.replace('April' , '04')
    df['Period Start'] = df.apply(lambda x: datetime.strptime(x['Period Start'], '%Y-%m'), axis = 1)
    df['Period End'] = df['Period End'].str.replace('March' , '03')
    df['Period End'] = df.apply(lambda x: datetime.strptime(x['Period End'], '%Y-%m'), axis = 1)

    df['Period'] = df.apply(lambda x: 'gregorian-interval/' + str(x['Period Start'])[:10] + 'T00:00:00/P' + str(diff_month(x['Period End'], x['Period Start'])) + 'M', axis = 1)

    df = df.rename(columns={'OBS' : 'Value'})

    df['Value'] = df.apply(lambda x: str(int(x['Value'])) if 'mw' not in x['Measure Type'] else x['Value'], axis = 1)

    df = df[['Period', 'Geography', 'Technology Type', 'Application Type', 'Application Status', 'Value', 'Measure Type']]

    formatted_sheets['2.2'] = df

except Exception as err:
    raise Exception('Above Error found in Tab 2.2') from err

df


# In[86]:


try:
    df = tidied_sheets['2.3']

    df = df.replace({'Measure Type' : {'Number' : 'applications',
                                       'MW' : 'mw'}})

    df['Period Start'] = df['Period Start'].str.replace('April' , '04')
    df['Period Start'] = df.apply(lambda x: datetime.strptime(x['Period Start'], '%Y-%m'), axis = 1)
    df['Period End'] = df['Period End'].str.replace('March' , '03')
    df['Period End'] = df.apply(lambda x: datetime.strptime(x['Period End'], '%Y-%m'), axis = 1)

    df['Period'] = df.apply(lambda x: 'gregorian-interval/' + str(x['Period Start'])[:10] + 'T00:00:00/P' + str(diff_month(x['Period End'], x['Period Start'])) + 'M', axis = 1)

    df = df.rename(columns={'OBS' : 'Value'})

    df['Value'] = df.apply(lambda x: str(int(x['Value'])) if 'mw' not in x['Measure Type'] else x['Value'], axis = 1)

    df = df[['Period', 'Geography', 'Technology Type', 'Application Type', 'Application Status', 'Value', 'Measure Type']]

    formatted_sheets['2.3'] = df

except Exception as err:
    raise Exception('Above Error found in Tab 2.3') from err

df


# In[87]:


try:
    df = tidied_sheets['2.4']

    df = df.replace({'Measure Type' : {'Number' : 'applications',
                                       'MW' : 'mw'}})

    df['Period Start'] = df['Period Start'].str.replace('April' , '04')
    df['Period Start'] = df.apply(lambda x: datetime.strptime(x['Period Start'], '%Y-%m'), axis = 1)
    df['Period End'] = df['Period End'].str.replace('March' , '03')
    df['Period End'] = df.apply(lambda x: datetime.strptime(x['Period End'], '%Y-%m'), axis = 1)

    df['Period'] = df.apply(lambda x: 'gregorian-interval/' + str(x['Period Start'])[:10] + 'T00:00:00/P' + str(diff_month(x['Period End'], x['Period Start'])) + 'M', axis = 1)

    df = df.rename(columns={'OBS' : 'Value', 'DATAMARKER' : 'Marker'})

    df = df.replace({'Marker' : {'#' : 'suppressed',
                                 '^' : 'suppressed'}})

    df = df[['Period', 'Geography', 'Technology Type', 'Application Type', 'Application Status', 'Value', 'Measure Type', 'Marker']]

    formatted_sheets['2.4'] = df

except Exception as err:
    raise Exception('Above Error found in Tab 2.4') from err

df


# In[88]:


try:
    df = tidied_sheets['M2.1']

    df['Measure Type'] = df.apply(lambda x: 'mw' if 'capacity' in x['Application Type'].lower() else 'applications', axis = 1)

    df['Period Start'] = df['Period Start'].str.replace('April' , '04')
    df['Period Start'] = df.apply(lambda x: datetime.strptime(x['Period Start'], '%Y-%m'), axis = 1)
    df['Period End'] = df['Period End'].str.replace('March' , '03')
    df['Period End'] = df.apply(lambda x: datetime.strptime(x['Period End'], '%Y-%m'), axis = 1)

    df['Period'] = df.apply(lambda x: 'month/' + x['Period Year'][:4] + '-' + x['Period Month'] if 'Total' not in x['Period Year'] else 'gregorian-interval/' + str(x['Period Start'])[:10] + 'T00:00:00/P' + str(diff_month(x['Period End'], x['Period Start'])) + 'M', axis = 1)

    df = df.rename(columns={'OBS' : 'Value'})

    df = df.replace({'Marker' : {'#' : 'suppressed',
                                 '^' : 'suppressed'},
                     'Technology Type' : {'total' : 'all'}})

    df['Value'] = df.apply(lambda x: str(int(x['Value'])) if 'mw' not in x['Measure Type'] else x['Value'], axis = 1)

    df = df[['Period', 'Geography', 'Technology Type', 'Application Type', 'Application Status', 'Value', 'Measure Type']]

    formatted_sheets['M2.1'] = df

except Exception as err:
    raise Exception('Above Error found in Tab M2.1') from err

df


# In[89]:


try:
    df = tidied_sheets['M2.2']

    df['Measure Type'] = df.apply(lambda x: 'mw' if 'capacity' in x['Application Type'].lower() else 'applications', axis = 1)

    df['Period Start'] = df['Period Start'].str.replace('April' , '04')
    df['Period Start'] = df.apply(lambda x: datetime.strptime(x['Period Start'], '%Y-%m'), axis = 1)
    df['Period End'] = df['Period End'].str.replace('March' , '03')
    df['Period End'] = df.apply(lambda x: datetime.strptime(x['Period End'], '%Y-%m'), axis = 1)

    df['Period'] = df.apply(lambda x: 'month/' + x['Period Year'][:4] + '-' + x['Period Month'] if 'Total' not in x['Period Year'] else 'gregorian-interval/' + str(x['Period Start'])[:10] + 'T00:00:00/P' + str(diff_month(x['Period End'], x['Period Start'])) + 'M', axis = 1)

    df = df.rename(columns={'OBS' : 'Value'})

    df['Value'] = df.apply(lambda x: str(int(x['Value'])) if 'mw' not in x['Measure Type'] else x['Value'], axis = 1)

    df = df[['Period', 'Geography', 'Technology Type', 'Application Type', 'Application Status', 'Value', 'Measure Type']]

    formatted_sheets['M2.2'] = df

except Exception as err:
    raise Exception('Above Error found in Tab M2.2') from err

df


# In[90]:


try:
    df = tidied_sheets['Q2.1']

    df['Measure Type'] = df.apply(lambda x: 'mw' if 'capacity' in x['Application Type'].lower() else 'applications', axis = 1)

    df['Period Start'] = df['Period Start'].str.replace('April' , '04')
    df['Period Start'] = df.apply(lambda x: datetime.strptime(x['Period Start'], '%Y-%m'), axis = 1)
    df['Period End'] = df['Period End'].str.replace('March' , '03')
    df['Period End'] = df.apply(lambda x: datetime.strptime(x['Period End'], '%Y-%m'), axis = 1)

    df['Period'] = df.apply(lambda x: 'month/' + x['Period Year'][:4] + '-' + x['Period Month'] if 'Total' not in x['Period Year'] else 'gregorian-interval/' + str(x['Period Start'])[:10] + 'T00:00:00/P' + str(diff_month(x['Period End'], x['Period Start'])) + 'M', axis = 1)

    df = df.rename(columns={'OBS' : 'Value'})

    df['Value'] = df.apply(lambda x: str(int(x['Value'])) if 'mw' not in x['Measure Type'] else x['Value'], axis = 1)

    df = df[['Period', 'Geography', 'Technology Type', 'Application Type', 'Application Status', 'Value', 'Measure Type']]

    formatted_sheets['Q2.1'] = df

except Exception as err:
    raise Exception('Above Error found in Tab Q2.1') from err

df


# In[91]:


try:
    df = tidied_sheets['Q2.2']

    df['Measure Type'] = df.apply(lambda x: 'mw' if 'capacity' in x['Application Type'].lower() else 'applications', axis = 1)

    df['Period Start'] = df['Period Start'].str.replace('April' , '04')
    df['Period Start'] = df.apply(lambda x: datetime.strptime(x['Period Start'], '%Y-%m'), axis = 1)
    df['Period End'] = df['Period End'].str.replace('March' , '03')
    df['Period End'] = df.apply(lambda x: datetime.strptime(x['Period End'], '%Y-%m'), axis = 1)

    df['Period'] = df.apply(lambda x: 'quarter/' + x['Period Year'][:4] + '-' + x['Period Month'] if 'Total' not in x['Period Year'] else 'gregorian-interval/' + str(x['Period Start'])[:10] + 'T00:00:00/P' + str(diff_month(x['Period End'], x['Period Start'])) + 'M', axis = 1)

    df = df.rename(columns={'OBS' : 'Value'})

    df['Value'] = df.apply(lambda x: str(int(x['Value'])) if 'mw' not in x['Measure Type'] else x['Value'], axis = 1)

    df = df[['Period', 'Geography', 'Technology Type', 'Application Type', 'Application Status', 'Value', 'Measure Type']]

    formatted_sheets['Q2.2'] = df

except Exception as err:
    raise Exception('Above Error found in Tab Q2.2') from err

df


# In[92]:


df = pd.concat([v for k,v in formatted_sheets.items() if k in ['1.1', '1.2', '1.3', '1.4', '1.6', '1.7', 'M1.1', 'M1.2', 'M1.3', 'M1.4', 'Q1.1']], sort = False)

monthReplace = {'January' : '01',
              'February' : '02',
              'March' : '03',
              'April' : '04',
              'May' : '05',
              'June' : '06',
              'July' : '07',
              'August' : '08',
              'September' : '09',
              'October' : '10',
              'November' : '11',
              'Novemeber' : '11',
              'December' : '12'}

for key in monthReplace.keys():
    df['Period'] = df['Period'].str.replace(key, monthReplace[key])

df['Application Type'] = df.apply(lambda x: x['Application Type'][:-1] if RepresentsInt(x['Application Type'][-1:]) is True else x['Application Type'], axis = 1)

df['Application Type'] = df['Application Type'].str.replace(r"\(.*\)","").str.strip()

df = df.replace({'Technology Type' : {'Biogas6' : 'Biogas',
                                      'Biomethane1' : 'Biomethane',
                                      'Biomethane4' : 'Biomethane',
                                      'Biomethane5, 6' : 'Biomethane',
                                      'Large Solid Biomass Boiler (> 1000 kW)' : 'Large Solid Biomass Boiler',
                                      'Large Water or Ground Source Heat Pumps (>100 kW)' : 'Large Water or Ground Source Heat Pumps',
                                      'Medium Solid Biomass Boiler (200-1000 kW)' : 'Medium Solid Biomass Boiler',
                                      'Small Solid Biomass Boiler (< 200 kW)' : 'Small Solid Biomass Boiler',
                                      'Small Water or Ground Source Heat Pumps (< 100 kW)' : 'Small Water or Ground Source Heat Pumps',
                                      'Solar Thermal (< 200 kW)' : 'Solar Thermal'},
                 'Geography' : {'Great Britain' : 'K03000001'}})

df


# In[93]:


applications = df.loc[df['Measure Type'] == 'applications']

applications['Applicant'] = 'non-domestic'

applications


# In[94]:


capacity = df.loc[df['Measure Type'] == 'mw']

capacity = capacity.drop(columns=['Application Status'])

indexNames = capacity[ capacity['Application Type'].fillna('').str.contains('Cumulative')].index
capacity.drop(indexNames, inplace = True)

indexNames = capacity[ capacity['Marker'].fillna('').str.contains('N/A')].index
capacity.drop(indexNames, inplace = True)

capacity['Measure Type'] = 'capacity'
capacity['Unit'] = 'mw'

scraper.dataset.title = 'RHI deployment data - Capacity (MW)'
scraper.dataset.comment = 'Capacity (MW) statistics for the Renewable Heat Incentive (RHI) programme'
scraper.dataset.description = 'Capacity (MW) statistics for the Renewable Heat Incentive (RHI) programme on technology type, region, local authority'                               'Technology types match Ofgem tariff bands'                               'Duplicate, withdrawn and cancelled applications are not included in the total of full applications.'                               'Accredited applications are a subset of full applications i.e. once a system has become accredited, it is counted as both a full application and an accredited installation.  '                               'Tariff guarantees are only available for a subset of non-domestic tariff bands.  Full guidance can be found on the Ofgem RHI site.'

COLUMNS_TO_NOT_PATHIFY = ['Period', 'Geography', 'Value', 'Marker']

for col in capacity.columns.values.tolist():
	if col in COLUMNS_TO_NOT_PATHIFY:
		continue
	try:
		capacity[col] = capacity[col].apply(pathify)
	except Exception as err:
		raise Exception('Failed to pathify column "{}".'.format(col)) from err

capacity.to_csv('rhi-deployment-data-capacity-mw-observations.csv', index=False)

catalog_metadata = scraper.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('rhi-deployment-data-capacity-mw-catalog-metadata.json')

capacity


# In[95]:


df = pd.concat([v for k,v in formatted_sheets.items() if k in ['2.1', '2.2', '2.3', '2.4', 'M2.1', 'M2.2', 'Q2.1', 'Q2.2']], sort = False)

monthReplace = {'January' : '01',
              'February' : '02',
              'March' : '03',
              'April' : '04',
              'May' : '05',
              'June' : '06',
              'July' : '07',
              'August' : '08',
              'September' : '09',
              'October' : '10',
              'November' : '11',
              'Novemeber' : '11',
              'December' : '12'}

for key in monthReplace.keys():
    df['Period'] = df['Period'].str.replace(key, monthReplace[key])

df['Installation'] = df['Installation'].fillna('Total (New & legacy installations)')

df['Installation'] = df['Installation'].str.replace('&', 'and')

for col in df.columns.values.tolist():
    if col in ['Period', 'Value', 'Geography', 'Marker']:
        continue
    try:
        df[col] = df.apply(lambda x: x[col][:-1] if RepresentsInt(x[col][-1:]) is True else x[col], axis = 1)
        #df[col] = df[col].str.replace(r"\(.*\)","").str.strip()
    except Exception as err:
        raise Exception('Failed to clean column "{}".'.format(col)) from err

df = df.replace({'Application Status' : {'Rejected, Failed or Cancelled3,' : 'Rejected, Failed or Cancelled'},
                 'Installation' : {'Legacy installations3,' : 'Legacy installations'},
                 'Geography' : {'Great Britain' : 'K03000001'}})

df['SIC'] = 'total'

df['Applicant'] = 'domestic'

df


# In[96]:


scraper = Scraper(seed="rhi-deployment-data-application-numbers-domestic-and-non-domestic-info.json")
scraper


# In[97]:


df = pd.concat([df, applications], sort = False)

df['Installation'] = df['Installation'].fillna('Total')

df['Measure Type'] = 'applications'
df['Unit'] = 'applicant'

indexNames = df[ df['Application Type'].fillna('').str.contains('Cumulative')].index
df.drop(indexNames, inplace = True)

scraper.dataset.title = 'RHI deployment data - Application Numbers, domestic and non-domestic'
scraper.dataset.comment = 'Application statistics for the Renewable Heat Incentive (RHI) programme'
scraper.dataset.description = 'Application statistics for the Renewable Heat Incentive (RHI) programme by technology type, region, local authority & domestic and non-domestic'                               'Accredited applications are a subset of full applications i.e. once a system has become accredited, it is counted as both a full application and an accredited installation.'                               'New installations refers to applications for systems installed after the launch of the domestic RHI scheme on 9 April 2014.'                               'Legacy refers to all applications for systems installed before the launch of the domestic RHI scheme on 9 April 2014, whether they claimed a RHPP voucher or not.'

COLUMNS_TO_NOT_PATHIFY = ['Period', 'Geography', 'Value', 'Marker']

for col in df.columns.values.tolist():
	if col in COLUMNS_TO_NOT_PATHIFY:
		continue
	try:
		df[col] = df[col].apply(pathify)
	except Exception as err:
		raise Exception('Failed to pathify column "{}".'.format(col)) from err

df.to_csv('rhi-deployment-data-application-numbers-domestic-and-non-domestic-observations.csv', index=False)

catalog_metadata = scraper.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('rhi-deployment-data-application-numbers-domestic-and-non-domestic-catalog-metadata.json')

df

