# Scrap_charika
This Flask app serves as an API for retrieving Moroccan company data from the Charika website (https://www.charika.ma/).<br>It allows users to retrieve information about companies by sending a GET request with the company name as a parameter. <br>The app utilizes BeautifulSoup for web scraping and provides a JSON response containing details such as company name, registration number (RC), tax identification number (ICE), capital, legal status, address, phone numbers, and fax numbers. <br>The app also handles session management using JSESSIONID cookies for authentication. Additionally, it includes functionality to save and load JSESSIONID from a local file to maintain session persistence.

# Scrap_directinfo
This Flask app also serves as an API for retrieving Moroccan company data from the directinfo website (https://www.directinfo.ma/) based on the company name provided as a query parameter.<br>
It then returns the retrieved data in JSON format, including the company name, registration number (RC), tax identification number (ICE), capital, city, legal status, and registration date.

## Run Scripts:
Install Dependencies in your python environment: pip install flask<br>
Run script in your python environment: python scrap_charika.py<br>
Access the API in your browser: http://HOST:PORT/charika_ma.py?name=COMPANY_NAME
