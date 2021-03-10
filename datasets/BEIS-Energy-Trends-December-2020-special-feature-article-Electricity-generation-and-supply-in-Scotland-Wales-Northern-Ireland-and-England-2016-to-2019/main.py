#!/usr/bin/env python
# coding: utf-8

# In[34]:


# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.9.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# Electricity generation and supply in Scotland, Wales, Northern Ireland and England, 2016 to 2019

import copy
import json
import pandas
from gssutils import *
from databaker.framework import *

cubes = Cubes('info.json')

scraper = Scraper(seed='info.json')
scraper

distribution = scraper.distributions[1] #check how to specify the media
distribution

tabs = distribution.as_databaker()

tab_names = [tab.name for tab in tabs]
tab_names

def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

def mid(s, offset, amount):
    return s[offset:offset+amount]

def with_year_overrides(period_dimension):
    """
    We're going to add a cellvalue overrides to each cell within the dimension AFTER
    it's been defined.
    So replacing the value of any dimensions cells that are blank with the appropriate year.
    """
    not_blank_cells = [x for x in period_dimension.hbagset if x.value != '']
    for cell in period_dimension.hbagset:
        # If a dimension cell is blank
        if cell.value == '':
            # Is there a value two cells to the left? if so use that value
            cell_checked = [x for x in not_blank_cells if x.x == cell.x-2]
            if len(cell_checked) > 0:
                period_dimension.AddCellValueOverride(cell, cell_checked[0].value)
            # Is there a value one cell to the left? if so use that value
            cell_checked = [x for x in not_blank_cells if x.x == cell.x-1]
            if len(cell_checked) > 0:
                period_dimension.AddCellValueOverride(cell, cell_checked[0].value)
            # Is there a value one cells to the right? if so use that value
            cell_checked = [x for x in not_blank_cells if x.x == cell.x+1]
            if len(cell_checked) > 0:
                period_dimension.AddCellValueOverride(cell, cell_checked[0].value)
            # Is there a value two cells to the right? if so use that value
            cell_checked = [x for x in not_blank_cells if x.x == cell.x+2]
            if len(cell_checked) > 0:
                period_dimension.AddCellValueOverride(cell, cell_checked[0].value)
    return period_dimension


pd.set_option('display.float_format', lambda x: '%.0f' % x)

for tab in tabs:
    if tab.name == 'Contents':
        title1 = ' '.join(tab.excel_ref('B18').value.split()[2:])
        title2 = ' '.join(tab.excel_ref('B19').value.split()[2:])
        print(title1)
        print(title2)

# +
trace = TransformTrace()

