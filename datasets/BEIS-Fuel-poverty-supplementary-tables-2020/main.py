# -*- coding: utf-8 -*-
# +
from gssutils import * 
import json

cubes = Cubes("info.json")
# -

# # Helpers
#
# These are all the same two variations of table repeated, so we're just gonna have a function for each

# +
LITTLE_TABLE_ANCHOR = "Median equivalised fuel costs (£)"
BIG_TABLE_ANCHOR = "Proportion of households within group (%)" # note we dont want this cell but we're using it to differentiate the styles of table - 

def process_little_table(anchor, task, trace):
    """
    Given a single anchoring cell, process the smaller style of the tables
    """
    
    year = "year/"+tab.excel_ref('A1').value.split(",")[-1]
    trace.Year('Get year from cell A1 and add "/year" prefix, gets us:"{}"'.format(year))
    
    # Get the obs, we don't want columns f + G
    # TODO - safety to make sure F & G actually are the columns we don't want for a given table 
    obs = anchor.shift(DOWN).expand(RIGHT).expand(DOWN).is_not_blank()
    obs = obs - tab.excel_ref('F:G')
    obs = clean_lower_tables(obs)

    trace.add_column("Category")
    trace.Category('Extract colum headers as a temporary "Category" column.')
    horizontal_dimension = anchor.expand(RIGHT).is_not_blank()

    # Use an alias to trace the differentiating dimension, as the name may or may not
    # support being set as an attribute
    trace.add_column({task["tables"][tab.name]["differentiating_dimension"]:"Diffdim"})
    trace.Diffdim('Take the left hand column as: "{}".'.format(task["tables"][tab.name]["differentiating_dimension"]))
    
    left_column = anchor.shift(LEFT).fill(DOWN).is_not_blank()
    left_column = clean_lower_tables(left_column)

    measure_type = anchor.fill(RIGHT)

    dimensions = [
        HDimConst("Period", year),
        HDim(horizontal_dimension, "Category", DIRECTLY, ABOVE),
        HDim(left_column, task["tables"][tab.name]["differentiating_dimension"], DIRECTLY, LEFT)
    ]

    cs = ConversionSegment(obs, dimensions)
    df = cs.topandas()
    
    # Pathify the differentiating dimension, switch all-hosueholds to all
    df[task["tables"][tab.name]["differentiating_dimension"]] = df[task["tables"][tab.name]["differentiating_dimension"]].apply(pathify)
    df[task["tables"][tab.name]["differentiating_dimension"]] = df[task["tables"][tab.name]["differentiating_dimension"]] \
            .map(lambda x: x.replace("all-households", "all"))

    # Measure and Unit
    trace.Unit('Set unit from mapping: "{}".'.format(json.dumps(task["units_map"])))
    df["Unit"] = df["Category"].apply(LookupFromDict("unit", task["units_map"]))
    
    trace.Measure_Type('Set measure type from mapping: "{}".'.format(json.dumps(task["measures_map"])))
    df["Measure Type"] = df["Category"].apply(LookupFromDict("measure", task["measures_map"]))

    # Add the constant column
    if "constant_columns" in task["tables"][tab.name].keys():
        for k,v in task["tables"][tab.name]["constant_columns"].items():
            trace.add_column(k)
            trace.multi([k.replace(" ", "_")], 'Set as value: "{}".'.format(v))
            df[k] = v
    
    # Tidy up
    df = df.rename(columns={"OBS": "Value"})

    return df, trace

def process_big_table(anchor, task, trace):
    """
    Given a single anchoring cell, process the bigger style of the tables
    """
    year = "year/"+tab.excel_ref('A1').value.split(",")[-1]
    
    # Switch to the anchor point we actually want to use
    anchor = anchor.expand(RIGHT).filter(LITTLE_TABLE_ANCHOR).assert_one()
    
    fuel = anchor.expand(RIGHT).expand(DOWN).filter(contains_string("fuel"))
    fuel = clean_lower_tables(fuel)
    assert len(fuel) == 2, 'We should only be selecting two references to "fuel" per sub table'
    
    
