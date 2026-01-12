
package org.springframework.RoostTest;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.*;

public class TestdataLoader {

    private Properties properties = new Properties();

    private String fromENV(String name) {
        return System.getenv(name);
    }

    private void loadPropertiesFile() {
        String propertiesFileName = this.fromENV("PROPERTIES_FILE");
        InputStream content = null;
        try {
            if (propertiesFileName == null || propertiesFileName.isEmpty()) {
                content = getClass().getClassLoader().getResourceAsStream("application.properties");
            } else if (propertiesFileName.contains(File.separator)) {
                content = new FileInputStream(propertiesFileName);
            } else {
                content = getClass().getClassLoader().getResourceAsStream(propertiesFileName);
            }

            if (content != null) {
                this.properties.load(content);
            } else {
                System.out.println("No properties file found to load.");
            }
        } catch (IOException e) {
            System.out.println("Failed to load properties file: " + e.getMessage());
        }
    }

    private String fromPropertiesFile(String name) {
        return properties.getProperty(name);
    }

    private String resolveVariable(String value) {
        if (value == null || !value.contains("${")) return value;

        int start = value.indexOf("${");
        int end = value.indexOf("}", start);
        while (start != -1 && end != -1) {
            String key = value.substring(start + 2, end);
            String resolvedValue = fromENV(key);
            if (resolvedValue == null) resolvedValue = fromPropertiesFile(key);
            if (resolvedValue != null) {
                value = value.replace("${" + key + "}", resolvedValue);
            }
            start = value.indexOf("${", end);
            end = value.indexOf("}", start);
        }
        return value;
    }

    private Object resolveRecursive(Object input) {
        if (input instanceof JSONObject) {
            JSONObject inputObj = (JSONObject) input;
            JSONObject resolvedObj = new JSONObject();
            for (String key : inputObj.keySet()) {
                resolvedObj.put(key, resolveRecursive(inputObj.get(key)));
            }
            return resolvedObj;
        } else if (input instanceof JSONArray) {
            JSONArray inputArr = (JSONArray) input;
            JSONArray resolvedArr = new JSONArray();
            for (int i = 0; i < inputArr.length(); i++) {
                resolvedArr.put(resolveRecursive(inputArr.get(i)));
            }
            return resolvedArr;
        } else if (input instanceof String) {
            return resolveVariable((String) input);
        } else {
            return input;
        }
    }

    public List<JSONObject> loadJson(String jsonFilePath) {
        List<JSONObject> testCases = new ArrayList<>();
        this.loadPropertiesFile();

        try {
            String content = new String(Files.readAllBytes(Paths.get(jsonFilePath)));
            JSONArray arr = new JSONArray(content);
            for (int i = 0; i < arr.length(); i++) {
                JSONObject original = arr.getJSONObject(i);
                JSONObject resolved = (JSONObject) resolveRecursive(original);
                testCases.add(resolved);
            }
        } catch (IOException e) {
            System.out.println("Error loading JSON test data: " + e.getMessage());
        }

        return testCases;
    }
}
