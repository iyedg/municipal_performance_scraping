import requests
from loguru import logger


def get_performance_data(municipality_id: int, year: int) -> dict:
    endpoint_url = "http://www.collectiviteslocales.gov.tn/wp-content/themes/sahifa-child/api/api_performance.php"
    params = {"id": municipality_id, "annee": year}
    response = requests.get(endpoint_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Response status: {response.status_code}")


if __name__ == "__main__":
    logger.debug(get_performance_data(1313, 2018))
