// ********RoostGPT********
/*
Test generated by RoostGPT for test nobel-prize-rest-assured-api-spec-test using AI Type Open AI and AI Model gpt-4

Test generated for /nobelPrize/{category}/{year}_get for http method type GET in rest-assured framework

RoostTestHash=adfce3f1d2


*/

// ********RoostGPT********
package org.springframework.RoostTest;

import io.restassured.RestAssured;
import io.restassured.path.json.JsonPath;
import io.restassured.http.ContentType;
import io.restassured.response.Response;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static io.restassured.RestAssured.given;
import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.ArrayList;
import java.util.List;
import org.hamcrest.MatcherAssert;
import static org.hamcrest.Matchers.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.json.JSONObject;
import org.json.XML;
import org.json.JSONException;
import org.json.JSONArray;
import java.util.Arrays;

public class nobelPrizeCategoryYearGetTest {

	List<Map<String, String>> envList = new ArrayList<>();

	@BeforeEach
	public void setUp() {
		TestdataLoader dataloader = new TestdataLoader();
		String[] envVarsList = { "category", "year" };
		envList = dataloader.load("src/test/java/org/springframework/RoostTest/nobelPrize_category_yearGetTest.csv",
				envVarsList);
	}

	@Test
	public void nobelPrizeCategoryYearGet_Test() throws JSONException {
		this.setUp();
		Integer testNumber = 1;
		for (Map<String, String> testData : envList) {
			RestAssured.baseURI = (testData.get("BASE_URL") != null && !testData.get("BASE_URL").isEmpty())
					? testData.get("BASE_URL") : "http://api.nobelprize.org/2.1";

			Response responseObj = given()
				.pathParam("category", testData.get("category") != null ? testData.get("category") : "")
				.pathParam("year", testData.get("year") != null ? testData.get("year") : "")
				.when()
				.get("/nobelPrize/{category}/{year}")
				.then()
				.extract()
				.response();
			JsonPath response;
			String contentType = responseObj.getContentType();

			System.out.printf("Test Case %d: nobelPrizeCategoryYearGet_Test \n", testNumber++);
			System.out.println("Request: GET /nobelPrize/{category}/{year}");
			System.out.println("Status Code: " + responseObj.statusCode());
			if (testData.get("statusCode") != null) {
				String statusCodeFromCSV = testData.get("statusCode");
				if (statusCodeFromCSV.contains("X")) {
					MatcherAssert.assertThat(
							"Expected a status code of category " + statusCodeFromCSV + ", but got "
									+ Integer.toString(responseObj.statusCode()) + " instead",
							Integer.toString(responseObj.statusCode()).charAt(0), equalTo(statusCodeFromCSV.charAt(0)));
				}
				else {
					MatcherAssert.assertThat(Integer.toString(responseObj.statusCode()), equalTo(statusCodeFromCSV));
				}
			}
			else {
				List<Integer> expectedStatusCodes = Arrays.asList(200, 400, 404, 422);
				MatcherAssert.assertThat(responseObj.statusCode(), is(in(expectedStatusCodes)));
			}
			String stringifiedStatusCode = "";
			if (contentType.contains("application/xml") || contentType.contains("text/xml")) {
				String xmlResponse = responseObj.asString();
				JSONObject jsonResponse = XML.toJSONObject(xmlResponse);
				JSONObject jsonData = jsonResponse.getJSONObject("xml");
				String jsonString = jsonData.toString();
				response = new JsonPath(jsonString);

			}
			else if (contentType.contains("application/json")) {
				response = responseObj.jsonPath();
			}
			else {
				System.out.println("Response content type found: " + contentType
						+ ", but RoostGPT currently only supports the following response content types: application/json,text/xml,application/xml");
				continue;
			}

			if (stringifiedStatusCode == "200") {
				System.out.println("Description: Successful call of the Nobel Prize giving the category and year");

				if (response.get("nobelPrize") != null) {
					if (response.get("nobelPrize.awardYear") != null) {
						MatcherAssert.assertThat(response.get("nobelPrize.awardYear"), instanceOf(Integer.class));
					}

					if (response.get("nobelPrize.category") != null) {
						if (response.get("nobelPrize.category.en") != null) {
							MatcherAssert.assertThat(response.get("nobelPrize.category.en"), instanceOf(String.class));
						}

						if (response.get("nobelPrize.category.se") != null) {
							MatcherAssert.assertThat(response.get("nobelPrize.category.se"), instanceOf(String.class));
						}

						if (response.get("nobelPrize.category.false") != null) {
							MatcherAssert.assertThat(response.get("nobelPrize.category.false"),
									instanceOf(String.class));
						}

					}

					if (response.get("nobelPrize.categoryFullName") != null) {
						if (response.get("nobelPrize.categoryFullName.en") != null) {
							MatcherAssert.assertThat(response.get("nobelPrize.categoryFullName.en"),
									instanceOf(String.class));
						}

						if (response.get("nobelPrize.categoryFullName.se") != null) {
							MatcherAssert.assertThat(response.get("nobelPrize.categoryFullName.se"),
									instanceOf(String.class));
						}

						if (response.get("nobelPrize.categoryFullName.false") != null) {
							MatcherAssert.assertThat(response.get("nobelPrize.categoryFullName.false"),
									instanceOf(String.class));
						}

					}

					if (response.get("nobelPrize.dateAwarded") != null) {
						MatcherAssert.assertThat(response.get("nobelPrize.dateAwarded"), instanceOf(String.class));
					}

					if (response.get("nobelPrize.prizeAmount") != null) {
						MatcherAssert.assertThat(response.get("nobelPrize.prizeAmount"), instanceOf(Integer.class));
					}

					if (response.get("nobelPrize.prizeAmountAdjusted") != null) {
						MatcherAssert.assertThat(response.get("nobelPrize.prizeAmountAdjusted"),
								instanceOf(Integer.class));
					}

					if (response.get("nobelPrize.topMotivation") != null) {
						if (response.get("nobelPrize.topMotivation.en") != null) {
							MatcherAssert.assertThat(response.get("nobelPrize.topMotivation.en"),
									instanceOf(String.class));
						}

						if (response.get("nobelPrize.topMotivation.se") != null) {
							MatcherAssert.assertThat(response.get("nobelPrize.topMotivation.se"),
									instanceOf(String.class));
						}

						if (response.get("nobelPrize.topMotivation.false") != null) {
							MatcherAssert.assertThat(response.get("nobelPrize.topMotivation.false"),
									instanceOf(String.class));
						}

					}

					if (response.get("nobelPrize.laureates") != null) {
						for (int i = 0; i < response.getList("nobelPrize.laureates").size(); i++) {
							if (response.get("nobelPrize.laureates[" + i + "].id") != null) {
								MatcherAssert.assertThat(response.get("nobelPrize.laureates[" + i + "].id"),
										instanceOf(Integer.class));
								MatcherAssert.assertThat(response.getDouble("nobelPrize.laureates[" + i + "].id"),
										greaterThanOrEqualTo(1));

							}

							if (response.get("nobelPrize.laureates[" + i + "].name") != null) {
							}

							if (response.get("nobelPrize.laureates[" + i + "].portion") != null) {
								MatcherAssert.assertThat(response.get("nobelPrize.laureates[" + i + "].portion"),
										instanceOf(String.class));
								MatcherAssert.assertThat(response.getString("nobelPrize.laureates[" + i + "].portion"),
										anyOf(equalTo("1"), equalTo("1/2"), equalTo("1/3"), equalTo("1/4")));

							}

							if (response.get("nobelPrize.laureates[" + i + "].sortOrder") != null) {
								MatcherAssert.assertThat(response.get("nobelPrize.laureates[" + i + "].sortOrder"),
										instanceOf(String.class));
								MatcherAssert.assertThat(
										response.getString("nobelPrize.laureates[" + i + "].sortOrder"),
										anyOf(equalTo("1"), equalTo("2"), equalTo("3")));

							}

							if (response.get("nobelPrize.laureates[" + i + "].motivation") != null) {
							}

							if (response.get("nobelPrize.laureates[" + i + "].links") != null) {
								for (int i1 = 0; i1 < response.getList("nobelPrize.laureates[" + i + "].links")
									.size(); i1++) {
								}
								MatcherAssert.assertThat(response.getList("nobelPrize.laureates[" + i + "].links"),
										instanceOf(List.class));

							}

						}
						MatcherAssert.assertThat(response.getList("nobelPrize.laureates"), instanceOf(List.class));

					}

				}
			}
			if (stringifiedStatusCode == "400") {
				System.out.println(
						"Description: Bad request.The request could not be understood by the server due to malformed syntax, modifications needed.");

				if (response.get("code") != null) {
					MatcherAssert.assertThat(response.get("code"), instanceOf(String.class));
				}

				if (response.get("message") != null) {
					MatcherAssert.assertThat(response.get("message"), instanceOf(String.class));
				}
			}
			if (stringifiedStatusCode == "404") {
				System.out.println(
						"Description: Not Found. The requested resource could not be found but may be available again in the future.");

				if (response.get("code") != null) {
					MatcherAssert.assertThat(response.get("code"), instanceOf(String.class));
				}

				if (response.get("message") != null) {
					MatcherAssert.assertThat(response.get("message"), instanceOf(String.class));
				}
			}
			if (stringifiedStatusCode == "422") {
				System.out.println(
						"Description: Unprocessable Entity. The request was well-formed but was unable to be followed due to semantic errors.");

				if (response.get("code") != null) {
					MatcherAssert.assertThat(response.get("code"), instanceOf(String.class));
				}

				if (response.get("message") != null) {
					MatcherAssert.assertThat(response.get("message"), instanceOf(String.class));
				}
			}

		}
	}

}
