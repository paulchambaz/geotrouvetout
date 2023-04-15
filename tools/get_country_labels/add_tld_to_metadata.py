import json
import pycountry
from countryinfo import CountryInfo

# Load the JSON files
with open('country_metadata.json', 'r') as file:
    country_metadata = json.load(file)
    
with open('country_tld_domain.json', 'r') as file:
    country_tld_domains = json.load(file)

# Create a dictionary converting country names to alpha2 codes
country_name_to_code = {}
for country in pycountry.countries:
    country_name_to_code[country.name] = country.alpha_3

# Add the TLDs to the dictionary
for country_tld in country_tld_domains:
    country_name = country_tld['country']
    tld = country_tld['tld']

    if country_name in country_name_to_code:
        country_code = country_name_to_code[country_name]
        if country_code in country_metadata:
            country_metadata[country_code]['tld'] = tld

# Update the country_metadata.json file
with open('country_metadata.json', 'w') as file:
    json.dump(country_metadata, file, indent=2)