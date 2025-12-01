package org.springframework.RoostTest.weather.utils;

import io.restassured.response.Response;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.hamcrest.MatcherAssert;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import org.springframework.RoostTest.weather.utils.SchemaModels.ResponseSchema;
import org.springframework.RoostTest.weather.utils.SchemaModels.FieldConstraint;
import org.springframework.RoostTest.weather.utils.SchemaModels.NumericConstraint;
import org.springframework.RoostTest.weather.utils.SchemaModels.StringConstraint;
import org.springframework.RoostTest.weather.utils.SchemaModels.ArrayConstraint;

import java.io.IOException;
import java.util.*;
import java.util.regex.Pattern;

import static org.hamcrest.Matchers.*;

/**
 * Reusable validator for REST API responses against OpenAPI schemas. Validates all
 * OpenAPI constraints including types, required fields, enums, numeric ranges, string
 * patterns, array constraints, and formats.
 */
public class ResponseValidator {

	private static final Logger logger = LoggerFactory.getLogger(ResponseValidator.class);

	private final ObjectMapper objectMapper;

	public ResponseValidator() {
		this.objectMapper = new ObjectMapper();
	}

	/**
	 * Main entry point for response validation. Routes to appropriate validator based on
	 * status code.
	 */
	public void validateResponse(Response response, int expectedStatusCode, ResponseSchema schema) {
		// Verify status code
		response.then().statusCode(expectedStatusCode);

		if (schema == null) {
			logger.warn("No schema defined for status code: {}", expectedStatusCode);
			return;
		}

		// Parse response body
		String responseBody = response.getBody().asString();
		if (responseBody == null || responseBody.isEmpty()) {
			return;
		}

		try {
			JsonNode responseJson = objectMapper.readTree(responseBody);

			// Route to appropriate validator
			if (expectedStatusCode >= 200 && expectedStatusCode < 300) {
				validateSuccessResponse(responseJson, schema);
			}
			else {
				validateErrorResponse(responseJson, schema);
			}
		}
		catch (IOException e) {
			logger.error("Failed to parse response JSON: {}", e.getMessage());
			throw new AssertionError("Failed to parse response JSON", e);
		}
	}

	/**
	 * Validates success responses (2xx status codes).
	 */
	public void validateSuccessResponse(JsonNode responseJson, ResponseSchema schema) {
		// Special handling when the root is an array (indicated by "$" field)
		if (schema.getFields().containsKey("$")) {
			FieldConstraint rootArrayConstraint = schema.getFields().get("$");

			// Verify the response is actually an array
			if (!responseJson.isArray()) {
				throw new AssertionError("Expected array response but got: " + responseJson.getNodeType());
			}

			// Validate the array itself
			validateType(responseJson, "array", "$");

			// Validate array constraints (minItems, maxItems, uniqueItems)
			if (rootArrayConstraint.getArrayConstraint() != null) {
				validateArrayConstraintsOnNode(responseJson, rootArrayConstraint.getArrayConstraint(), "$");
			}

			// Validate each item in the array
			if (rootArrayConstraint.getItemsConstraint() != null) {
				FieldConstraint itemConstraint = rootArrayConstraint.getItemsConstraint();

				for (int i = 0; i < responseJson.size(); i++) {
					JsonNode item = responseJson.get(i);
					String itemPath = "$[" + i + "]";

					// Validate item type
					if (itemConstraint.getType() != null) {
						validateType(item, itemConstraint.getType(), itemPath);
					}

					// Validate nested fields if item is an object
					// Use empty basePath because 'item' is already the correct context
					if ("object".equals(itemConstraint.getType()) && itemConstraint.getNestedFields() != null) {
						validateRequiredFields(item, itemConstraint.getNestedRequired(), "");
						validateFieldTypesWithPath(item, itemConstraint.getNestedFields(), "", itemPath);
						validateEnumValuesWithPath(item, itemConstraint.getNestedFields(), "", itemPath);
						validateNumericConstraintsWithPath(item, itemConstraint.getNestedFields(), "", itemPath);
						validateStringConstraintsWithPath(item, itemConstraint.getNestedFields(), "", itemPath);
						validateArrayConstraintsWithPath(item, itemConstraint.getNestedFields(), "", itemPath);
					}
				}
			}
		}
		else {
			// Standard object response validation
			validateRequiredFields(responseJson, schema.getRequiredFields(), "");
			validateFieldTypes(responseJson, schema.getFields(), "");
			validateEnumValues(responseJson, schema.getFields(), "");
			validateNumericConstraints(responseJson, schema.getFields(), "");
			validateStringConstraints(responseJson, schema.getFields(), "");
			validateArrayConstraints(responseJson, schema.getFields(), "");
		}
	}

