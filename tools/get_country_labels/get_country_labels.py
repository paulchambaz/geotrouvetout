import json
import pycountry
from countryinfo import CountryInfo
from tqdm import tqdm

dict_continent_region_pays = {
    # Afrique
    "AF": {"NAF": ["DZA", "EGY", "LBY", "MAR", "SDN", "TUN", "ESH"],
           "SAF": ["AGO", "BWA", "LSO", "MWI", "MOZ", "NAM", "ZAF", "SWZ",
                   "ZWB", "ZWE"],
           "EAF": ["DJI", "ERI", "ETH", "KEN", "SOM", "TZA", "UGA"],
           "WAF": ["BEN", "BFA", "CMR", "CPV", "CIV", "GNQ", "GAB", "GMB",
                   "GHA", "GIN", "GNB", "LBR", "MLI", "MRT", "NER", "NGA",
                   "STP", "SEN", "SLE", "TGO"],
           "CAF": ["BDI", "CAF", "TCD", "COG", "RWA", "ZAR"]
           },
    # Asie (PSE = Palestine)
    "AS": {"NAS": ["MNG", "RUS"],
           "SAS": ["AFG", "BGD", "BTN", "IND", "MDV", "NPL", "PAK", "LKA"],
           "EAS": ["CHN", "JPN", "PRK", "KOR", "TWN"],
           "CAS": ["KAZ", "KGZ", "TJK", "TKM", "UZB"],
           "SEA": ["BRN", "KHM", "CXR", "CCK", "IDN", "LAO", "MYS", "MMR",
                   "PHL", "SGP", "THA", "VNM"],
           "SWA": ["ARM", "AZE", "BHR", "CYP", "GEO", "IRN", "IRQ", "ISR",
                   "JOR", "KWT", "LBN", "OMN", "PSE", "QAT", "SAU", "SYR",
                   "TUR", "ARE", "YEM"],
           },
    # Europe (SJM = Svalbard et Jan Mayen, GGY = Guernsey,
    # JEY = Jersey, IMN = iles de Man,
    # SCG = Serbia et Montenegro)
    "EU": {"NEU": ["DNK", "FRO", "FIN", "ISL", "NOR", "SJM", "SWE"],
           "SEU": ["VAT", "ITA", "MLT", "SMR"],
           "EEU": ["BLR", "EST", "LVA", "LTU", "MDA", "POL", "UKR"],
           "WEU": ["BEL", "FRA", "DEU", "GGY", "IRL", "JEY", "LUX", "IMN",
                   "MCO", "NLD", "GBR"],
           "CEU": ["AUT", "CZE", "HUN", "LIE", "SVK", "CHE"],
           "SEE": ["ALB", "BIH", "BGR", "HRV", "GRC", "MKD", "ROM", "SCG",
                   "SVN"],
           "SWE": ["AND", "GIB", "PRT", "ESP"]
           },
    # America
    "AM": {"NAM": ["CAN", "GRL", "SPM", "USA"],
           "SAM": ["ARG", "BOL", "BRA", "CHL", "COL", "ECU", "FLK", "GUF",
                   "GUY", "PRY", "PER", "SUR", "URY", "VEN"],
           "CAM": ["BLZ", "CRI", "SLV", "GTM", "HND", "MEX", "NIC", "PAN"],
           "WIN": ["AIA", "ATG", "ABW", "BHS", "BRB", "BMU", "VGB", "CYM",
                   "CUB", "DMA", "DOM", "GRD", "GLP", "HTI", "JAM", "MTQ",
                   "MSR", "ANT", "PRI", "KNA", "LCA", "VCT", "TTO", "TCA",
                   "VIR"]
           },
    # Oceanie
    "OC": {"PAC": ["ASM", "AUS", "COK", "FJI", "PYF", "GUM", "KIR", "MHL",
                   "FSM", "NRU", "NCL", "NZL", "NIU", "NFK", "MNP", "PLW",
                   "PNG", "PCN", "SLB", "TKL", "TON", "TUV", "VUT", "WLF",
                   "WSM"]}
}


# Get a list of all country codes
countries = list(pycountry.countries)

country_metadatas = {}
for country in countries:
    country_code = country.alpha_3
    continent, zone = None, None
    for cont, zones in dict_continent_region_pays.items():
        for zn, countries in zones.items():
            if country_code in countries:
                continent, zone = cont, zn
                break
        if continent is not None:
            break

    if continent is None or zone is None:
        continue

    try:
        country_info = CountryInfo(country.alpha_2)
        languages = country_info.languages()
    except KeyError:
        # handle error when country code is not valid
        continue

    languages = [lang.upper() for lang in languages]

    country_dict = {
        "continent": continent,
        "zone": zone,
        "languages": languages
    }
    country_metadatas[country_code] = country_dict


# Write out the JSON file
with open('country_metadata.json', 'w') as file:
    json.dump(country_metadatas, file, indent=2)