def clean_lower_tables(bag):
    """
    Cut everything below the relevant "All households" line
    """
    return bag -bag.expand(DOWN).expand(LEFT).filter("All households").by_index(1).fill(DOWN).expand(RIGHT)

# TODO - there's gotta be a baked in pandas method for this im not remembering, look it up, kiss etc
class LookupFromDict:
    """
    Pandas apply function that takes a dictionary argument.
    Used to figure out the measures to use, uses the "measures_map"
    dictionary passed from the task
    """
    
    # store the dict in the class on instantiation
    def __init__(self, name, measures_map):
        self.map = measures_map
        self.name = name
        
    # do the lookup on each cell value passed in by df[whatever].apply()
    def __call__(self, cell_value):
        try:
            for k in self.map.keys():
                if k in cell_value: # use "in" not a direct lookup to avoid whitespace/footnote issues
                    return self.map[k]
        except Exception as err:
            raise ('Measure lookup, couldnt find {} lookup for value: "{}".'.format(self.name, cell_value)) from err



# -

scraper = Scraper(seed="info.json")   
scraper


distro = scraper.distribution(latest=True)
tabs = distro.as_databaker()
tabs = [x for x in tabs if "Table" in x.name] # TODO = typos? Tables change? Numnbering of tables by concept changes?

# # Energy Efficiency and Dwelling Characteristics
#
# Tables 1 through 11 (the parameters, the processing will happen later on)

# +

# We're just gonna loop and use slightly different variables each time.
# If you need yo tweak anything you should be able to do it here.
energy_efficiency_task = {
    "name": "Energy Efficiency",
    "store_as": "1through17",
    "tables":{
        "Table 1": {
            "sub_table_count": 1,
            "differentiating_dimension": "Low Income High costs Matrix"
        },
        "Table 2": {
            "sub_table_count": 1,
            "differentiating_dimension": "FPEER"
        },
        "Table 3": {
            "sub_table_count": 1,
            "differentiating_dimension": "SAP BAND"
        },
        "Table 4": {
            "sub_table_count": 1,
            "differentiating_dimension": "Rurality"
        },
        "Table 5": {
            "sub_table_count": 1,
            "differentiating_dimension": "Region"
        },
        "Table 6": {
            "sub_table_count": 1,
            "differentiating_dimension": "Dwelling Type"
        },
       "Table 7": {
            "sub_table_count": 1,
            "differentiating_dimension": "Dwelling Age"
        },
       "Table 8": {
            "sub_table_count": 1,
            "differentiating_dimension": "Floor Area"
        },
       "Table 9": {
            "sub_table_count": 1,
            "differentiating_dimension": "Gas Grid Connection"
        },
       "Table 10": {
            "sub_table_count": 1,
            "differentiating_dimension": "Main Fuel Type"
        },
       "Table 11": {
            "sub_table_count": 1,
            "differentiating_dimension": "Wall Insulation"
        }
    },
    "measures_map": {
        "Median equivalised fuel costs (£)": "Median costs",
        "Median after housing costs (AHC), equivalised income (£)": "Median income",
        "Median Fuel Poverty Energy Efficiency Rating (FPEER)": "Median rating",
        "Median floor area (m2)": "Median floor area"
    },
    "units_map": {
        "Median equivalised fuel costs (£)": "gdp",
        "Median after housing costs (AHC), equivalised income (£)": "gdp",
        "Median Fuel Poverty Energy Efficiency Rating (FPEER)": "rating",
        "Median floor area (m2)": "m2"
    }
}
# -


# # Household characteristics
#
# Tables 12 through 16 (the parameters, the processing will happen later on)

# +

