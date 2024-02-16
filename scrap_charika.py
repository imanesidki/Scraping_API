from flask import Flask, Response, request
from bs4 import BeautifulSoup
import requests
import json
import time
import pickle
import os
import re

base_url = 'https://www.charika.ma/' # Website url to scrap data from
bot_account_email = 'losag12404@fahih.com' # Bot account email
bot_account_password = 'losag12404@fahih.com' # Bot account password
cookie_path = 'jsessionid.pkl' # Path to save JSESSIONID

app = Flask(__name__)

# Save JSESSIONID to a local file
def save_cookie(jsessionid):
    with open(cookie_path, 'wb') as f:
        pickle.dump({'jsessionid': jsessionid, 'timestamp': time.time()}, f)

# Load JSESSIONID from the local file
def load_cookie():
    if os.path.exists(cookie_path):
        with open(cookie_path, 'rb') as f:
            return pickle.load(f)
    return None

# Check if the saved JSESSIONID is still valid
def is_cookie_valid(cookie_data):
    if cookie_data:
        # Check if the cookie is still valid (30 minutes)
        elapsed_time = time.time() - cookie_data['timestamp']
        return elapsed_time < 1800, cookie_data['jsessionid']
    return False, None

# Get or refresh JSESSIONID
def get_jsessionid():
    cookie_data = load_cookie()
    valid, jsessionid = is_cookie_valid(cookie_data)
    if valid:
        return jsessionid
    
    # Send a POST request to the login endpoint
    login_endpoint = f'{base_url}/user-login'
    payload = f"username={bot_account_email}&password={bot_account_password}"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    }
    response = requests.post(login_endpoint, headers=headers, data=payload)
    # Save the JSESSIONID
    jsessionid = response.cookies.get('JSESSIONID')
    save_cookie(jsessionid)
    return jsessionid

# Scrape company data
@app.route('/charika_ma.py', methods=['GET'])
def scrape_company_data():
    # Get the JSESSIONID
    jsessionid = get_jsessionid()
    search_url = f'{base_url}/societe-rechercher'
    # Prepare the form data
    form_data = {
        'sDenomination': request.args.get('name'),
        'sRegion': '',
        'sActivite': ''
    }
    # Send a POST request to the search endpoint
    cookies = {'JSESSIONID': jsessionid}
    response = requests.post(search_url, data=form_data, cookies=cookies, allow_redirects=True)

    # Parse the response content
    soup = BeautifulSoup(response.content, 'html.parser')
    # Check if there are any results
    results = soup.find_all('h5', class_='strong text-lowercase truncate')
    if not results:
        return Response(json.dumps({"status": False, "error": "No results found"}, indent=4, ensure_ascii=False), content_type='application/json; charset=utf-8')
        
    # Get the first result (company page link)
    first_result = results[0].find('a', class_='goto-fiche')
    company_id = first_result.get('href') if first_result else ""
    
    # Send a GET request to the company page
    company_url = f'{base_url}/{company_id}'
    response = requests.get(company_url, cookies=cookies)
    soup = BeautifulSoup(response.content, 'html.parser')

    # helper function to get sibling text
    def get_sibling_text(element, keyword):
        # Find the target element
        target = soup.find(lambda tag: tag.name == "td" and keyword in tag.get_text())
        return target.find_next_sibling("td").get_text().strip() if target else None

    # Parsing companyRC having the initial format: [companyRC] (Tribunal de [companyCity])
    companyRCCity = get_sibling_text(soup, "RC").replace("Tribunal de ", "")
    # Extract companyRC using Regex expression
    companyRC = re.search(r'(\d+)', companyRCCity)
    # Extract companyCity using Regex expression
    companyCity = re.search(r'\((.*?)\)', companyRCCity)

    # Extract company data
    data = {
        "companyName": soup.find("h1", class_="nom").get_text(strip=True) if soup.find("h1", class_="nom") else None,
        "companyRC": companyRC.group(0) if companyRC else None,
        "companyICE": get_sibling_text(soup, "ICE"),
        "companyCapital": int(re.sub(r'\D', '', get_sibling_text(soup, "Capital"))),
        "companyCity": companyCity.group(1) if companyCity else None,
        "companyLegalStatus": get_sibling_text(soup, "Forme juridique"),
        "companyAddress": soup.find("div", class_="ligne-tfmw").find("label").get_text(strip=True) if soup.find("div", class_="ligne-tfmw") and soup.find("div", class_="ligne-tfmw").find("label") else None,
        "companypPhone": [tel.get_text(strip=True) for tel in soup.select(".marketingInfoTelFax")],
        "companyFax": soup.select_one("div.row.ligne-tfmw:nth-of-type(2) .marketingInfoTelFax").get_text(strip=True) if soup.select_one("div.row.ligne-tfmw:nth-of-type(2) .marketingInfoTelFax") else None,
    }

    # Return the data as a JSON response
    return Response(json.dumps(data, indent=4, ensure_ascii=False), content_type='application/json; charset=utf-8')

if __name__ == "__main__":
    # Run the Flask app
    app.run(host='localhost', port=8000)

# Run script: python scrap_charika.py
# Access the API: http://localhost:8000/charika_ma.py?name=company_name
