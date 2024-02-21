from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import json
from api.utils_charika import requests, get_jsessionid, scrape_company_data

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_path = urlparse(self.path)
        query = parse_qs(parsed_path.query)

        name = query.get('name', [None])[0]
        provider = query.get('provider', [None])[0]

        if not name or not provider:
            self.respond({"status": False, "error": "Please provide both a company name and a provider"}, 400)
            return

        if provider == "charika":
            data = self.handle_charika(name)
        elif provider == "directinfo":
            data = self.handle_directinfo(name)
        else:
            self.respond({"status": False, "error": "Invalid provider. Choose 'charika' or 'directinfo'."}, 400)
            return

        if data:
            self.respond(data, 200)
        else:
            self.respond({"status": False, "error": "No result found"}, 500)


    def respond(self, content, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        response_content = json.dumps(content, ensure_ascii=False, indent=4).encode('utf-8')
        self.wfile.write(response_content)


    def handle_charika(self, name):
        base_url = 'https://www.charika.ma/'
        bot_account_email = 'losag12404@fahih.com'
        bot_account_password = 'losag12404@fahih.com'
        jsessionid = get_jsessionid(base_url, bot_account_email, bot_account_password)
        if not jsessionid:
            return None        
        data = scrape_company_data(base_url, name, "", jsessionid)
        if data:
            return data
        return None


    def handle_directinfo(self, name):
        try:
            searchResponse = requests.get(f'https://www.directinfo.ma/directinfo-backend/api/queryDsl/search/{name}', timeout=20)
            # get the first page of the search results
            searchJson = searchResponse.json() 
            # get the first company's database ID
            companyDatabaseID = str(searchJson[0][0]['id']) 
            # get the company's details
            companyResponse = requests.get(f'https://www.directinfo.ma/directinfo-backend/api/entreprise/{companyDatabaseID}', timeout=20)
            companyJson = companyResponse.json()
            # prepare the response
            data = {
                "companyName": companyJson['denomination'],
                "companyRC": companyJson['numeroRC'],
                "companyICE": companyJson['numeroICE'],
                "companyCapital": companyJson['capital'],
                "companyCity": companyJson['tribunal'],
                "companyLegalStatus": companyJson['formeJuridique'],
                "companyImmatriculation": companyJson['dateImmatriculation']
            }
            return data
        except Exception as e:
            return None



# # To test on localhost
# def run(server_class=HTTPServer, handler_class=handler, port=8080):
#     server_address = ('', port)
#     httpd = server_class(server_address, handler_class)
#     print(f'Starting server on port {port}...')
#     httpd.serve_forever()

# if __name__ == '__main__':
#     run()
