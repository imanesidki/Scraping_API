# Scrap_charika
This Flask app serves as an API for scraping Moroccan company data from the Charika website (https://www.charika.ma/).<br>It allows users to retrieve information about companies by sending a GET request with the company name as a parameter. <br>The app utilizes BeautifulSoup for web scraping and provides a JSON response containing details such as company name, registration number (RC), tax identification number (ICE), capital, legal status, address, phone numbers, and fax numbers. <br>The app also handles session management using JSESSIONID cookies for authentication. Additionally, it includes functionality to save and load JSESSIONID from a local file to maintain session persistence.

## To Test This App:
Run script: "python scrap_charika.py" in your python environment.<br>
Access the API: http://HOST:PORT/charika_ma.py?name=COMPANY_NAME
