# COGS Dataset Specification


## BEIS RHI monthly deployment data   Month Year   Annual edition 

[Landing Page](https://www.gov.uk/government/collections/renewable-heat-incentive-statistics)

[Transform Flowchart](https://gss-cogs.github.io/family-EDVP/datasets/specflowcharts.html?BEIS-RHI-monthly-deployment-data-Month-Year-Annual-edition/flowchart.ttl)

## The following tables will result in 2 datasets being output one for application numbers and one for capacity in MW

### Sheet: 1.1 Number of applications and total capacity by technology type, Great Britain, November 2011 to February 2021

	2 dimensions in dataset to be split out into 2 datasets after joining with other tables: 
		Applications: Columns B, G, L, Q
		Capacity MW: Columns D, I, N, T

	Skip percentage columns

	Dimensions
		Period: from title (November 2011 to February 2021), convert to suitable format
		Column A: Technology Type (A7:A18) {Codelist, might already be one for this as it follows Ofgem tariff bands}
		Row 5: Application Type (B5:T5) {Codelist}

	Add Dimensions
		Geography with code for Great Britain
		Application Status with value "all"
		SIC with value "total"
		Measure Type with values "applications" and "mw"

	Footnotes
		footnote 1 needs to be added to the codelist definition json file
		
### Sheet: 1.2 Application status, Great Britain, November 2011 to February 2021

	Skip percentage columns

	Dimensions
		Period: from title (November 2011 to February 2021), convert to suitable format
		Column A: Application Type (A7:A12) {Codelist}
		Row 5: Application Type (B5:T5) {Codelist}

	Add Dimensions
		Technology Type with value "total""
		Geography with code for Great Britain
		SIC with value "total"
		Measure Type with values "applications"

### Sheet: 1.3 Number of applications and capacity by region, Great Britain, November 2011 to February 2021

	2 dimensions in dataset to be split out into 2 datasets after joining with other tables: 
		Applications: Columns C, F
		Capacity MW: Columns I, L

	Skip percentage columns

	Dimensions
		Period: from title (November 2011 to February 2021), convert to suitable format
		Column A: Geography (A7:A18), ignore Region column {Geography codelist already in use}
		Row 5: Application Type (C5:L5) {Codelist}

	Add Dimensions
		Technology Type with value "total"
		Application Status with value "all"
		SIC with value "total"
		Measure Type with values "applications" and "mw"

### Sheet 1.4 Number of accredited applications and installed capacity by local authority, Great Britain, November 2011 to February 2021

	2 dimensions in dataset to be split out into 2 datasets after joining with other tables: 
		Applications: Columns E
		Capacity MW: Columns F

	Skip percentage columns

	Dimensions
		Period: from title (November 2011 to February 2021), convert to suitable format
		Column A: Geography (A7:A420), ignore area name column {Geography codelist already in use}
		Row 5: Application Type (C5:L5) {Codelist}

	Add Dimensions
		Technology Type with value "total"
		Application Status with value "all"
		SIC with value "total"
		Measure Type with values "applications" and "mw"
	
### Sheet 1.6 Number of tariff guarantee applications by tariff band, Great Britain, at end-February 2021

	2 dimensions in dataset to be split out into 2 datasets after joining with other tables: 
		Applications: Columns B, H, N, T
		Capacity MW: Columns E, K, Q, W
		
	Skip percentage columns

	Dimensions
		Period: from title (November 2011 to February 2021), convert to suitable format
		Column A: Technology Type (Change from Tariff band) (A10:A16) {Codelist}
		Row 8: Application Type (B8:W8)

	Add Dimensions
		Application Status with value "all"
		SIC with value "total"
		Measure Type with values "applications" and "mw"

	GUIDANCE NOTES UNDER THE TITLE NEED TO BE ADDED TO DESCRIPTION

### Sheet M1.1 Number of full applications, number of accredited full applications, and installed capacity per month, Great Britain, November 2011 to February 2021

	2 dimensions in dataset to be split out into 2 datasets after joining with other tables: 
		Applications: Columns D, H
		Capacity MW: Columns F, J
				
	Skip cumulative columns

	Dimensions
		Column A & B: Period: convert year and month to suitable format (month/yyyy-mm)
		Row 5: Application Type (D5:J5) {codelist} has added (by date of first submission) keep for now

	Add Dimensions
		Application Status with value "all"
		SIC with value "total"
		Technology Type with value "total"
		Geography with code for Great Britain
		Measure Type with values "applications" and "mw"

### Sheet M1.2 - Number of full applications (by date of first submission), by technology, per month, Great Britain, November 2011 to February 2021
			
	Dimensions
		Column A & B: Period: convert year and month to suitable format (month/yyyy-mm)
		Row 5: Technology Type (D5:O5) {codelist} 

	Add Dimensions
		Application Status with value "all"
		SIC with value "total"
		Application Type with value "Number of full applications (by date of first submission)"
		Geography with code for Great Britain
		Measure Type with values "applications"

### Sheet M1.3 - Capacity of full applications (MW) (by date of first submission), by technology, per month, Great Britain, November 2011 to February 2021

	Dimensions
		Column A & B: Period: convert year and month to suitable format (month/yyyy-mm)
		Row 5: Technology Type (D5:O5) {codelist}

	Add Dimensions
		Application Status with value "all"
		SIC with value "total"
		Application Type with value " Capacity of full applications (MW) (by date of first submission)"
		Geography with code for Great Britain
		Measure Type with values "mw"

### Sheet M1.4 - Number of TG applications (by date of first submission), by technology, per month, Great Britain, November 2011 to February 2021

	Dimensions
		Column A & B: Period: convert year and month to suitable format (month/yyyy-mm)
		Row 5: Technology Type (D5:J5) {codelist} has added (by date of first submission) keep for now

	Add Dimensions
		Application Status with value "all"
		SIC with value "total"
		Application Type with value "Number of Tariff Guarantee Applications"
		Geography with code for Great Britain
		Measure Type with values "applications"

### Sheet Q1.1 - Number of full applications, number of accreditations, and installed capacity per quarter¹ Great Britain, November 2011 to December 2020
			
	2 dimensions in dataset to be split out into 2 datasets after joining with other tables: 
		Applications: Columns D, H
		Capacity MW: Columns F, J
				
	Skip cumulative columns

	Dimensions
		Column A & B: Period: convert year and quarter to suitable format (quarter/yyyy-Qq)
		Row 5: Application Type (D5:J5) {codelist} has added (by date of first submission) keep for now

	Add Dimensions
		Application Status with value "all"
		SIC with value "total"
		Technology Type with value "total"
		Geography with code for Great Britain
		Measure Type with values "applications" and "mw"


## Joined Dataset 1 & 2

	Join all tables detailed above, 1.1, 1.2, 1.3, 1.4, 1.6, M1.1, M1.2, M1.3, M1.4, Q1.1

	Add Dimension:
		Household Type with value "non-domestic"
		
	Then split into 2 datasets by Measure Type: applications & MW

	Applications Dataset
	Scraper
	Title:
		RHI deployment data - Application Numbers
	Comment:
		Application statistics for the Renewable Heat Incentive (RHI) programme
	Description:
		Application statistics for the Renewable Heat Incentive (RHI) programme on technology type, region, local authority

	MW Dataset
	Scraper
	Title:
		RHI deployment data - Capacity (MW)
	Comment:
		Capacity (MW) statistics for the Renewable Heat Incentive (RHI) programme
	Description:
		Capacity (MW) statistics for the Renewable Heat Incentive (RHI) programme on technology type, region, local authority  
		ALL FOOTNOTES TO BE ADDED TO DESCRIPTION but some wording will have to be altered


	Wordings in some dimensions will have to be changed but will figure that out when we can see the output
	Footnotes need to be altered to suit

----------------------------------------------------

# Sheet 1.7 Number and capacity of accredited installations and heat generated by Standard Industrial Classification Code (SIC), Great Britain, November 2011 to February 2021

	3 dimensions in dataset : 
		Installations: Column C 
		Capacity MW: Column E
		Heat paid for GWh: Column G

	Marker
		Replace any # values with empty string and put suppressed in Marker column
		
	Skip percentage columns

	Dimensions
		Period: from title (November 2011 to February 2021), convert to suitable format
		Column A: SIC Code (A7:A95) {SIC Codelist} probably not a code for total so might have to leave out
		Row 5: Installation Type (C5:G5)

	Add Dimensions
		Measure Type with values "installations"
		
	SIC CODES WEB ADDRESS FOR SIC CODES IN FOOTNOTES







### Sheet 1.5

	Heat generated and paid for by technology, Great Britain, November 2011 to February 2021

	Skip percentage columns

	Dimensions
		Period: from title (November 2011 to February 2021), convert to suitable format
		Column A: Technology Type (A7:A18) {Codelist, might already be one for this as it follows Ofgem tariff bands}

	Footnotes
		All footnotes need to be added to scraper description

	Measure Type: generated-heat
	Unit: kWh

	Scraper:
		Title: 
			RHI deployment data - Heat generated and paid for by technology, Great Britain
		Comment:
			Statistics for the Renewable Heat Incentive (RHI) programme. Heat generated and paid for by technology, Great Britain
		Description
			Statistics for the Renewable Heat Incentive (RHI) programme. Heat generated and paid for by technology, Great Britain
			These statistics provide an update on the uptake of both the non-domestic and domestic Renewable Heat Incentive (RHI) schemes
			PLUS FOOTNOTES


			

##### DM Notes

		notes

