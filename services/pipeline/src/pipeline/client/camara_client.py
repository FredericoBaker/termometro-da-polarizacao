from pipeline.config.loader import get
import requests
import logging

logger = logging.getLogger(__name__)

class CamaraClient:
    def __init__(self):
        self.base_url = get("camara_api", "base_url")
        self.timeout = get("camara_api", "timeout_seconds")
        self.page_size = get("camara_api", "page_size")
        self.retries = get("camara_api", "retries")

        logger.debug(
            "Initialized CamaraClient",
            extra={
                "base_url": self.base_url,
                "timeout_seconds": self.timeout,
                "page_size": self.page_size,
                "retries": self.retries,
            },
        )

    def fetch_data(self, endpoint: str, params: dict) -> dict:
        url = f"{self.base_url}{endpoint}"
        last_error = None
        
        for attempt in range(1, self.retries + 1):
            try:
                logger.debug(
                    "Fetching data from endpoint",
                    extra={"endpoint": endpoint, "attempt": attempt, "max_retries": self.retries},
                )

                response = requests.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()

                logger.debug(
                    "Successfully fetched data",
                    extra={"endpoint": endpoint, "status_code": response.status_code},
                )

                return response.json()
            
            except requests.exceptions.Timeout as e:
                last_error = e

                logger.warning(
                    "Request timeout",
                    extra={"endpoint": endpoint, "attempt": attempt, "max_retries": self.retries},
                )

                if attempt < self.retries:
                    continue
        
        logger.error(
            "Max retries exceeded for endpoint",
            extra={"endpoint": endpoint, "max_retries": self.retries},
            exc_info=last_error,
        )

        raise last_error

    def get_parties(self, data_inicio: str, data_fim: str, page: int = 1) -> dict:
        parties_endpoint = get("camara_api", "parties_endpoint")
        params = {
            "dataInicio": data_inicio,
            "dataFim": data_fim,
            "pagina": page,
            "itens": self.page_size,
        }

        logger.info(
            "Fetching parties",
            extra={"start_date": data_inicio, "end_date": data_fim, "page": page},
        )

        return self.fetch_data(parties_endpoint, params)
    
    def get_deputies(self, data_inicio: str, data_fim: str, page: int = 1) -> dict:
        deputies_endpoint = get("camara_api", "deputies_endpoint")
        params = {
            "dataInicio": data_inicio,
            "dataFim": data_fim,
            "pagina": page,
            "itens": self.page_size,
        }

        logger.info(
            "Fetching deputies",
            extra={"start_date": data_inicio, "end_date": data_fim, "page": page},
        )

        return self.fetch_data(deputies_endpoint, params)

    def get_votings(self, data_inicio: str, data_fim: str, page: int = 1) -> dict:
        votings_endpoint = get("camara_api", "votings_endpoint")
        params = {
            "dataInicio": data_inicio,
            "dataFim": data_fim,
            "pagina": page,
            "itens": self.page_size,
        }

        logger.info(
            "Fetching votings",
            extra={"start_date": data_inicio, "end_date": data_fim, "page": page},
        )

        return self.fetch_data(votings_endpoint, params)

    def get_rollcalls(self, voting_id: int) -> dict:
        rollcalls_endpoint = get("camara_api", "rollcalls_endpoint").format(voting_id=voting_id)

        logger.info("Fetching rollcalls", extra={"voting_id": voting_id})
        
        return self.fetch_data(rollcalls_endpoint, params={})
