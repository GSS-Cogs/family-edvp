from gssutils import * 
import json 

info = json.load(open('info.json')) 
etl_title = info["Name"] 
etl_publisher = info["Producer"][0] 
print("Publisher: " + etl_publisher) 
print("Title: " + etl_title) 

scraper = Scraper(seed="info.json")   
scraper 

