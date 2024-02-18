from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests
import json

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_path = urlparse(self.path)
        query = parse_qs(parsed_path.query)

        name = query.get('name', [None])[0]
        if not name:
            self.respond({"status": False, "error": "Please provide a company name"}, 400)
            return

        try:
            searchResponse = requests.get(f'https://www.directinfo.ma/directinfo-backend/api/queryDsl/search/{name}')
            # get the first page of the search results
            searchJson = searchResponse.json() 
            # get the first company's database ID
            companyDatabaseID = str(searchJson[0][0]['id']) 
            # get the company's details
            companyResponse = requests.get(f'https://www.directinfo.ma/directinfo-backend/api/entreprise/{companyDatabaseID}')
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
            # send the response
            self.respond(data, 200)
        except Exception as e:
            self.respond({"status": False, "Error": str(e)}, 500)

    def respond(self, content, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        response_content = json.dumps(content, ensure_ascii=False, indent = 4).encode('utf-8')
        self.wfile.write(response_content)