	/**
	 * Validates error responses (4xx/5xx status codes).
	 */
	public void validateErrorResponse(JsonNode responseJson, ResponseSchema schema) {
		validateRequiredFields(responseJson, schema.getRequiredFields(), "");
		validateFieldTypes(responseJson, schema.getFields(), "");
	}

	/**
	 * Validates that all required fields are present.
	 */
	private void validateRequiredFields(JsonNode json, List<String> requiredFields, String basePath) {
		if (requiredFields == null || requiredFields.isEmpty()) {
			return;
		}

		for (String field : requiredFields) {
			String fieldPath = basePath.isEmpty() ? field : basePath + "." + field;
			JsonNode node = getNodeAtPath(json, fieldPath);
			MatcherAssert.assertThat("Required field missing: " + fieldPath, node, notNullValue());
		}
	}

	/**
	 * Validates field types according to schema.
	 */
	private void validateFieldTypes(JsonNode json, Map<String, FieldConstraint> fields, String basePath) {
		validateFieldTypesWithPath(json, fields, basePath, basePath);
	}

	/**
	 * Validates field types with separate display and navigation paths.
	 */
	private void validateFieldTypesWithPath(JsonNode json, Map<String, FieldConstraint> fields, String basePath,
			String displayPath) {
		if (fields == null || fields.isEmpty()) {
			return;
		}

		for (Map.Entry<String, FieldConstraint> entry : fields.entrySet()) {
			String fieldName = entry.getKey();
			FieldConstraint constraint = entry.getValue();
			String fieldPath = basePath.isEmpty() ? fieldName : basePath + "." + fieldName;
			String fieldDisplayPath = displayPath.isEmpty() ? fieldName : displayPath + "." + fieldName;

			JsonNode node = getNodeAtPath(json, fieldPath);
			if (node == null || node.isNull()) {
				continue;
			}

			String type = constraint.getType();
			if (type != null) {
				validateType(node, type, fieldDisplayPath);

				// Recursively validate nested objects
				if ("object".equals(type) && constraint.getNestedFields() != null) {
					validateFieldTypesWithPath(node, constraint.getNestedFields(), fieldPath, fieldDisplayPath);
					validateRequiredFields(node, constraint.getNestedRequired(), fieldPath);
					validateEnumValuesWithPath(node, constraint.getNestedFields(), fieldPath, fieldDisplayPath);
					validateNumericConstraintsWithPath(node, constraint.getNestedFields(), fieldPath, fieldDisplayPath);
					validateStringConstraintsWithPath(node, constraint.getNestedFields(), fieldPath, fieldDisplayPath);
					validateArrayConstraintsWithPath(node, constraint.getNestedFields(), fieldPath, fieldDisplayPath);
				}
			}
		}
	}

	/**
	 * Validates type of a single field.
	 */
	private void validateType(JsonNode node, String type, String fieldPath) {
		switch (type) {
			case "string":
				MatcherAssert.assertThat(fieldPath + " should be string", node.isTextual(), is(true));
				break;
			case "number":
				MatcherAssert.assertThat(fieldPath + " should be number", node.isNumber(), is(true));
				break;
			case "integer":
				MatcherAssert.assertThat(fieldPath + " should be integer", node.isInt() || node.isLong(), is(true));
				break;
			case "boolean":
				MatcherAssert.assertThat(fieldPath + " should be boolean", node.isBoolean(), is(true));
				break;
			case "array":
				MatcherAssert.assertThat(fieldPath + " should be array", node.isArray(), is(true));
				break;
			case "object":
				MatcherAssert.assertThat(fieldPath + " should be object", node.isObject(), is(true));
				break;
		}
	}

