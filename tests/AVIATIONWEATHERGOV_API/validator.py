import json
import yaml
from jsonschema import validate, ValidationError, RefResolver
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
        self.resolver = self._create_resolver()

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

    def _create_resolver(self) -> RefResolver:
        """Create a reference resolver for $ref handling."""
        # Create a resolver that can handle internal references
        return RefResolver.from_schema(self.spec)

    # TODO: add this function to codegen
    def get_response_schema(self, path: str, method: str, status_code: str) -> Dict[str, Any]:
        """
        Get the response schema for a specific endpoint, method, and status code.
        
        Args:
            path: The path of the endpoint
            method: The HTTP method (e.g., 'get', 'post')
            status_code: The HTTP status code (e.g., '200', '404')

        Returns:
            The schema dictionary for the response
        """
        # Find the operation
        operation = None
        for p, methods in self.spec.get('paths', {}).items():
            if p == path:
                operation = methods.get(method.lower())
                break

        if not operation:
            raise ValueError(f"Path '{path}' and method '{method}' not found in specification")

        # Find the response
        response = operation.get('responses', {}).get(status_code)
        if not response:
            raise ValueError(f"Status code '{status_code}' not found for path '{path}' and method '{method}'")
        schema = response.get('content', {}).get('application/json', {}).get('schema')

        if not schema:  
            raise ValueError(f"No schema found for status code '{status_code}' at path '{path}' and method '{method}'")

        # Get the schema reference
        schema_ref = schema.get('$ref')
        if not schema_ref:
            return schema

        # Resolve the schema reference
        schema_name = schema_ref.split('/')[-1]
        return self.get_schema(schema_name)

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
        validate(instance=data, schema=schema, resolver=self.resolver)
        return True

    def validate_with_schema(self, json_data: Union[str, Dict], schema: Dict[str, Any]) -> bool:
        """
        Validate a JSON object against a provided schema.
        
        Args:
            json_data: JSON string or dictionary to validate
            schema: The schema dictionary to validate against
            
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

        # Validate
        validate(instance=data, schema=schema, resolver=self.resolver)
        return True

    def validate_with_details(self, json_data: Union[str, Dict], schema_name: str) -> Dict[str, Any]:
        """
        Validate and return detailed results.
        
        Args:
            json_data: JSON string or dictionary to validate
            schema_name: Name of the component schema to validate against
            
        Returns:
            Dictionary with validation results
        """
        result = {
            'valid': False,
            'schema_name': schema_name,
            'errors': []
        }

        try:
            self.validate_json(json_data, schema_name)
            result['valid'] = True
        except ValidationError as e:
            result['errors'].append({
                'message': e.message,
                'path': list(e.path),
                'schema_path': list(e.schema_path),
                'validator': e.validator,
                'validator_value': e.validator_value
            })
        except json.JSONDecodeError as e:
            result['errors'].append({
                'message': f"Invalid JSON: {str(e)}",
                'type': 'JSONDecodeError'
            })
        except Exception as e:
            result['errors'].append({
                'message': str(e),
                'type': type(e).__name__
            })

        return result

    def list_schemas(self) -> list:
        """Return a list of all available schema names."""
        return list(self.schemas.keys())  
