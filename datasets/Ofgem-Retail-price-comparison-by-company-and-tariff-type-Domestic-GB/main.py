from gssutils import * 
import json 

scrape = Scraper(seed="info.json") 

publisher = "The Office of Gas and Electricity Markets"
title = "Retail price comparison by company and tariff type: Domestic (GB)"

scrape.publisher = publisher
scrape.distributions[0].title = title

scrape

def Value_To_Number(value):
    # tidying up values -> removing comma and whitespace
    try:
        new_value = value.replace(' ', '').replace(',', '').strip()
        return new_value
    except:
        return ''
    
def Time_Formatter(date):
    # returns time in gregorian-day/dd/mm/yyyy format
    return 'gregorian-day/' + date

trace = TransformTrace()
link = scrape.distributions[0].downloadURL
link = link.split('?')[0] # added ?fake=.csv to download link as a hacky fix

columns = ['Period', 'Dimension 1', 'Value']

trace.start(publisher, title, columns, link)

source = scrape.distributions[0].as_pandas()

dimensions = list(source.columns) # list of columns
dimensions = [col for col in dimensions if 'date' not in col.lower()] # list of the dimensions

df_list = []
for col in dimensions:
    df_loop = pd.DataFrame()
    df_loop['Period'] = source['Date']
    df_loop['Dimension 1'] = col
    df_loop['Value'] = source[col]
    df_list.append(df_loop)
    
df = pd.concat(df_list)

trace.Period("Values taken from 'Date' column")
trace.Dimension_1("Values one of {}", dimensions)
trace.Value("Values taken from {} columns", dimensions)

df['Value'] = df['Value'].apply(Value_To_Number)
trace.Value("Removed commas and whitespaces from values")
df['Period'] = df['Period'].apply(Time_Formatter)
trace.Period("Formatted time to 'gregorian-day/dd/mm/yyyy'")

# if rows have no value -> create a Marker column and add it to the trace
if '' in df['Value'].unique():
    marker = 'x' # x used as a marker
    df.loc[df['Value'] == '', 'Marker'] = marker 
    df = df[['Period', 'Dimension 1', 'Marker', 'Value']]
    trace.add_column("Marker")
    trace.Marker("Rows with no values have a marker of '{}'", marker)
    
trace.store(title, df)

out = Path('out')
out.mkdir(exist_ok=True)
trace.render("spec_v1.html")
df.drop_duplicates().to_csv(out / f'{title}.csv', index=False)