	/**
	 * Validates enum constraints.
	 */
	private void validateEnumValues(JsonNode json, Map<String, FieldConstraint> fields, String basePath) {
		validateEnumValuesWithPath(json, fields, basePath, basePath);
	}

	/**
	 * Validates enum constraints with separate display and navigation paths.
	 */
	private void validateEnumValuesWithPath(JsonNode json, Map<String, FieldConstraint> fields, String basePath,
			String displayPath) {
		if (fields == null || fields.isEmpty()) {
			return;
		}

		for (Map.Entry<String, FieldConstraint> entry : fields.entrySet()) {
			String fieldName = entry.getKey();
			FieldConstraint constraint = entry.getValue();
			String fieldPath = basePath.isEmpty() ? fieldName : basePath + "." + fieldName;
			String fieldDisplayPath = displayPath.isEmpty() ? fieldName : displayPath + "." + fieldName;

			JsonNode node = getNodeAtPath(json, fieldPath);
			if (node == null || node.isNull()) {
				continue;
			}

			if (constraint.getEnumValues() != null && !constraint.getEnumValues().isEmpty()) {
				String value = node.asText();
				MatcherAssert.assertThat(fieldDisplayPath + " should be one of " + constraint.getEnumValues(),
						constraint.getEnumValues(), hasItem(value));
			}
		}
	}

	/**
	 * Validates numeric constraints (min, max, multipleOf).
	 */
	private void validateNumericConstraints(JsonNode json, Map<String, FieldConstraint> fields, String basePath) {
		validateNumericConstraintsWithPath(json, fields, basePath, basePath);
	}

	/**
	 * Validates numeric constraints with separate display and navigation paths.
	 */
	private void validateNumericConstraintsWithPath(JsonNode json, Map<String, FieldConstraint> fields, String basePath,
			String displayPath) {
		if (fields == null || fields.isEmpty()) {
			return;
		}

		for (Map.Entry<String, FieldConstraint> entry : fields.entrySet()) {
			String fieldName = entry.getKey();
			FieldConstraint constraint = entry.getValue();
			String fieldPath = basePath.isEmpty() ? fieldName : basePath + "." + fieldName;
			String fieldDisplayPath = displayPath.isEmpty() ? fieldName : displayPath + "." + fieldName;

			JsonNode node = getNodeAtPath(json, fieldPath);
			if (node == null || node.isNull() || !node.isNumber()) {
				continue;
			}

			NumericConstraint numConstraint = constraint.getNumericConstraint();
			if (numConstraint != null) {
				double value = node.asDouble();

				if (numConstraint.getMinimum() != null) {
					if (numConstraint.isExclusiveMinimum()) {
						MatcherAssert.assertThat(fieldDisplayPath + " > " + numConstraint.getMinimum(), value,
								greaterThan(numConstraint.getMinimum()));
					}
					else {
						MatcherAssert.assertThat(fieldDisplayPath + " >= " + numConstraint.getMinimum(), value,
								greaterThanOrEqualTo(numConstraint.getMinimum()));
					}
				}

				if (numConstraint.getMaximum() != null) {
					if (numConstraint.isExclusiveMaximum()) {
						MatcherAssert.assertThat(fieldDisplayPath + " < " + numConstraint.getMaximum(), value,
								lessThan(numConstraint.getMaximum()));
					}
					else {
						MatcherAssert.assertThat(fieldDisplayPath + " <= " + numConstraint.getMaximum(), value,
								lessThanOrEqualTo(numConstraint.getMaximum()));
					}
				}

				if (numConstraint.getMultipleOf() != null) {
					double remainder = value % numConstraint.getMultipleOf();
					MatcherAssert.assertThat(fieldDisplayPath + " multipleOf " + numConstraint.getMultipleOf(),
							remainder, closeTo(0, 0.0000001));
				}
			}

			// Recursively validate nested objects
			if (constraint.getNestedFields() != null && node.isObject()) {
				validateNumericConstraintsWithPath(node, constraint.getNestedFields(), fieldPath, fieldDisplayPath);
			}
		}
	}

