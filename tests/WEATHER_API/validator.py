import json
import yaml
from jsonschema import validate, ValidationError
from typing import Dict, Any, Union
import sys
import requests

class SwaggerSchemaValidator:
    """
    Validates JSON objects against component schemas defined in Swagger/OpenAPI specifications.
    """

    def __init__(self, swagger_source: str):
        """
        Initialize the validator with a Swagger/OpenAPI specification file or URL.
        
        Args:
            swagger_source: Path to file or URL of the Swagger/OpenAPI YAML or JSON spec
        """
        self.spec = self._load_spec(swagger_source)
        self.schemas = self._extract_schemas()

    def _load_spec(self, source: str) -> Dict[str, Any]:
        """Load the Swagger/OpenAPI specification from a file or URL."""
        if source.startswith(('http://', 'https://')):
            response = requests.get(source)
            response.raise_for_status()
            content = response.text
            
            # Try YAML first, then JSON
            try:
                if source.endswith(('.yaml', '.yml')) or 'yaml' in response.headers.get('content-type', ''):
                    return yaml.safe_load(content)
                else:
                    return yaml.safe_load(content)  # Try YAML first
            except yaml.YAMLError:
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    raise ValueError(f"URL content is not valid YAML or JSON. Check if URL points to a Swagger/OpenAPI spec.")
        else:
            with open(source, 'r') as f:
                if source.endswith('.yaml') or source.endswith('.yml'):
                    return yaml.safe_load(f)
                elif source.endswith('.json'):
                    return json.load(f)
                else:
                    raise ValueError("File must be .yaml, .yml, or .json")

    def _extract_schemas(self) -> Dict[str, Any]:
        """Extract component schemas from the specification."""
        # OpenAPI 3.x uses 'components/schemas'
        if 'components' in self.spec and 'schemas' in self.spec['components']:
            return self.spec['components']['schemas']
        # Swagger 2.x uses 'definitions'
        elif 'definitions' in self.spec:
            return self.spec['definitions']
        else:
            raise ValueError("No component schemas found in specification")

    def get_schema(self, schema_name: str) -> Dict[str, Any]:
        """
        Get a specific component schema by name.
        
        Args:
            schema_name: Name of the component schema
            
        Returns:
            The schema dictionary
        """
        if schema_name not in self.schemas:
            available = ', '.join(self.schemas.keys())
            raise ValueError(f"Schema '{schema_name}' not found. Available schemas: {available}")
        return self.schemas[schema_name]

    def validate_schema_by_response(
        self,
        endpoint: str,
        method: str,
        status_code: str,
        response_json: Union[str, Dict]
    ) -> Dict[str, Any]:
        """
        Validate a response JSON against the schema defined for an endpoint + method + status code.

        Args:
            endpoint: API path (e.g. "/users/{id}")
            method: HTTP method (GET, POST, etc.)
            status_code: HTTP status code as string ("200", "201", "default")
            response_json: JSON response (str or dict)

        Returns:
            dict:
                {
                    "valid": bool,
                    "endpoint": str,
                    "method": str,
                    "status_code": str,
                    "errors": [...]
                }
        """

        result = {
            "valid": False,
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "errors": []
        }

        # Normalize JSON input
        try:
            data = json.loads(response_json) if isinstance(response_json, str) else response_json
        except Exception as e:
            result["errors"].append({"message": f"Invalid JSON: {e}"})
            return result

        # Normalize method
        method = method.lower()

        # Validate path
        paths = self.spec.get("paths", {})
        if endpoint not in paths:
            result["errors"].append({"message": f"Endpoint '{endpoint}' not found in API spec"})
            return result

        # Validate method
        if method not in paths[endpoint]:
            result["errors"].append({"message": f"Method '{method.upper()}' not found under '{endpoint}'"})
            return result

        # Validate response status
        responses = paths[endpoint][method].get("responses", {})
        if status_code not in responses:
            result["errors"].append({
                "message": f"Status code '{status_code}' not found for {method.upper()} {endpoint}"
            })
            return result

        response_block = responses[status_code]

        # Determine schema format (OpenAPI3 vs Swagger2)
        schema = None

        # OpenAPI 3.x: schema under content -> application/json
        if "content" in response_block:
            content = response_block.get("content", {})
            if "application/json" in content:
                schema = content["application/json"].get("schema")

        # Swagger 2.x: schema directly present
        if schema is None and "schema" in response_block:
            schema = response_block["schema"]

        if not schema:
            result["errors"].append({
                "message": "No schema defined for this endpoint/method/statusCode"
            })
            return result

        # Resolve $ref if present
        if "$ref" in schema:
            ref_name = schema["$ref"].split("/")[-1]
            try:
                schema = self.get_schema(ref_name)
            except Exception as e:
                result["errors"].append({"message": f"Invalid $ref: {e}"})
                return result

        # Validate JSON against schema
        try:
            validate(instance=data, schema=schema)
            result["valid"] = True
        except ValidationError as e:
            result["errors"].append({
                "message": e.message,
                "path": list(e.path),
                "schema_path": list(e.schema_path),
                "validator": e.validator,
                "validator_value": e.validator_value
            })

        return result

    def validate_json(self, json_data: Union[str, Dict], schema_name: str) -> bool:
        """
        Validate a JSON object against a component schema.
        
        Args:
            json_data: JSON string or dictionary to validate
            schema_name: Name of the component schema to validate against
            
        Returns:
            True if validation succeeds
            
        Raises:
            ValidationError: If validation fails
        """
        # Parse JSON if string is provided
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data

        # Get the schema
        schema = self.get_schema(schema_name)

        # Validate
        validate(instance=data, schema=schema)
        return True

    def list_schemas(self) -> list:
        """Return a list of all available schema names."""
        return list(self.schemas.keys())  