# We're just gonna loop and use slightly different variables each time.
# If you need yo tweak anything you should be able to do it here.
household_characteristics_task = {
    "name": "Household characteristics",
    "store_as": "12through16",
    "tables":{
        "Table 12": {
            "sub_table_count": 1,
            "differentiating_dimension": "Tenure"
        },
        "Table 13": {
            "sub_table_count": 1,
            "differentiating_dimension": "Household Composition"
        },
       "Table 14": {
            "sub_table_count": 1,
            "differentiating_dimension": "Age of Youngest Person"
        },
       "Table 15": {
            "sub_table_count": 1,
            "differentiating_dimension": "Age of Oldest Person"
        },
       "Table 16": {
            "sub_table_count": 1,
            "differentiating_dimension": "Ethnicity"
        }
    },
    "measures_map": {
        "Median equivalised fuel costs (£)": "Median costs",
        "Median after housing costs (AHC), equivalised income (£)": "Median income",
        "Median Fuel Poverty Energy Efficiency Rating (FPEER)": "Median rating",
        "Median floor area (m2)": "Median floor area"
    },
    "units_map": {
        "Median equivalised fuel costs (£)": "gdp",
        "Median after housing costs (AHC), equivalised income (£)": "gdp",
        "Median Fuel Poverty Energy Efficiency Rating (FPEER)": "rating",
        "Median floor area (m2)": "m2"
    }
}
# -

# # Household income
#
# Tables 17 through 18 (the parameters, the processing will happen later on)

# +

# We're just gonna loop and use slightly different variables each time.
# If you need yo tweak anything you should be able to do it here.
household_income_task = {
    "name": "Household income",
    "store_as": "17through18",
    "tables": {
        "Table 17": {
            "sub_table_count": 1,
            "differentiating_dimension": "Employment Status"
        },
        "Table 18": {
            "sub_table_count": 1,
            "differentiating_dimension": "Income Decile Group"
        }
    },
    "measures_map": {
        "Median equivalised fuel costs (£)": "Median costs",
        "Median after housing costs (AHC), equivalised income (£)": "Median income",
        "Median Fuel Poverty Energy Efficiency Rating (FPEER)": "Median rating",
        "Median floor area (m2)": "Median floor area"
    },
    "units_map": {
        "Median equivalised fuel costs (£)": "gdp",
        "Median after housing costs (AHC), equivalised income (£)": "gdp",
        "Median Fuel Poverty Energy Efficiency Rating (FPEER)": "rating",
        "Median floor area (m2)": "m2"
    }
}
# -

# # Fuel payment type
#
# Tables 19 through 20 (the parameters, the processing will happen later on)

# +

# We're just gonna loop and use slightly different variables each time.
# If you need yo tweak anything you should be able to do it here.
fuel_payment_type_task = {
    "name": "Fuel payment type",
    "store_as": "19through20",
    "tables":
        {
        "Table 19": {
            "sub_table_count": 1,
            "differentiating_dimension": "Payment Method",
            "constant_columns": {
              "Fuel Type": "Gas"  
            }
        },
        "Table 20": {
            "sub_table_count": 1,
            "differentiating_dimension": "Payment Method",
            "constant_columns": {
              "Fuel Type": "Electricity"  
            }
        }
    },
    "measures_map": {
        "Median equivalised fuel costs (£)": "Median costs",
        "Median after housing costs (AHC), equivalised income (£)": "Median income",
        "Median Fuel Poverty Energy Efficiency Rating (FPEER)": "Median rating",
        "Median floor area (m2)": "Median floor area"
    },
    "units_map": {
        "Median equivalised fuel costs (£)": "gdp",
        "Median after housing costs (AHC), equivalised income (£)": "gdp",
        "Median Fuel Poverty Energy Efficiency Rating (FPEER)": "rating",
        "Median floor area (m2)": "m2"
    }
}

# +

trace = TransformTrace()
table_dict = {}