	/**
	 * Validates string constraints (minLength, maxLength, pattern, format).
	 */
	private void validateStringConstraints(JsonNode json, Map<String, FieldConstraint> fields, String basePath) {
		validateStringConstraintsWithPath(json, fields, basePath, basePath);
	}

	/**
	 * Validates string constraints with separate display and navigation paths.
	 */
	private void validateStringConstraintsWithPath(JsonNode json, Map<String, FieldConstraint> fields, String basePath,
			String displayPath) {
		if (fields == null || fields.isEmpty()) {
			return;
		}

		for (Map.Entry<String, FieldConstraint> entry : fields.entrySet()) {
			String fieldName = entry.getKey();
			FieldConstraint constraint = entry.getValue();
			String fieldPath = basePath.isEmpty() ? fieldName : basePath + "." + fieldName;
			String fieldDisplayPath = displayPath.isEmpty() ? fieldName : displayPath + "." + fieldName;

			JsonNode node = getNodeAtPath(json, fieldPath);
			if (node == null || node.isNull() || !node.isTextual()) {
				continue;
			}

			String value = node.asText();
			StringConstraint strConstraint = constraint.getStringConstraint();

			if (strConstraint != null) {
				if (strConstraint.getMinLength() != null) {
					MatcherAssert.assertThat(fieldDisplayPath + " length >= " + strConstraint.getMinLength(),
							value.length(), greaterThanOrEqualTo(strConstraint.getMinLength()));
				}

				if (strConstraint.getMaxLength() != null) {
					MatcherAssert.assertThat(fieldDisplayPath + " length <= " + strConstraint.getMaxLength(),
							value.length(), lessThanOrEqualTo(strConstraint.getMaxLength()));
				}

				if (strConstraint.getPattern() != null) {
					MatcherAssert.assertThat(fieldDisplayPath + " matches pattern",
							Pattern.matches(strConstraint.getPattern(), value), is(true));
				}
			}

			// Validate format
			if (constraint.getFormat() != null) {
				validateFormat(value, constraint.getFormat(), fieldDisplayPath);
			}

			// Recursively validate nested objects
			if (constraint.getNestedFields() != null && node.isObject()) {
				validateStringConstraintsWithPath(node, constraint.getNestedFields(), fieldPath, fieldDisplayPath);
			}
		}
	}

	/**
	 * Validates array constraints (minItems, maxItems, uniqueItems).
	 */
	private void validateArrayConstraints(JsonNode json, Map<String, FieldConstraint> fields, String basePath) {
		validateArrayConstraintsWithPath(json, fields, basePath, basePath);
	}

	/**
	 * Validates array constraints with separate display and navigation paths.
	 */
	private void validateArrayConstraintsWithPath(JsonNode json, Map<String, FieldConstraint> fields, String basePath,
			String displayPath) {
		if (fields == null || fields.isEmpty()) {
			return;
		}

		for (Map.Entry<String, FieldConstraint> entry : fields.entrySet()) {
			String fieldName = entry.getKey();
			FieldConstraint constraint = entry.getValue();
			String fieldPath = basePath.isEmpty() ? fieldName : basePath + "." + fieldName;
			String fieldDisplayPath = displayPath.isEmpty() ? fieldName : displayPath + "." + fieldName;

			JsonNode node = getNodeAtPath(json, fieldPath);
			if (node == null || node.isNull() || !node.isArray()) {
				continue;
			}

			ArrayConstraint arrConstraint = constraint.getArrayConstraint();
			if (arrConstraint != null) {
				validateArrayConstraintsOnNode(node, arrConstraint, fieldDisplayPath);
			}

			// Recursively validate array items
			if (constraint.getItemsConstraint() != null && constraint.getItemsConstraint().getNestedFields() != null) {
				for (int i = 0; i < node.size(); i++) {
					JsonNode item = node.get(i);
					if (item.isObject()) {
						String itemPath = fieldPath + "[" + i + "]";
						String itemDisplayPath = fieldDisplayPath + "[" + i + "]";
						validateFieldTypesWithPath(item, constraint.getItemsConstraint().getNestedFields(), "",
								itemDisplayPath);
						validateNumericConstraintsWithPath(item, constraint.getItemsConstraint().getNestedFields(), "",
								itemDisplayPath);
						validateStringConstraintsWithPath(item, constraint.getItemsConstraint().getNestedFields(), "",
								itemDisplayPath);
						validateArrayConstraintsWithPath(item, constraint.getItemsConstraint().getNestedFields(), "",
								itemDisplayPath);
					}
				}
			}
		}
	}

