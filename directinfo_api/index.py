from flask import Flask, Response, request
import requests
import json

app = Flask(__name__)

@app.route('/index.py', methods=['GET'])
def scrape_company_data():    
    if not request.args.get('name'):
        return Response(json.dumps({"status": False, "error": "Please provide a company name"}, indent=4, ensure_ascii=False), content_type='application/json; charset=utf-8')
    searchResponse = requests.get('https://www.directinfo.ma/directinfo-backend/api/queryDsl/search/' + request.args.get('name'))
    searchJson = searchResponse.json()

    companyDatabaseID = str(searchJson[0][0]['id'])

    companyResponse = requests.get('https://www.directinfo.ma/directinfo-backend/api/entreprise/' + companyDatabaseID)
    companyJson = companyResponse.json()

    data = {
        "companyName": companyJson['denomination'],
        "companyRC": companyJson['numeroRC'],
        "companyICE": companyJson['numeroICE'],
        "companyCapital": companyJson['capital'],
        "companyCity": companyJson['tribunal'],
        "companyLegalStatus": companyJson['formeJuridique'],
        "companyImmatriculation": companyJson['dateImmatriculation']
    }
    response = Response(json.dumps(data, indent=4, ensure_ascii=False), content_type='application/json; charset=utf-8')
    return response

if __name__ == '__main__':
    app.run(host='localhost', port=8001)

# Access the API: http://localhost:8000/direct_api/?name=company_name