# do everything
# for dataset_task in [energy_efficiency_tasks, household_characteristics_tasks, household_income_tasks,fuel_payment_type_tasks]:
for category, dataset_task in {
    "Fuel Payment":fuel_payment_type_task,
    "Household Income": household_income_task,
    "Household Characteristics": household_characteristics_task,
    "Energy Efficiency": energy_efficiency_task
    }.items():

    try:
        subset_of_tabs = [x for x in tabs if x.name.strip() in dataset_task["tables"].keys()]
        for tab in subset_of_tabs:
            
            # Just specifiy the common dimensions for now
            columns = ["Year", "Measure Type", "Unit"]
            trace.start(category, tab.name, columns, distro.downloadURL)

            # there can only be one style of anchor per sheet
            is_little_table = False
            anchors = tab.filter(BIG_TABLE_ANCHOR)
            if len(anchors) == 0:
                anchors = tab.filter(LITTLE_TABLE_ANCHOR)
                is_little_table = True

            if len(anchors) == 0:
                raise Exception("Cannot find any anchor cells")

            for i, anchor in enumerate(anchors):   # i.e for each sub table on this sheet
                if is_little_table:
                    df, trace = process_little_table(anchor, dataset_task, trace)
                else:
                    df, trace = process_big_table(anchor, dataset_task, trace)
                
            # Store however many tabs we've extracted against the specified identifier
            trace.store(dataset_task["store_as"], df)
        
    except Exception as err:
        raise Exception('Error encountered while processing task "{}" from "{}".'.format(json.dumps(dataset_task["tables"][tab.name]), 
                                                                                         dataset_task["name"])) from err
# -
# # Metadata & Joins

# +
# description we'll add to most joined tables

comment = "Fuel poverty statistics report detailing Energy Efficiency and Dwelling Characteristics	 based on Median Fuel Costs, Income, FPEER Rating and Floor Area"
description = """Fuel poverty statistics report detailing Energy Efficiency and Dwelling Characteristics based on Median Fuel Costs, Income, FPEER Rating and Floor Area,
The Government is interested in the amount of energy households need to consume to have a warm, well-lit home, with hot water for everyday use, and the running of appliances. Therefore fuel poverty is measured based on required energy bills rather than actual spending. This ensures that those households who have low energy bills simply because they actively limit their use of energy at home, for example, by not heating their home are not overlooked. A methodology handbook has been published alongside this publication. This sets out the method for calculating the headline statistics using the LIHC indicator and the detailed methodology for calculating the income, energy efficiency and fuel prices for each household. It is available at:
https://www.gov.uk/government/publications/fuel-poverty-statistics-methodology-handbook
"""