for tab in tabs:
    if tab.name == 'Generation and supply':
        title = title1
        scraper.dataset.title = title
        scraper.dataset.comment = title
        scraper.dataset.description = title

        columns = ['Period', 'Region', 'Description of Generation & Supply', 'Measure Type', 'Unit', 'Value']
        trace.start(title, tab, columns, distribution.downloadURL)

        footnote = tab.excel_ref('A23').expand(DOWN)

        generation = tab.excel_ref('A5').expand(DOWN).is_not_blank() - footnote
        region = tab.excel_ref('B4').expand(RIGHT).is_not_blank()

        trace.Period("Selected as the given years, with the blank cells filled in with the 'with_year_overrides' function")
        period = region.shift(UP)

        observations = tab.excel_ref('B5').expand(DOWN).expand(RIGHT).is_not_blank()

        dimensions = [
            HDim(period, 'Period', DIRECTLY, ABOVE),
            HDim(region, 'Region', DIRECTLY, ABOVE),
            HDim(generation, 'Measure Type', DIRECTLY, LEFT),
            HDimConst('Unit', 'gwh')
        ]
        dimensions[0] = with_year_overrides(dimensions[0])

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        trace.store('dataframe1', tidy_sheet.topandas())

        df = trace.combine_and_trace(title, 'dataframe1')

        df = df.replace({'Region': {
            'UK Total' : 'K02000001',
            'Scotland' : 'S92000003',
            'Wales' : 'W92000004',
            'Northern Ireland' : 'N92000002',
            'England' : 'K04000001'
            }})

        df['Period'] = df.apply(lambda x: 'year/' + left(str(x['Period']), 4), axis = 1)
        df['OBS'] = df['OBS'].astype(int)
        df.rename(columns={'OBS' : 'Value'}, inplace=True)
        tidy = df[['Period', 'Region', 'Value', 'Measure Type', 'Unit']]

        for column in tidy:
            if column in ('Description of Generation & Supply', 'Measure Type'):
                tidy[column] = tidy[column].map(lambda x: pathify(x))

        tidy = tidy.replace({'Measure Type' : {'consumption-from-public-supply-a' : 'consumption-from-public-supply',
                                               'electricity-sales-public-supply-b' : 'electricity-sales-public-supply',
                                               'statistical-difference-between-calculated-consumption-a-and-sales-b' : 'statistical-difference-between-calculated-consumption-a-and-sales'}})

        cubes.add_cube(copy.deepcopy(scraper), tidy, scraper.dataset.title)

    elif tab.name == 'Electricity generation by fuel':
        title = title2
        scraper.dataset.title = title
        scraper.dataset.comment = title
        scraper.dataset.description = title

        columns = ['Period', 'Region', 'Generating Company', 'Fuel Type', 'Measure Type', 'Unit', 'Value']
        trace.start(title, tab, columns, distribution.downloadURL)

        footnote = tab.excel_ref('A53').expand(DOWN).expand(RIGHT).is_not_blank()

        within_which = tab.excel_ref('A').expand(DOWN).by_index([20, 27, 32, 41, 46])

        share_totalGen = tab.excel_ref('A40').expand(DOWN).expand(RIGHT) - footnote

        total_electricity = tab.excel_ref('B').expand(DOWN).by_index([15, 25, 39])

        trace.Generating_Company('Selected as the electricity generating companies with the totals pulled over         from cell B, and with the share of total generation(%) and the footnote removed')
        generators = tab.excel_ref('A5').expand(DOWN).is_not_blank()|total_electricity
        generators = generators - within_which - share_totalGen - footnote

        trace.Fuel_Type('Selected as the fuel type with the share of total generation(%) and the footnote removed.             The totals cell pulled over to generators are removed below')
        fuel = tab.excel_ref('B5').expand(DOWN).is_not_blank() - share_totalGen - footnote

        region = tab.excel_ref('C4').expand(RIGHT).is_not_blank()

        trace.Period("Selected as the given years with the blank cells filled in with the 'with_year_overrides' function")
        period = region.shift(UP)

        observations = tab.excel_ref('C5').expand(DOWN).expand(RIGHT).is_not_blank() - share_totalGen - footnote

        '''Correcting the 'total' cells in fuel column'''
        fuel_override = {}
        for cell in fuel:
            if cell in generators:
                fuel_override[cell.value] = 'all'

        dimensions = [
            HDim(period, 'Period', DIRECTLY, ABOVE),
            HDim(region, 'Region', DIRECTLY, ABOVE),
            HDim(generators, 'Generating Company', CLOSEST, ABOVE),
            HDim(fuel, 'Fuel', DIRECTLY, LEFT, cellvalueoverride = fuel_override),
            HDimConst('Measure Type', 'gigawatt hours'),
            HDimConst('Unit', 'GWh')
        ]
        dimensions[0] = with_year_overrides(dimensions[0])

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        trace.store('dataframe2', tidy_sheet.topandas())

        df = trace.combine_and_trace(title, 'dataframe2')

        df = df.replace({'Region': {
            'UK total' : 'K02000001',
            'Scotland' : 'S92000003',
            'Wales' : 'W92000004',
            'Northern Ireland' : 'N92000002',
            'England' : 'K04000001'
            }})

        '''removing footnote caption from fuel type'''
        df['Fuel'] = df['Fuel'].str.replace(r'\(.*\)', ' ')

        df['Period'] = df.apply(lambda x: 'year/' + left(str(x['Period']), 4), axis = 1)
        df['OBS'] = df['OBS'].astype(int)
        df.rename(columns={'OBS' : 'Value'}, inplace=True)

        tidy = df[['Period', 'Region', 'Generating Company', 'Fuel', 'Value', 'Measure Type', 'Unit']]
        for column in tidy:
            if column in ('Generating Company', 'Fuel', 'Measure Type'):
                tidy[column] = tidy[column].map(lambda x: pathify(x))

        cubes.add_cube(copy.deepcopy(scraper), tidy, scraper.dataset.title)

tidy


# In[35]:


cubes.output_all()


# In[36]:



from IPython.core.display import HTML
for col in tidy:
    if col not in ['Value']:
        tidy[col] = tidy[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(tidy[col].cat.categories)

