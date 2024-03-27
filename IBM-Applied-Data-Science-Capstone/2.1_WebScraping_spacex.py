import requests 
from bs4 import BeautifulSoup
import re
import unicodedata
import pandas as pd


# function which are used
def extract_column(element):
    if (element.br):
        element.br.extract()
    if element.a:
        element.a.extract()
    if element.sup:
        element.sup.extract()
    colunm_name = " ".join(element.contents)
    if not(colunm_name.strip().isdigit()):
        colunm_name = colunm_name.strip()
        return colunm_name

def date_time(table_cells):
    """
    This function returns the data and time from the HTML  table cell
    Input: the  element of a table data cell extracts extra row
    """
    return [data_time.strip() for data_time in list(table_cells.strings)][0:2]

def booster_version(table_cells):
    """
    This function returns the booster version from the HTML  table cell 
    Input: the  element of a table data cell extracts extra row
    """
    out=''.join([booster_version for i,booster_version in enumerate( table_cells.strings) if i%2==0][0:-1])
    return out

def landing_status(table_cells):
    """
    This function returns the landing status from the HTML table cell 
    Input: the  element of a table data cell extracts extra row
    """
    out=[i for i in table_cells.strings][0]
    return out


def get_mass(table_cells):
    mass=unicodedata.normalize("NFKD", table_cells.text).strip()
    if mass:
        mass.find("kg")
        new_mass=mass[0:mass.find("kg")+2]
    else:
        new_mass=0
    return new_mass


url = "https://en.wikipedia.org/wiki/List_of_Falcon_9_and_Falcon_Heavy_launches_(2010%E2%80%932019)"
headers = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'

html = requests.get(url)
print(html.status_code)

soup = BeautifulSoup(html.text, "html5lib")

table = soup.find_all('table')
first_launch_table = table[1]

# Getting Headers
column_names = []

for element in first_launch_table.find_all('th'):
    name = extract_column(element)
    if name is not None and len(name) > 0:
        column_names.append(name)


# getting rows data
launch_dict = dict.fromkeys(column_names)

# remove an irrelvant column
del launch_dict['Date and time ( )']

# let's initial the launch_dict with each value to be an empty list
launch_dict['Flight No.'] = []
launch_dict['Launch site'] = []
launch_dict['Payload'] = []
launch_dict['Payload mass'] = []
launch_dict['Orbit'] = []
launch_dict['Customer'] = []
launch_dict['Launch outcome'] = []

# added some new columns
launch_dict['Version Booster'] = []
launch_dict['Booster landing'] = []
launch_dict['Date'] = []
launch_dict['Time'] = []

extracted_row = 0
tables = soup.find_all('table', class_="wikitable plainrowheaders collapsible")
for table_number, table in enumerate(tables):
    for rows in table.find_all('tr'):
        if rows.th:
            if rows.th.string:
                flight_number = rows.th.string.strip()
                flag = flight_number.isdigit()
            else:
                flag=False
            row = rows.find_all('td')
            if flag:
                extracted_row += 1
                #print(flight_number)
                launch_dict['Flight No.'].append(flight_number)
                
                # extract data and time
                datatimelist = date_time(row[0])
                #print(datatimelist)
                # data value
                date = datatimelist[0].strip(',')
                #print(date)
                launch_dict['Date'].append(date)

                # time value
                time = datatimelist[1].strip(',')
                #print(time)
                launch_dict['Time'].append(time)

                # booster version
                bv = booster_version(row[1])
                if not(bv):
                    bv = row[1].a.string
                #print(bv)
                launch_dict['Version Booster'].append(bv)

                # launch site
                launch_site = row[2].a.string
                #print(launch_site)
                launch_dict['Launch site'].append(launch_site)

                # payload
                payload = row[3].a.string
                #print(payload)
                launch_dict['Payload'].append(payload)

                # payload mass
                payload_mass = get_mass(row[4])
                # print(payload_mass)
                launch_dict['Payload mass'].append(payload_mass)

                # orbit
                orbit = row[5].a.string
                #print(orbit)
                launch_dict['Orbit'].append(orbit)

                # customer
                try:
                    customer = row[6].a.string
                except:
                    customer = "Various"
                # print(customer)
                launch_dict['Customer'].append(customer)
                    
                # launch outcome
                launch_outcome = list(row[7].strings)[0]
                #print(launch_outcome)
                launch_dict['Launch outcome'].append(launch_outcome)

                # booster landing
                booster_landing = landing_status(row[8])
                #print(booster_landing)
                launch_dict['Booster landing'].append(booster_landing)

df = pd.DataFrame(launch_dict)
df.to_csv('spacex_web_scraping.csv', index=False)