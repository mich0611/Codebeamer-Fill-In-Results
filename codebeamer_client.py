''''
Codebeamer Client
'''
import requests
import logging
from requests import Response
from requests.auth import HTTPBasicAuth

def setup_logger(name: str,
                 level: int = logging.INFO,
                 to_file: bool = True,
                 filepath: str = 'app.log') -> logging.Logger:
    """
    建立並回傳一個預設格式的 logger。
    Args:
        name (str): logger name
        level (int): logging level, ex: logging.INFO、logging.DEBUG
        to_file (bool): output to file
        filepath (str): log path

    Returns:
        logging.Logger
    """

    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter(
        '[%(asctime)s][%(levelname)s][%(name)s] %(message)s',
        '%Y-%m-%d %H:%M:%S'
    )

    # 避免重複加 handler
    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler (optional)
        if to_file:
            file_handler = logging.FileHandler(filepath)
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
    return logger

# your codebeamer URL. ex: https://alm.<company_name>.com/cb/api/v3/
CODEBEAMER_URL = ''
LOGGER = setup_logger("CB-logger", filepath = "CBM.log")

def sap_api_gateway_response_handler(response: Response):
    if not isinstance(response, Response):
        error_msg = f"Response Type: {type(response)}. Input is not a type of Response."
        LOGGER.error(error_msg)
        raise TypeError(error_msg)

    response_status_code = response.status_code
    if response_status_code == 200:
        try:
            response.json()         # SAP API response body must be a valid json.
        except Exception as error:
            error_msg = f"Response: {response.url}. SAP API response body must be a valid json."
            LOGGER.error(error_msg)
            raise ConnectionResetError(error_msg) from error
    else:
        error_msg = f"Response: {response.url} {response_status_code} fail, {response.reason}"
        LOGGER.error(error_msg)
        raise ConnectionResetError(error_msg)
    return response

class CodebeamerClient:
    def __init__(self, base_url=CODEBEAMER_URL, username=None, password=None):
        LOGGER.info("Initialization Success")
        self.base_url = base_url.rstrip("/")
        self.auth = HTTPBasicAuth(username, password)
        self.headers = {
            "Content-Type": "application/json",
        }

    def get(self, path, params=None):
        """List resources"""
        url = f"{self.base_url}/{path.lstrip('/')}"
        response = requests.get(url, headers=self.headers, params=params, auth=self.auth)
        try:
            return sap_api_gateway_response_handler(response).json()
        except (TypeError, ConnectionResetError) as error:
            LOGGER.error(f"Failed to get {path}")
            return {}

    def retrieve(self, path, resource_id, suffix=None):
        """Get a single resource by ID"""
        url = f"{self.base_url}/{path.rstrip('/')}/{resource_id}/"
        if suffix:
            url += suffix
        response = requests.get(url, headers=self.headers, auth=self.auth)
        try:
            return sap_api_gateway_response_handler(response).json()
        except (TypeError, ConnectionResetError) as error:
            LOGGER.error(f"Failed to get {path} id {resource_id}")
            return {}

    def post(self, path, data, type='json'):
        url = f"{self.base_url}/{path.lstrip('/')}"
        if type != 'json':
            response = requests.post(url, auth=self.auth, files=data)
        else:
            response = requests.post(url, headers=self.headers, json=data, auth=self.auth)
        try:
            return sap_api_gateway_response_handler(response).json()
        except (TypeError, ConnectionResetError):
            LOGGER.error(f"Failed to post to {path} with data: {data}")
            return {}

    def patch(self, path, data):
        url = f"{self.base_url}/{path.lstrip('/')}"
        response = requests.patch(url, headers=self.headers, json=data, auth=self.auth)
        try:
            return sap_api_gateway_response_handler(response).json()
        except (TypeError, ConnectionResetError) as error:
            LOGGER.error(f"Failed to patch data: {data}")
            return {}

    def put(self, path, data):
        """Update or replace a resource"""
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            response = requests.put(url, headers=self.headers, json=data, auth=self.auth)
            return sap_api_gateway_response_handler(response).json()
        except (TypeError, ConnectionResetError) as error:
            LOGGER.error(f"Failed to put to {path} with data: {data}. Error: {error}")
            return {}

    def delete(self, path):
        """Delete a resource"""
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            response = requests.delete(url, headers=self.headers, auth=self.auth)
            return sap_api_gateway_response_handler(response).json()
        except (TypeError, ConnectionResetError) as error:
            LOGGER.error(f"Failed to delete {path}. Error: {error}")
            return {}

class CustomCodeBeamer(CodebeamerClient):
    def __init__(self, base_url=CODEBEAMER_URL, username=None, password=None):
        super().__init__(base_url, username, password)

    @staticmethod
    def handle_missing_keys(default_value=None):
        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except (KeyError, IndexError, TypeError):
                    return default_value
            return wrapper
        return decorator

    def put_item(self, item_id, payload):
        return self.put(f"items/{item_id}/fields", payload)

    '''ITEM'''
    def get_item_info(self, item_id):
        return self.retrieve("items", item_id)

    # assume the test set and test run is one to one mapping
    @handle_missing_keys(default_value="")
    def find_test_run_id_by_test_set(self, item_id):
        payload = {
            "queryString": f"referenceToId = {item_id}",
            "pageSize": 500
        }
        return self.post("items/query", payload)['items'][0]['parent']['id']

    # set test run status to "In Progress"
    def test_run_status_to_progress(self, test_run_id):
        curr_status = self.get_item_info(test_run_id)['status']['name']
        if curr_status != 'Finished':
            return
        payload = {
                    "fieldValues": [
                            {'fieldId': 7,
                                'name': 'Status',
                                'values': [
                                    {
                                        'id': 1,
                                        'name': 'In progress',
                                        'type': 'ChoiceOptionReference'
                                    }
                                ],
                                'sharedFieldNames': [],
                                'type': 'ChoiceFieldValue'}
                    ]
                }
        return self.put_item(test_run_id, payload)

    def format_test_case_id_res_map(self, test_cases_info: list[dict]) -> list[dict]:
        update_request_models = []

        for test_case_info in test_cases_info:
            update_request_model = {
                "testCaseReference": {
                    "id": test_case_info['id'],
                    "type": "TrackerItemReference"
                },
                "result": test_case_info['result'],
                "conclusion": test_case_info['url'],
            }
            update_request_models.append(update_request_model)

        return update_request_models

    def update_test_runs(self, test_run_id: int, test_cases_info: list[dict]):
        payload = {
            "updateRequestModels": self.format_test_case_id_res_map(test_cases_info)
        }
        print('payload:', payload)
        return self.put(f"testruns/{test_run_id}", payload)
