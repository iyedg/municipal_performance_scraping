import pandas as pd
import requests
import requests_cache
from pyprojroot import here

requests_cache.install_cache()


def extract_performance_data(municipality_id: int, year: int) -> dict:
    endpoint_url = "http://www.collectiviteslocales.gov.tn/wp-content/themes/sahifa-child/api/api_performance.php"
    params = {"id": municipality_id, "annee": year}
    response = requests.get(endpoint_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Response status: {response.status_code}")


def extract_raw_official_names():
    return pd.read_csv(here("data/raw/municipalities_list.csv"))
