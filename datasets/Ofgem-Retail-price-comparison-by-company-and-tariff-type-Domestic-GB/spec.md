# COGS Dataset Specification

[Family Transform Status](https://gss-cogs.github.io/family-EDVP/datasets/index.html)

## Ofgem Retail price comparison by company and tariff type  Domestic  GB 

[Landing Page](https://www.ofgem.gov.uk/data-portal/all-charts)

#### Sheet: Retail price comparison by company and tariff

	Dimensions:
		Dimension_1: rename as Tariff and pathify
		Remove empty Value rows for "Default tariff cap level" as it was not introduced until Oct 2020
		Remove marker column

	Measures:
		Measure Type: tariff
		Unit: gbp 

	Scraper:
		dataset_path: (should be ok as is)
		Title: (should be ok as it)
		Comment: 
		This data shows trends in domestic energy bills by tariff offered by the six largest suppliers and all other suppliers.
		Description:
		This data shows trends in domestic energy bills by tariff offered by the six largest suppliers and all other suppliers. It compares their average standard variable tariffs with the default tariff cap and the cheapest tariffs available in the market (including white label tariffs). Figures are based on a typical domestic dual fuel customer paying by direct debit.
		Relevance and further information
		Tariff differentials reflect pricing in different market segments, as well as how much other suppliers are able to compete on price with the large legacy suppliers. See definition of supplier groups:
		https://www.ofgem.gov.uk/chart/gas-supply-market-shares-company-domestic-gb
		Methodology
		We calculate the bill values associated with the different tariff types using a ‘typical medium domestic consumer’. As of April 2020, typical domestic consumption values (TDCV) for a medium consumer are 12,000kWh/year for gas and 2,900kWh/year for electricity (profile class 1). The previous typical domestic consumption values (TDCV), that came into effect as of October 2017, were 12,000kWh/year for gas and 3,100kWh/year for electricity (profile class 1). The data includes collective switching tariffs from Q1 2016. All tariffs shown in the chart are for a dual fuel, direct debit customer. Dual fuel refers to a situation where a customer takes gas and electricity from the same supplier.
		A standard variable tariff refers to a supply contract which is for a period of an indefinite length and which does not contain a fixed term period that applies to any of the terms and conditions. It’s an energy supplier’s basic offer. If a customer does not chose a specific energy plan, for example after their fixed tariff ends, they will be moved on a standard variable tariff until they have chosen a new one. A customer can also make an active choice to select a standard variable tariff.
		Tariffs with limited availability depending on customer features (for example, tariffs which are only available to new customers, also known as ‘acquisition’ tariffs, or tariffs restricted to certain regions) are excluded from the calculation to make sure that all tariffs considered are generally available to all customers across GB.
		Tariffs available with white label suppliers are included in the calculation of the cheapest tariffs. White label suppliers are organisations without supply licenses that partner with an active licensed supplier to offer gas and electricity using their own brand.
		To calculate the average of the cheapest tariffs from the 10 cheapest suppliers we took the cheapest tariff offered by each supplier in the market (i.e. one tariff per supplier) and then ranked the tariffs in order of price. We then took the simple average of the 10 cheapest tariffs in this list. This method is to ensure a cross section of suppliers is included in the calculation.
		The Default tariff cap level only came into effect from 1 October 2020.

#### Table Structure

		Period, Tariff, Value

##### DM Notes

		Codelist has been created and info.json updated with column references

