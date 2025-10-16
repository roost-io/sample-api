import os
import pytest
import yaml
import requests
from pathlib import Path
from typing import Dict, Any, Optional

@pytest.fixture(scope="session")
def config():
    config_path = Path(__file__).parent / "config.yml"
    with open(config_path, 'r') as file:
        config_data = yaml.safe_load(file)
    
    def replace_env_vars(data):
        if isinstance(data, dict):
            return {k: replace_env_vars(v) for k, v in data.items()}
        elif isinstance(data, str) and data.startswith('${') and data.endswith('}'):
            env_var = data[2:-1]
            return os.getenv(env_var, data)
        return data
    
    return replace_env_vars(config_data)

class APIHelper:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
    
    def make_request(self, endpoint: str, params: Optional[Dict] = None, headers: Optional[Dict] = None, method: str = 'GET'):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.request(method=method, url=url, params=params, headers=headers)
        return response

@pytest.fixture(scope="session")
def api_helper(config):
    base_url = config.get('api', {}).get('base_url', '')
    return APIHelper(base_url)

class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
    
    def get(self, endpoint: str, headers: Optional[Dict] = None, params: Optional[Dict] = None):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.get(url, headers=headers, params=params)
        return response

@pytest.fixture(scope="session")
def api_client(config):
    base_url = config.get('api', {}).get('base_url', '')
    return APIClient(base_url)

@pytest.fixture(scope="session")
def valid_api_key(config):
    return config.get('auth', {}).get('api_key', '')

@pytest.fixture(scope="session")
def invalid_api_key():
    return "invalid_api_key_12345"

@pytest.fixture(scope="session")
def valid_location():
    return "KORD"

@pytest.fixture(scope="session")
def oauth2_token(config):
    return config.get('auth', {}).get('oauth2_token', '')

