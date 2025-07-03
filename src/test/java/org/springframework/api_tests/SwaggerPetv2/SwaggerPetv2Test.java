
package org.springframework.api_tests.SwaggerPetv2;

import com.intuit.karate.Results;
import com.intuit.karate.Runner;
// import com.intuit.karate.http.HttpServer;
// import com.intuit.karate.http.ServerConfig;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class SwaggerPetv2Test {

	@Test
	void testAll() {
		String apihost = System.getenv().get("API_HOST");
		String authtoken = System.getenv().get("AUTH_TOKEN");
		Results results = Runner.path("src/test/java/org/springframework/api_tests/SwaggerPetv2")
			.systemProperty("API_HOST", apihost)
			.systemProperty("AUTH_TOKEN", authtoken)
			.reportDir("testReport")
			.parallel(1);
		assertEquals(0, results.getFailCount(), results.getErrorMessages());
	}

}
