
package org.springframework.api_tests;

import com.intuit.karate.Results;
import com.intuit.karate.Runner;
// import com.intuit.karate.http.HttpServer;
// import com.intuit.karate.http.ServerConfig;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class ApisPetstoreV3Test {

	@Test
	void testAll() {
		String petstoreapihost = System.getenv().get("PETSTORE_API_HOST");
		String petstoreauthtoken = System.getenv().get("PETSTORE_AUTH_TOKEN");
		String apikey = System.getenv().get("API_KEY");
		Results results = Runner.path("src/test/java/org/springframework/api_tests/ApisPetstoreV3")
			.systemProperty("PETSTORE_API_HOST", petstoreapihost)
			.systemProperty("PETSTORE_AUTH_TOKEN", petstoreauthtoken)
			.systemProperty("API_KEY", apikey)
			.reportDir("testReport")
			.parallel(1);
		assertEquals(0, results.getFailCount(), results.getErrorMessages());
	}

}