# dictionary of what needs joining to what
#
# <output name> : {
#    "category": <what ever measure we're joining on",    # column name from where the data came from, we'll drop this after the joins
#    "tables": "whichever tables we're gettign the measure from"
# }
table_joins = {
    "Fuel poverty supplementary tables - Energy Efficiency and Dwelling Characteristics - Median equivalised fuel costs": {
        "category": "Median equivalised fuel costs (£)",
        "tables": "1through17",
        "comment": comment,
        "description": description
    },
    "Fuel poverty supplementary tables - Energy Efficiency and Dwelling Characteristics - Median after housing costs (AHC), equivalised income": {
        "category": "Median after housing costs (AHC), equivalised income (£)",
        "tables": "1through17",
        "comment": comment,
        "description": description
    },
    "Fuel poverty supplementary tables - Energy Efficiency and Dwelling Characteristics - Median Fuel Poverty Energy Efficiency Rating (FPEER)": {
        "category": "Median Fuel Poverty Energy Efficiency Rating (FPEER)1",
        "tables": "1through17",
        "comment": comment,
        "description": description
    },
    "Fuel poverty supplementary tables - Energy Efficiency and Dwelling Characteristics - Median floor area": {
        "category": "Median floor area (m2)",
        "tables": "1through17",
        "comment": comment,
        "description": description
    },
    "Fuel poverty supplementary tables - Housing Characteristics - Median equivalised fuel costs": {
        "category": "Median equivalised fuel costs (£)",
        "tables": "12through16",
        "comment": comment,
        "description": description
    },
    "Fuel poverty supplementary tables - Housing Characteristics - Median after housing costs (AHC), equivalised income": {
        "category": "Median after housing costs (AHC), equivalised income (£)",
        "tables": "12through16",
        "comment": comment,
        "description": description
    },
    "Fuel poverty supplementary tables - Housing Characteristics - Median Fuel Poverty Energy Efficiency Rating (FPEER)": {
        "category": "Median Fuel Poverty Energy Efficiency Rating (FPEER)1",
        "tables": "12through16",
        "comment": comment,
        "description": description
    },
    "Fuel poverty supplementary tables - Housing Characteristics - Median floor area": {
        "category": "Median floor area (m2)",
        "tables": "12through16",
        "comment": comment,
        "description": description
    },
    "Fuel poverty supplementary tables - Housing Income - Median equivalised fuel costs": {
        "category": "Median equivalised fuel costs (£)",
        "tables": "17through18",
        "comment": comment,
        "description": description
    },
    "Fuel poverty supplementary tables - Housing Income - Median after housing costs (AHC), equivalised income": {
        "category": "Median after housing costs (AHC), equivalised income (£)",
        "tables": "17through18",
        "comment": comment,
        "description": description
    },
    "Fuel poverty supplementary tables - Housing Income - Median Fuel Poverty Energy Efficiency Rating (FPEER)": {
        "category": "Median Fuel Poverty Energy Efficiency Rating (FPEER)1",
        "tables": "17through18",
        "comment": comment,
        "description": description
    },
    "Fuel poverty supplementary tables - Housing Income - Median floor area": {
        "category": "Median floor area (m2)",
        "tables": "17through18",
        "comment": comment,
        "description": description
    },
    "Fuel poverty supplementary tables - Fuel Payment Type - Median equivalised fuel costs": {
        "category": "Median equivalised fuel costs (£)",
        "tables": "19through20",
        "comment": comment,
        "description": description
    },
    "Fuel poverty supplementary tables - Fuel Payment Type - Median after housing costs (AHC), equivalised income": {
        "category": "Median after housing costs (AHC), equivalised income (£)",
        "tables": "19through20",
        "comment": comment,
        "description": description
    },
    "Fuel poverty supplementary tables - Fuel Payment Type - Median Fuel Poverty Energy Efficiency Rating (FPEER)": {
        "category": "Median Fuel Poverty Energy Efficiency Rating (FPEER)1",
        "tables": "19through20",
        "comment": comment,
        "description": description
    },
    "Fuel poverty supplementary tables - HFuel Payment Type - Median floor area": {
        "category": "Median floor area (m2)",
        "tables": "19through20",
        "comment": comment,
        "description": description
    } 
} 

# TEMP - just one to get it working
#keys = list(table_joins.keys())
#for key in keys:
#    if key != "Fuel poverty supplementary tables - Energy Efficiency and Dwelling Characteristics - Median equivalised fuel costs":
#        del table_joins[key]
    
for title, info in table_joins.items():
    
    df = trace.combine_and_trace(title, info["tables"])
    
    # slicve jsut teh bit we want using category, then drop it
    df = df[df["Category"] == info["category"]]
    df = df.drop("Category", axis=1)
    trace.Measure_Type('Drop all rows not related to: "{}".'.format(info["category"]))
    
    # Fill up the sparsity with alls
    df = df.fillna("all")
    for col in df.columns.values:
        df[df[col] == ""] = "all"
        
    # Metadata etc
    if "comment" in info.keys():
        scraper.dataset.comment = info["comment"]
        
    if "description" in info.keys():
        scraper.dataset.description = info["description"]
    
    df = df.drop_duplicates()
    cubes.add_cube(scraper, df, title)

# -
cubes.output_all()
trace.render("spec_v1.html")



