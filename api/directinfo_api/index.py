from fastapi import FastAPI, Response, HTTPException, Request
import requests
import json

app = FastAPI()

@app.get('/api/directinfo_api/index.py')
async def scrape_company_data(name: str):
    if not name:
        raise HTTPException(status_code=400, detail="Please provide a company name")
        
    search_response = requests.get(f'https://www.directinfo.ma/directinfo-backend/api/queryDsl/search/{name}')
    search_json = search_response.json()

    company_database_id = str(search_json[0][0]['id'])

    company_response = requests.get(f'https://www.directinfo.ma/directinfo-backend/api/entreprise/{company_database_id}')
    company_json = company_response.json()

    data = {
        "companyName": company_json['denomination'],
        "companyRC": company_json['numeroRC'],
        "companyICE": company_json['numeroICE'],
        "companyCapital": company_json['capital'],
        "companyCity": company_json['tribunal'],
        "companyLegalStatus": company_json['formeJuridique'],
        "companyImmatriculation": company_json['dateImmatriculation']
    }
    return data
