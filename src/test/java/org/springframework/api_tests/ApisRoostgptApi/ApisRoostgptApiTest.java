
package org.springframework.api_tests;

import com.intuit.karate.Results;
import com.intuit.karate.Runner;
// import com.intuit.karate.http.HttpServer;
// import com.intuit.karate.http.ServerConfig;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class ApisRoostgptApiTest {

	@Test
	void testAll() {
		String apihost = System.getenv().get("API_HOST");
		String bearer = System.getenv().get("BEARER");
		Results results = Runner.path("src/test/java/org/springframework/api_tests/ApisRoostgptApi")
			.systemProperty("API_HOST", apihost)
			.systemProperty("BEARER", bearer)
			.reportDir("testReport")
			.parallel(1);
		assertEquals(0, results.getFailCount(), results.getErrorMessages());
	}

}
