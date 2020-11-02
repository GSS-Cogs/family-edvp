# COGS Dataset Specification

[Family Home](https://gss-cogs.github.io/family-edvp/datasets/specmenu.html)

[Family Transform Status](https://gss-cogs.github.io/family-edvp/datasets/index.html)

## BEIS Fuel poverty supplementary tables 2020 

[Landing Page](https://www.gov.uk/government/statistics/fuel-poverty-supplementary-tables-2020)

[Transform Flowchart](https://gss-cogs.github.io/family-edvp/datasets/specflowcharts.html?BEIS-Fuel-poverty-supplementary-tables-2020/flowchart.ttl)

### INFO

	We are only interested in the following columns
		Median equivalised fuel costs (£)	
		Median after housing costs (AHC), equivalised income (£)	
		Median Fuel Poverty Energy Efficiency Rating (FPEER)	
		Median floor area (m2)

#### Energy Efficiency and Dwelling Characteristics

	Tables: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11
		
	Dimensions:
		Year: 2018
		FPEER (codelist): A/B/C, D, E, F, G, All
		Low Income High costs Matrix (codelist/pathify): Low Income High Costs, Low Income Low Costs, High Income High Costs, High Income Low Costs, (All households = All)
		SAP BAND (codelist): A/B/C, D, E, F, G, All	
		Rurality (codelist/pathify): Urban, Semi-rural, Rural, All
		Region (codelist): replace regions with ONS geography codes (All households will be code for England)
		Dwelling Type (codelist/pathify): Converted Flat, etc. (All Households = all) (remove superscripts)
		Dwelling Age (codelist/pathify): Pre 1919, etc. (All Households = all)
		Floor Area (codelist/pathify): Less than 50 sqm, etc. (All Households = all)
		Gas Grid Connection (codelist): Yes, No, Total (Y|N|T) (could maybe represent this through an already defined ontology)
		Main Fuel Type {Table 12 & 13} (codelist/pathify): Gas, etc. (All Households = all)
		Wall Insulation (codelist/pathify): Cavity uninsulated, etc. (All Households = all)
	Measures:
		Measure Type:  
			Median costs	
			Median income
			Median rating	
			Median floor area
		Unit: gbp, rating, m2
	Marker:
		^ number based on low sample count (between 10 and less than 30), inferences should not be made based on this figure. = low-sample-count
		* numbers hidden due to very low sample count (less than 10) within this category. = low-sample-count		
		
	Table Structure
		Year, FPEER, Low Income High costs Matrix, SAP Band, Rurality, Region, Dwelling Type, Dwelling Age, Floor Area, Gas Grid Connection, Main Fuel Type, Wall Insulation, Marker, Value

	Scraper
		Dataset-title 1: beis-fuel-poverty-supplementary-tables-2020/energycosts
		Dataset-title 2: beis-fuel-poverty-supplementary-tables-2020/energyincome
		Dataset-title 3: beis-fuel-poverty-supplementary-tables-2020/energyfpeer
		Dataset-title 4: beis-fuel-poverty-supplementary-tables-2020/energyarea
		Title 1: Fuel poverty detailed tables - Energy Efficiency and Dwelling Characteristics - Median equivalised fuel costs
		Title 2: Fuel poverty detailed tables - Energy Efficiency and Dwelling Characteristics - Median after housing costs (AHC), equivalised income
		Title 3: Fuel poverty detailed tables - Energy Efficiency and Dwelling Characteristics - Median Fuel Poverty Energy Efficiency Rating (FPEER)
		Title 4: Fuel poverty detailed tables - Energy Efficiency and Dwelling Characteristics - Median floor area
		Comment: Fuel poverty statistics report detailing Energy Efficiency and Dwelling Characteristics	 based on Median Fuel Costs, Income, FPEER Rating and Floor Area	
		Description: 
		Fuel poverty statistics report detailing Energy Efficiency and Dwelling Characteristics based on Median Fuel Costs, Income, FPEER Rating and Floor Area,
		The Government is interested in the amount of energy households need to consume to have a warm, well-lit home, with hot water for everyday use, and the running of appliances. Therefore fuel poverty is measured based on required energy bills rather than actual spending. This ensures that those households who have low energy bills simply because they actively limit their use of energy at home, for example, by not heating their home are not overlooked. A methodology handbook has been published alongside this publication. This sets out the method for calculating the headline statistics using the LIHC indicator and the detailed methodology for calculating the income, energy efficiency and fuel prices for each household. It is available at:
		https://www.gov.uk/government/publications/fuel-poverty-statistics-methodology-handbook
		Family: edv

#### Household characteristics

	Tables: 12, 13, 14, 15, 16

	Dimensions:
		Year: 2018
		Tenure (codelist/pathify): Owner occupied, etc. (All Households = all)
		Household Composition (codelist/pathify): Couple with dependent child(ren), etc. (All Households = all)
		Age of Youngest Person (codelist, combine with oldest): 0-4 etc. (All Households = all) (reformat age ranges: Y0T4). Add a not-applicable category for 'Age of Oldest' values.
		Age of Oldest Person (codelist, combine with youngest): 16-24 etc. (All Households = all) (reformat age ranges: Y16T24). Add a not-applicable category for 'Age of Youngest values.
		Ethnicity (codelist/pathify): Ethnic minority, White  (All Households = all)	
	Measures:
		Measure Type:  
			Median costs	
			Median income
			Median rating	
			Median floor area
		Unit: gbp, rating, m2
	Marker:
		^ number based on low sample count (between 10 and less than 30), inferences should not be made based on this figure. = low-sample-count
		* numbers hidden due to very low sample count (less than 10) within this category. = low-sample-count		
		
	Table Structure
		Year, Tenure, Housing Composition, Age of Youngest Person, Age of Oldest Person, Ethnicity, Marker, Value

	Scraper
		Dataset-title 1: beis-fuel-poverty-supplemantary-tables-2020/characteristicscosts
		Dataset-title 2: beis-fuel-poverty-supplemantary-tables-2020/characteristicsincome
		Dataset-title 3: beis-fuel-poverty-supplemantary-tables-2020/characteristicsrating
		Dataset-title 4: beis-fuel-poverty-supplemantary-tables-2020/characteristicsarea
		Title 1: Fuel poverty detailed tables - Energy Efficiency and Dwelling Characteristics - Median equivalised fuel costs
		Title 2: Fuel poverty detailed tables - Energy Efficiency and Dwelling Characteristics - Median after housing costs (AHC), equivalised income
		Title 3: Fuel poverty detailed tables - Energy Efficiency and Dwelling Characteristics - Median Fuel Poverty Energy Efficiency Rating (FPEER)
		Title 4: Fuel poverty detailed tables - Energy Efficiency and Dwelling Characteristics - Median floor area		Comment: Fuel poverty statistics report detailing Household characteristics based on Median Fuel Costs, Income, FPEER Rating and Floor Area
		Description:
		Fuel poverty statistics report detailing Household characteristic based on Median Fuel Costs, Income, FPEER Rating and Floor Area
		The Government is interested in the amount of energy households need to consume to have a warm, well-lit home, with hot water for everyday use, and the running of appliances. Therefore fuel poverty is measured based on required energy bills rather than actual spending. This ensures that those households who have low energy bills simply because they actively limit their use of energy at home, for example, by not heating their home are not overlooked. A methodology handbook has been published alongside this publication. This sets out the method for calculating the headline statistics using the LIHC indicator and the detailed methodology for calculating the income, energy efficiency and fuel prices for each household. It is available at:
		https://www.gov.uk/government/publications/fuel-poverty-statistics-methodology-handbook
		Family: edv

#### Household Income

	Tables: 17, 18
	
	Dimensions:
		Year: 2018
		Employment Status (codelist/pathify): Full-time work, etc. (All Households = all)	
		Income Decile Group (codelist/pathify): 1st decile - lowest income, etc. (All Households = all)
	Measures:
		Measure Type:  
			Median costs	
			Median income
			Median rating	
			Median floor area
		Unit: gbp, rating, m2
	Marker:
		^ number based on low sample count (between 10 and less than 30), inferences should not be made based on this figure. = low-sample-count
		* numbers hidden due to very low sample count (less than 10) within this category. = low-sample-count		
		
	Table Structure
		Year, Employment Status, Income Decile Group, Households in Fuel Poverty, Households not in Fuel Poverty, Marker, Value

	Scraper
		Dataset-title 1: beis-fuel-poverty-supplemantary-tables-2020/incomecosts
		Dataset-title 2: beis-fuel-poverty-supplemantary-tables-2020/incomeincome
		Dataset-title 3: beis-fuel-poverty-supplemantary-tables-2020/incomerating
		Dataset-title 4: beis-fuel-poverty-supplemantary-tables-2020/incomearea
		Title 1: Fuel poverty detailed tables - Household Income - Median equivalised fuel costs
		Title 2: Fuel poverty detailed tables - Household Income - Median after housing costs (AHC), equivalised income
		Title 3: Fuel poverty detailed tables - Household Income - Median Fuel Poverty Energy Efficiency Rating (FPEER)
		Title 4: Fuel poverty detailed tables - Household Income - Median floor area
		Comment: Fuel poverty statistics report detailing Household Income based on Median Fuel Costs, Income, FPEER Rating and Floor Area
		Description:
		Fuel poverty statistics report detailing Household Income based on Median Fuel Costs, Income, FPEER Rating and Floor Area

		The Government is interested in the amount of energy households need to consume to have a warm, well-lit home, with hot water for everyday use, and the running of appliances. Therefore fuel poverty is measured based on required energy bills rather than actual spending. This ensures that those households who have low energy bills simply because they actively limit their use of energy at home, for example, by not heating their home are not overlooked. A methodology handbook has been published alongside this publication. This sets out the method for calculating the headline statistics using the LIHC indicator and the detailed methodology for calculating the income, energy efficiency and fuel prices for each household. It is available at:
		https://www.gov.uk/government/publications/fuel-poverty-statistics-methodology-handbook
		Family: edv

#### Fuel Payment Type

	Tables: 19, 20

	Dimensions:
		Year: 2018
		Fuel Type (codelist/pathify): Gas, Electric
		Payment Method (codelist/pathify): Direct debit, etc. (All Households = all) from both table (31, 32).
	Measures:
		Measure Type:  
			Median costs	
			Median income
			Median rating	
			Median floor area
		Unit: gbp, rating, m2
	Marker:
		^ number based on low sample count (between 10 and less than 30), inferences should not be made based on this figure. = low-sample-count
		* numbers hidden due to very low sample count (less than 10) within this category. = low-sample-count		
		
	Table Structure
		Year, Fuel Type, Payment Method, Marker, Value

	Scraper
		Dataset-title 1: beis-fuel-poverty-supplemantary-tables-2020/paymentcosts
		Dataset-title 2: beis-fuel-poverty-supplemantary-tables-2020/paymentincome
		Dataset-title 3: beis-fuel-poverty-supplemantary-tables-2020/paymentrating
		Dataset-title 4: beis-fuel-poverty-supplemantary-tables-2020/paymentarea
		Title 1: Fuel poverty detailed tables - Fuel Payment Type - Median equivalised fuel costs
		Title 2: Fuel poverty detailed tables - Fuel Payment Type - Median after housing costs (AHC), equivalised income
		Title 3: Fuel poverty detailed tables - Fuel Payment Type - Median Fuel Poverty Energy Efficiency Rating (FPEER)
		Title 4: Fuel poverty detailed tables - Fuel Payment Type - Median floor area

		Comment: Fuel poverty statistics report detailing Fuel Payment Type based on Median Fuel Costs, Income, FPEER Rating and Floor Area
		Description:
		Fuel poverty statistics report detailing Fuel Payment Type based on Median Fuel Costs, Income, FPEER Rating and Floor Area
		The Government is interested in the amount of energy households need to consume to have a warm, well-lit home, with hot water for everyday use, and the running of appliances. Therefore fuel poverty is measured based on required energy bills rather than actual spending. This ensures that those households who have low energy bills simply because they actively limit their use of energy at home, for example, by not heating their home are not overlooked. A methodology handbook has been published alongside this publication. This sets out the method for calculating the headline statistics using the LIHC indicator and the detailed methodology for calculating the income, energy efficiency and fuel prices for each household. It is available at:
		https://www.gov.uk/government/publications/fuel-poverty-statistics-methodology-handbook
		Family: edv

##### Footnotes

		footnotes

##### DM Notes

		All datasets need to be split into 4 as we can't currently manage multiple measure cubes. 
		Split into:
			Median equivalised fuel costs	
			Median after housing costs (AHC), equivalised income 
			Median Fuel Poverty Energy Efficiency Rating 
			Median floor area 
		You using the CSVMapping class you need to pull in the info.json file into a dict change the Measure Type and unit and pass the dict to the Mapping class.

		Once we have multiple measures in place this data will probably be joined up with the detailed fuel poverty tables

