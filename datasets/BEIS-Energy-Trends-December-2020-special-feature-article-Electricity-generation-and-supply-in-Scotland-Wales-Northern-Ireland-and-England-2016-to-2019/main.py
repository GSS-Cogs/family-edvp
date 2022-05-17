#!/usr/bin/env python
# coding: utf-8

# In[89]:


# Electricity generation and supply in Scotland, Wales, Northern Ireland and England, 2016 to 2019

import copy
import json
import pandas
from gssutils import *
import numpy as np

info = json.load(open('info.json'))


# In[90]:


scraper = Scraper(seed='info.json')
scraper

distribution = scraper.distributions[1] #check how to specify the media
distribution


# In[91]:


tabs = distribution.as_databaker(data_only=True)

tab_names = [tab.name for tab in tabs]
tab_names

def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

def mid(s, offset, amount):
    return s[offset:offset+amount]

def create_xy_lookup(period_dimension):
    override_from_xy = {}
    not_blank_cells = [x for x in period_dimension.hbagset if x.value != '']
    for cell in period_dimension.hbagset:
        # If a dimension cell is blank
        if cell.value == '':
            # Is there a value two cells to the left? if so use that value
            cell_checked = [x for x in not_blank_cells if x.x == cell.x-2]
            if len(cell_checked) > 0:
                override_from_xy[cell.x] = cell_checked[0].value
            cell_checked = [x for x in not_blank_cells if x.x == cell.x-1]
            if len(cell_checked) > 0:
                override_from_xy[cell.x] = cell_checked[0].value
            # Is there a value one cells to the right? if so use that value
            cell_checked = [x for x in not_blank_cells if x.x == cell.x+1]
            if len(cell_checked) > 0:
                override_from_xy[cell.x] = cell_checked[0].value
            # Is there a value two cells to the right? if so use that value
            cell_checked = [x for x in not_blank_cells if x.x == cell.x+2]
            if len(cell_checked) > 0:
                override_from_xy[cell.x] = cell_checked[0].value

    return override_from_xy


pd.set_option('display.float_format', lambda x: '%.0f' % x)

for tab in tabs:
    if tab.name == 'Contents':
        title1 = ' '.join(tab.excel_ref('B18').value.split()[2:])
        title2 = ' '.join(tab.excel_ref('B19').value.split()[2:])
        print(title1)
        print(title2)


# In[92]:



trace = TransformTrace()

