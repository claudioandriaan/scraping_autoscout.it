import requests
from bs4 import BeautifulSoup
import pandas as pd
import re


def get_pages(max_page):
    urls = []
    for page_number in range(1, max_page + 1):        
        url = f"https://www.autoscout24.it/lst/bmw/x2-m?atype=C&cy=I&desc=0&page={page_number}&search_id=s8yq4lkjug&sort=standard&source=listpage_pagination&ustate=N%2CU"
        urls.append(url)
    return urls

def parse_data(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    voitures = soup.find_all("article", class_="cldt-summary-full-item listing-impressions-tracking list-page-item ListItem_article__qyYw7")

    data = []

    for voiture in voitures:
        nom = ""
        price = ""
        km = ""
        adresse = ""
        garage_name = ""
        rating = ""
        ville= ""
        cp = ""
        pays = ""
        departement = ""

        try:
            nom = voiture.find("h2").text.strip()
        except AttributeError as e: 
            pass
        
        try:
            price = clean_price(voiture.find("p", class_="Price_price__APlgs PriceAndSeals_current_price__ykUpx").text.strip())
        except AttributeError as e:
            pass

        try:
            km = clean_km(voiture.find('span', class_="VehicleDetailTable_item__4n35N").text.strip())
        except AttributeError as e:
            pass
            
        try:
            adresse = voiture.find('span', class_='SellerInfo_address__leRMu').text.strip()
            # Splitting the address
            parts = adresse.split(' • ')
            if len(parts) == 2:
                ville = parts[0].strip()
                code_postal, rest = parts[1].split(' ', 1)
                pays, cp = code_postal.split('-')
                if ' - ' in rest:
                    departement = rest.split(' - ')[1].split(' ')[0]
                else:
                    departement = ''
            else:
                ville = ''
                pays = ''
                cp = ''
                departement = ''
                
        except AttributeError as e:
            adresse = ""
            ville = ""
            pays = ""
            cp = ""
            departement = ""

        try:
            dealer_name = voiture.find('span', class_='SellerInfo_name__nR9JH').text.strip()
            # Using regular expressions
            match = re.match(r'^(.*)\((\d+)\)$', dealer_name)
            if match:
                garage_name = match.group(1).strip()
                rating = int(match.group(2))
                
        except AttributeError as e:
            pass
            
        data.append({'Nom': nom, 'Price': price, 'Km': km, 'Adresse': adresse, 'Nom du Garage': garage_name, 'Rating': rating, 'Ville': ville, 'CP': cp, 'Pays': pays, 'Departement': departement})
    
    return data

def clean_price(price):
    cleaned_price = price.replace('.', '').replace(',', '').replace('-', '').strip()
    return cleaned_price

def clean_km(km):
    cleaned_km = km.replace('.', '').replace(',', '').replace('-', '').strip()
    return cleaned_km

def main():
    max_page = 5
    urls = get_pages(max_page)
    
    all_data = []

    for url in urls:        
        all_data.extend(parse_data(url))

    # Writing data to Excel
    df = pd.DataFrame(all_data)
    df.to_excel('autos.xlsx', index=False)

    print("Data saved successfully to autos.xlsx")

if __name__ == "__main__":
    main()