	/**
	 * Helper method to validate array constraints on a specific node.
	 */
	private void validateArrayConstraintsOnNode(JsonNode arrayNode, ArrayConstraint arrConstraint, String fieldPath) {
		int size = arrayNode.size();

		if (arrConstraint.getMinItems() != null) {
			MatcherAssert.assertThat(fieldPath + " minItems " + arrConstraint.getMinItems(), size,
					greaterThanOrEqualTo(arrConstraint.getMinItems()));
		}

		if (arrConstraint.getMaxItems() != null) {
			MatcherAssert.assertThat(fieldPath + " maxItems " + arrConstraint.getMaxItems(), size,
					lessThanOrEqualTo(arrConstraint.getMaxItems()));
		}

		if (arrConstraint.isUniqueItems()) {
			Set<String> uniqueItems = new HashSet<>();
			for (JsonNode item : arrayNode) {
				uniqueItems.add(item.toString());
			}
			MatcherAssert.assertThat(fieldPath + " should have unique items", uniqueItems.size(), equalTo(size));
		}
	}

	/**
     * Validates string format (date, email, uri, uuid, etc.).
     */
    private void validateFormat(String value, String format, String fieldPath) {
        if (format == null || value == null) {
            return;
        }

        switch (format.toLowerCase()) {
            case "date":
                MatcherAssert.assertThat(fieldPath + " valid date",
                    Pattern.matches("^\d{4}-\d{2}-\d{2}$", value), is(true));
                break;
            case "date-time":
                MatcherAssert.assertThat(fieldPath + " valid date-time",
                    Pattern.matches("^\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}(:\d{2})?.*$", value), is(true));
                break;
            case "email":
                MatcherAssert.assertThat(fieldPath + " valid email",
                    Pattern.matches("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", value), is(true));
                break;
            case "uri":
            case "url":
                MatcherAssert.assertThat(fieldPath + " valid URI",
                    Pattern.matches("^(https?|ftp)://.*$", value), is(true));
                break;
            case "uuid":
                MatcherAssert.assertThat(fieldPath + " valid UUID",
                    Pattern.matches("^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$", value), is(true));
                break;
            case "ipv4":
                MatcherAssert.assertThat(fieldPath + " valid IPv4",
                    Pattern.matches("^(\d{1,3}\.){3}\d{1,3}$", value), is(true));
                break;
            case "ipv6":
                MatcherAssert.assertThat(fieldPath + " valid IPv6",
                    Pattern.matches("^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$", value), is(true));
                break;
        }
    }

	/**
     * Gets JsonNode at specific path in JSON tree.
     */
    private JsonNode getNodeAtPath(JsonNode json, String path) {
        if (path == null || path.isEmpty()) {
            return json;
        }

        String[] parts = path.split("\.");
        JsonNode current = json;

        for (String part : parts) {
            if (current == null) {
                return null;
            }

            if (part.contains("[") && part.endsWith("]")) {
                int bracketIndex = part.indexOf("[");
                String fieldName = part.substring(0, bracketIndex);
                int arrayIndex = Integer.parseInt(part.substring(bracketIndex + 1, part.length() - 1));

                // Handle special case where fieldName is "$" or empty (root array)
                if (fieldName.isEmpty() || "$".equals(fieldName)) {
                    if (current.isArray() && arrayIndex < current.size()) {
                        current = current.get(arrayIndex);
                    } else {
                        return null;
                    }
                } else {
                    current = current.get(fieldName);
                    if (current != null && current.isArray() && arrayIndex < current.size()) {
                        current = current.get(arrayIndex);
                    } else {
                        return null;
                    }
                }
            } else {
                current = current.get(part);
            }
        }

        return current;
    }

}