for tab in tabs:
    if tab.name == 'Generation and supply':
        title = title1
        scraper.dataset.title = title
        scraper.dataset.comment = title
        scraper.dataset.description = title

        footnote = tab.excel_ref('A23').expand(DOWN)

        generation = tab.excel_ref('A5').expand(DOWN).is_not_blank() - footnote
        region = tab.excel_ref('B4').expand(RIGHT).is_not_blank()

        period = region.shift(UP)

        observations = tab.excel_ref('B5').expand(DOWN).expand(RIGHT).is_not_blank()

        dimensions = [
            HDim(period, 'Period', DIRECTLY, ABOVE),
            HDim(region, 'Region', DIRECTLY, ABOVE),
            HDim(generation, 'Measure Type', DIRECTLY, LEFT),
            HDimConst('Unit', 'gwh')
        ]
        my_lookup_dict = create_xy_lookup(dimensions[0])

        tidy_sheet = ConversionSegment(tab, dimensions, observations, includecellxy=True)        
        savepreviewhtml(tidy_sheet,fname=tab.name + "Preview.html")

        df = tidy_sheet.topandas()

        df["Period"] = df.apply(lambda x: my_lookup_dict.get(x['__x'], x) if '20' not in x['Period'] else x['Period'], axis = 1)

        df['Period'] = df.apply(lambda x: 'year/' + left(str(x['Period']), 4), axis = 1)

        df = df.replace({'Region': {
            'UK Total' : 'K02000001',
            'Scotland' : 'S92000003',
            'Wales' : 'W92000004',
            'Northern Ireland' : 'N92000002',
            'England' : 'K04000001'
            }})

        df = df.replace(r'^\s*$', np.nan, regex=True)

        df['OBS'] = df['OBS'].astype(float).round(2)
        df.rename(columns={'OBS' : 'Value'}, inplace=True)
        tidy = df[['Period', 'Region', 'Value', 'Measure Type', 'Unit']]

        for column in tidy:
            if column in ('Description of Generation & Supply', 'Measure Type'):
                tidy[column] = tidy[column].map(lambda x: pathify(x))

        tidy = tidy.replace({'Measure Type' : {'consumption-from-public-supply-a' : 'consumption-from-public-supply',
                                               'electricity-sales-public-supply-b' : 'electricity-sales-public-supply',
                                               'statistical-difference-between-calculated-consumption-a-and-sales-b' : 'statistical-difference-between-calculated-consumption-a-and-sales'}})

        """info['transform']['columns']['Measure Type']['types'] = tidy['Measure Type'].unique().tolist()

        with open('info.json', 'w') as f:
            json.dump(info, f, indent=4)"""

        tidy.to_csv(pathify(tab.name) +  '-observations.csv', index=False)

        catalog_metadata = scraper.as_csvqb_catalog_metadata()
        catalog_metadata.to_json_file(pathify(tab.name) + '-catalog-metadata.json')

    elif tab.name == 'Electricity generation by fuel':
        title = title2
        scraper.dataset.title = title
        scraper.dataset.comment = title
        scraper.dataset.description = title

        footnote = tab.excel_ref('A53').expand(DOWN).expand(RIGHT).is_not_blank()

        within_which = tab.excel_ref('A').expand(DOWN).by_index([20, 27, 32, 41, 46])

        share_totalGen = tab.excel_ref('A40').expand(DOWN).expand(RIGHT) - footnote

        total_electricity = tab.excel_ref('B').expand(DOWN).by_index([15, 25, 39])

        generators = tab.excel_ref('A5').expand(DOWN).is_not_blank()|total_electricity
        generators = generators - within_which - share_totalGen - footnote

        fuel = tab.excel_ref('B5').expand(DOWN).is_not_blank() - share_totalGen - footnote

        region = tab.excel_ref('C4').expand(RIGHT).is_not_blank()

        period = region.shift(UP)

        observations = tab.excel_ref('C5').expand(DOWN).expand(RIGHT).is_not_blank() - share_totalGen - footnote

        dimensions = [
            HDim(period, 'Period', DIRECTLY, ABOVE),
            HDim(region, 'Region', DIRECTLY, ABOVE),
            HDim(generators, 'Generating Company', CLOSEST, ABOVE),
            HDim(fuel, 'Fuel', DIRECTLY, LEFT),
            HDimConst('Measure Type', 'Electricity Generated'),
            HDimConst('Unit', 'GWh')
        ]
        my_lookup_dict = create_xy_lookup(dimensions[0])

        tidy_sheet = ConversionSegment(tab, dimensions, observations, includecellxy=True)
        savepreviewhtml(tidy_sheet,fname=tab.name + "Preview.html")

        df = tidy_sheet.topandas()

        df["Period"] = df.apply(lambda x: my_lookup_dict.get(x['__x'], x) if '20' not in x['Period'] else x['Period'], axis = 1)

        df['Period'] = df.apply(lambda x: 'year/' + left(str(x['Period']), 4), axis = 1)

        df = df.replace({'Region': {
            'UK total' : 'K02000001',
            'Scotland' : 'S92000003',
            'Wales' : 'W92000004',
            'Northern Ireland' : 'N92000002',
            'England' : 'K04000001'
            }})

        '''removing footnote caption from fuel type'''
        df['Fuel'] = df['Fuel'].str.replace(r'\(.*\)', ' ')

        df['OBS'] = df['OBS'].astype(float).round(2)
        df.rename(columns={'OBS' : 'Value', 'Generating Company' : 'Generating Companies'}, inplace=True)

        tidy = df[['Period', 'Region', 'Generating Companies', 'Fuel', 'Value', 'Measure Type', 'Unit']]
        for column in tidy:
            if column in ('Measure Type', 'Unit', 'Fuel'):
                tidy[column] = tidy[column].map(lambda x: pathify(x))

        tidy['Fuel'] = tidy['Fuel'].str.strip()

        tidy = tidy.replace({'Fuel' : {'TOTAL ALL GENERATING COMPANIES' : 'Total All Generating Companies', 
                                       'TOTAL MPPs' : 'Total MPPs',
                                       'TOTAL OTHER GENERATORS' : 'Total Other Generators'},
                             'Generating Companies' : {
                                        'TOTAL ALL GENERATING COMPANIES' : 'Total All Generating Companies', 
                                        'TOTAL MPPs' : 'Total MPPs',
                                        'TOTAL OTHER GENERATORS' : 'Total Other Generators'}})

        """info['transform']['columns']['Measure Type']['types'] = tidy['Measure Type'].unique().tolist()

        with open('info.json', 'w') as f:
            json.dump(info, f, indent=4)"""

        tidy.to_csv(pathify(tab.name) + '-observations.csv', index=False)

        catalog_metadata = scraper.as_csvqb_catalog_metadata()
        catalog_metadata.to_json_file(pathify(tab.name) + '-catalog-metadata.json')

tidy


# In[93]:


from IPython.core.display import HTML
for col in tidy:
    if col not in ['Value']:
        tidy[col] = tidy[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(tidy[col].cat.categories)

