package org.springframework.RoostTest.circle_ci_oai_security.utils;

import java.util.*;

/**
 * Schema model classes for API response validation.
 */
public class SchemaModels {

	/**
	 * Response schema containing field definitions and constraints.
	 */
	public static class ResponseSchema {

		private Map<String, FieldConstraint> fields;

		private List<String> requiredFields;

		public ResponseSchema() {
			this.fields = new HashMap<>();
			this.requiredFields = new ArrayList<>();
		}

		public Map<String, FieldConstraint> getFields() {
			return fields;
		}

		public ResponseSchema setFields(Map<String, FieldConstraint> fields) {
			this.fields = fields;
			return this;
		}

		public List<String> getRequiredFields() {
			return requiredFields;
		}

		public ResponseSchema setRequiredFields(List<String> requiredFields) {
			this.requiredFields = requiredFields;
			return this;
		}

	}

	/**
	 * Field constraint containing type and validation rules.
	 */
	public static class FieldConstraint {

		private String type;

		private String format;

		private List<String> enumValues;

		private NumericConstraint numericConstraint;

		private StringConstraint stringConstraint;

		private ArrayConstraint arrayConstraint;

		private Map<String, FieldConstraint> nestedFields;

		private List<String> nestedRequired;

		private FieldConstraint itemsConstraint;

		public FieldConstraint(String type) {
			this.type = type;
		}

		public String getType() {
			return type;
		}

		public FieldConstraint setType(String type) {
			this.type = type;
			return this;
		}

		public String getFormat() {
			return format;
		}

		public FieldConstraint setFormat(String format) {
			this.format = format;
			return this;
		}

		public List<String> getEnumValues() {
			return enumValues;
		}

		public FieldConstraint setEnumValues(List<String> enumValues) {
			this.enumValues = enumValues;
			return this;
		}

		public NumericConstraint getNumericConstraint() {
			return numericConstraint;
		}

		public FieldConstraint setNumericConstraint(NumericConstraint numericConstraint) {
			this.numericConstraint = numericConstraint;
			return this;
		}

		public StringConstraint getStringConstraint() {
			return stringConstraint;
		}

		public FieldConstraint setStringConstraint(StringConstraint stringConstraint) {
			this.stringConstraint = stringConstraint;
			return this;
		}

		public ArrayConstraint getArrayConstraint() {
			return arrayConstraint;
		}

		public FieldConstraint setArrayConstraint(ArrayConstraint arrayConstraint) {
			this.arrayConstraint = arrayConstraint;
			return this;
		}

		public Map<String, FieldConstraint> getNestedFields() {
			return nestedFields;
		}

		public FieldConstraint setNestedFields(Map<String, FieldConstraint> nestedFields) {
			this.nestedFields = nestedFields;
			return this;
		}

		public List<String> getNestedRequired() {
			return nestedRequired;
		}

		public FieldConstraint setNestedRequired(List<String> nestedRequired) {
			this.nestedRequired = nestedRequired;
			return this;
		}

		public FieldConstraint getItemsConstraint() {
			return itemsConstraint;
		}

		public FieldConstraint setItemsConstraint(FieldConstraint itemsConstraint) {
			this.itemsConstraint = itemsConstraint;
			return this;
		}

	}

	/**
	 * Numeric constraints (min, max, multipleOf).
	 */
	public static class NumericConstraint {

		private Double minimum;

		private Double maximum;

		private boolean exclusiveMinimum;

		private boolean exclusiveMaximum;

		private Double multipleOf;

		public Double getMinimum() {
			return minimum;
		}

		public NumericConstraint setMinimum(Double minimum) {
			this.minimum = minimum;
			return this;
		}

		public Double getMaximum() {
			return maximum;
		}

		public NumericConstraint setMaximum(Double maximum) {
			this.maximum = maximum;
			return this;
		}

		public boolean isExclusiveMinimum() {
			return exclusiveMinimum;
		}

		public NumericConstraint setExclusiveMinimum(boolean exclusiveMinimum) {
			this.exclusiveMinimum = exclusiveMinimum;
			return this;
		}

		public boolean isExclusiveMaximum() {
			return exclusiveMaximum;
		}

		public NumericConstraint setExclusiveMaximum(boolean exclusiveMaximum) {
			this.exclusiveMaximum = exclusiveMaximum;
			return this;
		}

		public Double getMultipleOf() {
			return multipleOf;
		}

		public NumericConstraint setMultipleOf(Double multipleOf) {
			this.multipleOf = multipleOf;
			return this;
		}

	}

	/**
	 * String constraints (minLength, maxLength, pattern).
	 */
	public static class StringConstraint {

		private Integer minLength;

		private Integer maxLength;

		private String pattern;

		public Integer getMinLength() {
			return minLength;
		}

		public StringConstraint setMinLength(Integer minLength) {
			this.minLength = minLength;
			return this;
		}

		public Integer getMaxLength() {
			return maxLength;
		}

		public StringConstraint setMaxLength(Integer maxLength) {
			this.maxLength = maxLength;
			return this;
		}

		public String getPattern() {
			return pattern;
		}

		public StringConstraint setPattern(String pattern) {
			this.pattern = pattern;
			return this;
		}

	}

	/**
	 * Array constraints (minItems, maxItems, uniqueItems).
	 */
	public static class ArrayConstraint {

		private Integer minItems;

		private Integer maxItems;

		private boolean uniqueItems;

		public Integer getMinItems() {
			return minItems;
		}

		public ArrayConstraint setMinItems(Integer minItems) {
			this.minItems = minItems;
			return this;
		}

		public Integer getMaxItems() {
			return maxItems;
		}

		public ArrayConstraint setMaxItems(Integer maxItems) {
			this.maxItems = maxItems;
			return this;
		}

		public boolean isUniqueItems() {
			return uniqueItems;
		}

		public ArrayConstraint setUniqueItems(boolean uniqueItems) {
			this.uniqueItems = uniqueItems;
			return this;
		}

	}

}