class SchemaValidator:
    def validate_metarproperties_schema(self, metarproperties_data: Dict[str, Any]) -> bool:
        """Validate METARproperties object schema"""
        required_fields = []
        return all(field in metarproperties_data for field in required_fields)

    def validate_metartext_schema(self, metartext_data: Dict[str, Any]) -> bool:
        """Validate METARtext object schema"""
        required_fields = []
        return all(field in metartext_data for field in required_fields)

    def validate_metarjson_schema(self, metarjson_data: Dict[str, Any]) -> bool:
        """Validate METARJSON object schema"""
        required_fields = []
        return all(field in metarjson_data for field in required_fields)

    def validate_metargeojson_schema(self, metargeojson_data: Dict[str, Any]) -> bool:
        """Validate METARGeoJSON object schema"""
        required_fields = []
        return all(field in metargeojson_data for field in required_fields)

    def validate_metarxml_schema(self, metarxml_data: Dict[str, Any]) -> bool:
        """Validate METARXML object schema"""
        required_fields = []
        return all(field in metarxml_data for field in required_fields)

    def validate_tafproperties_schema(self, tafproperties_data: Dict[str, Any]) -> bool:
        """Validate TAFproperties object schema"""
        required_fields = []
        return all(field in tafproperties_data for field in required_fields)

    def validate_taftext_schema(self, taftext_data: Dict[str, Any]) -> bool:
        """Validate TAFtext object schema"""
        required_fields = []
        return all(field in taftext_data for field in required_fields)

    def validate_tafjson_schema(self, tafjson_data: Dict[str, Any]) -> bool:
        """Validate TAFJSON object schema"""
        required_fields = []
        return all(field in tafjson_data for field in required_fields)

    def validate_tafgeojson_schema(self, tafgeojson_data: Dict[str, Any]) -> bool:
        """Validate TAFGeoJSON object schema"""
        required_fields = []
        return all(field in tafgeojson_data for field in required_fields)

    def validate_pireptext_schema(self, pireptext_data: Dict[str, Any]) -> bool:
        """Validate PIREPtext object schema"""
        required_fields = []
        return all(field in pireptext_data for field in required_fields)

    def validate_pirepjson_schema(self, pirepjson_data: Dict[str, Any]) -> bool:
        """Validate PIREPJSON object schema"""
        required_fields = []
        return all(field in pirepjson_data for field in required_fields)

    def validate_pirepgeojson_schema(self, pirepgeojson_data: Dict[str, Any]) -> bool:
        """Validate PIREPGeoJSON object schema"""
        required_fields = []
        return all(field in pirepgeojson_data for field in required_fields)

    def validate_pirepxml_schema(self, pirepxml_data: Dict[str, Any]) -> bool:
        """Validate PIREPXML object schema"""
        required_fields = []
        return all(field in pirepxml_data for field in required_fields)

    def validate_stationinfojson_schema(self, stationinfojson_data: Dict[str, Any]) -> bool:
        """Validate StationInfoJSON object schema"""
        required_fields = []
        return all(field in stationinfojson_data for field in required_fields)

    def validate_stationinfogeojson_schema(self, stationinfogeojson_data: Dict[str, Any]) -> bool:
        """Validate StationInfoGeoJSON object schema"""
        required_fields = []
        return all(field in stationinfogeojson_data for field in required_fields)

    def validate_stationinfoxml_schema(self, stationinfoxml_data: Dict[str, Any]) -> bool:
        """Validate StationInfoXML object schema"""
        required_fields = []
        return all(field in stationinfoxml_data for field in required_fields)

    def validate_cloudinfo_schema(self, cloudinfo_data: Dict[str, Any]) -> bool:
        """Validate CloudInfo object schema"""
        required_fields = []
        return all(field in cloudinfo_data for field in required_fields)

    def validate_airsigmetjson_schema(self, airsigmetjson_data: Dict[str, Any]) -> bool:
        """Validate AirSigmetJSON object schema"""
        required_fields = []
        return all(field in airsigmetjson_data for field in required_fields)

    def validate_airsigmetgeojson_schema(self, airsigmetgeojson_data: Dict[str, Any]) -> bool:
        """Validate AirSigmetGeoJSON object schema"""
        required_fields = []
        return all(field in airsigmetgeojson_data for field in required_fields)

    def validate_isigmetjson_schema(self, isigmetjson_data: Dict[str, Any]) -> bool:
        """Validate ISigmetJSON object schema"""
        required_fields = []
        return all(field in isigmetjson_data for field in required_fields)

    def validate_isigmetgeojson_schema(self, isigmetgeojson_data: Dict[str, Any]) -> bool:
        """Validate ISigmetGeoJSON object schema"""
        required_fields = []
        return all(field in isigmetgeojson_data for field in required_fields)

    def validate_gairmetjson_schema(self, gairmetjson_data: Dict[str, Any]) -> bool:
        """Validate GairmetJSON object schema"""
        required_fields = []
        return all(field in gairmetjson_data for field in required_fields)

    def validate_gairmetgeojson_schema(self, gairmetgeojson_data: Dict[str, Any]) -> bool:
        """Validate GairmetGeoJSON object schema"""
        required_fields = []
        return all(field in gairmetgeojson_data for field in required_fields)

    def validate_airmetjson_schema(self, airmetjson_data: Dict[str, Any]) -> bool:
        """Validate AirmetJSON object schema"""
        required_fields = []
        return all(field in airmetjson_data for field in required_fields)

    def validate_airmetgeojson_schema(self, airmetgeojson_data: Dict[str, Any]) -> bool:
        """Validate AirmetGeoJSON object schema"""
        required_fields = []
        return all(field in airmetgeojson_data for field in required_fields)

    def validate_cwajson_schema(self, cwajson_data: Dict[str, Any]) -> bool:
        """Validate CwaJSON object schema"""
        required_fields = []
        return all(field in cwajson_data for field in required_fields)

    def validate_cwageojson_schema(self, cwageojson_data: Dict[str, Any]) -> bool:
        """Validate CwaGeoJSON object schema"""
        required_fields = []
        return all(field in cwageojson_data for field in required_fields)

    def validate_tcfgeojson_schema(self, tcfgeojson_data: Dict[str, Any]) -> bool:
        """Validate TcfGeoJSON object schema"""
        required_fields = []
        return all(field in tcfgeojson_data for field in required_fields)

    def validate_errorjson_schema(self, errorjson_data: Dict[str, Any]) -> bool:
        """Validate ErrorJSON object schema"""
        required_fields = []
        return all(field in errorjson_data for field in required_fields)

    def validate_errorxml_schema(self, errorxml_data: Dict[str, Any]) -> bool:
        """Validate ErrorXML object schema"""
        required_fields = []
        return all(field in errorxml_data for field in required_fields)

@pytest.fixture(scope="session")
def schema_validator():
    return SchemaValidator()
