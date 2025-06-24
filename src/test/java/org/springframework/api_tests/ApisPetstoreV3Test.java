
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
		String apiHostServer = System.getenv().getOrDefault("petapp_URL_BASE", "https://petstore3.swagger.io/api/v3/");
		String petappauthtoken = System.getenv().getOrDefault("petapp_AUTH_TOKEN", "dummy_petapp_AUTH_TOKEN");
		Results results = Runner.path("src/test/java/org/springframework/api_tests/ApisPetstoreV3")
			.systemProperty("petapp_URL_BASE", apiHostServer)
			.systemProperty("petapp_AUTH_TOKEN", petappauthtoken)
			.reportDir("testReport")
			.parallel(1);
		assertEquals(0, results.getFailCount(), results.getErrorMessages());
	}

}
