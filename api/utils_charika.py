from bs4 import BeautifulSoup
import requests
import re

def get_jsessionid(base_url, bot_account_email, bot_account_password):
    # Attempt to login and get JSESSIONID
    login_endpoint = f'{base_url}/user-login'
    payload = f"username={bot_account_email}&password={bot_account_password}"
    headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
    response = requests.post(login_endpoint, headers=headers, data=payload, timeout=20)
    if response.status_code == 200:
        return response.cookies.get('JSESSIONID')
    return None


# Scrape company data
def scrape_company_data(base_url, name, region, jsessionid):
    search_url = f'{base_url}/societe-rechercher'
    form_data = {'sDenomination': name, 'sRegion': region, 'sActivite': ''}
    cookies = {'JSESSIONID': jsessionid}
    response = requests.post(search_url, data=form_data, cookies=cookies, allow_redirects=True, timeout=20)
    if not response.ok:
        return None
    soup = BeautifulSoup(response.content, 'html.parser')
    results = soup.find_all('h5', class_='strong text-lowercase truncate')
    if not results:
        return None
    company_id = None
    company_name = None
    # Iterate through all results to find a matching company name
    for result in results:
        a_tag = result.find('a', class_='goto-fiche')
        if a_tag:
            company_name = a_tag.text.strip().lower()
            # Compare the company name from the result with the one we're looking for
            if company_name == name.lower():
                company_id = a_tag.get('href')
                break
    if (company_id is None):  # This if corresponds to the for loop, executed only if no break occurs
        a_tag = results[0].find('a', class_='goto-fiche')
        company_id = a_tag.get('href') if a_tag else ""
    company_url = f'{base_url}/{company_id}'
    response = requests.get(company_url, cookies=cookies, timeout=20)
    if not response or response.status_code != 200:
        return None
    html_content = response.content
    if not html_content:
        return None
    data = parse_company_data(html_content)
    return data


def parse_company_data(html_content):
    if not html_content:
        return None
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Helper function to get sibling text
    def get_sibling_text(keyword):
        target = soup.find(lambda tag: tag.name == "td" and keyword in tag.get_text())
        return target.find_next_sibling("td").get_text().strip() if target else None

    # Extracting company data
    company_name = soup.find("h1", class_="nom").get_text(strip=True) if soup.find("h1", class_="nom") else None

    # Parsing companyRC and companyCity from a combined field if necessary
    company_rc_city_raw = get_sibling_text("RC")
    company_rc = None
    company_city = None
    if company_rc_city_raw:
        rc_city_match = re.search(r'(\d+).*?\((.*?)\)', company_rc_city_raw)
        if rc_city_match:
            company_rc = rc_city_match.group(1)
            company_city = rc_city_match.group(2)

    company_ice = get_sibling_text("ICE")
    company_capital_raw = get_sibling_text("Capital")
    company_capital = int(re.sub(r'\D', '', company_capital_raw)) if company_capital_raw else None
    company_legal_status = get_sibling_text("Forme juridique")
    company_address = soup.find("div", class_="ligne-tfmw").find("label").get_text(strip=True) if soup.find("div", class_="ligne-tfmw") and soup.find("div", class_="ligne-tfmw").find("label") else None

    # Extracting phone numbers, assuming they are in a list
    phone_numbers = [tel.get_text(strip=True) for tel in soup.select(".marketingInfoTelFax")]

    # Assuming the first number is the phone and the second is the fax, if present
    company_phone = phone_numbers[0] if phone_numbers else None
    company_fax = phone_numbers[1] if len(phone_numbers) > 1 else None

    # Constructing the data dictionary
    data = {
        "companyName": company_name,
        "companyRC": company_rc,
        "companyICE": company_ice,
        "companyCapital": company_capital,
        "companyCity": company_city,
        "companyLegalStatus": company_legal_status,
        "companyAddress": company_address,
        "companyPhone": company_phone,
        "companyFax": company_fax,
    }

    return data
