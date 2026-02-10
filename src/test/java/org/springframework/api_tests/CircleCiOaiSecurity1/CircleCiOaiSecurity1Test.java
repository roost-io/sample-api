
package org.springframework.api_tests.CircleCiOaiSecurity1;

import com.intuit.karate.Results;
import com.intuit.karate.Runner;
// import com.intuit.karate.http.HttpServer;
// import com.intuit.karate.http.ServerConfig;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class CircleCiOaiSecurity1Test {

	@Test
	void testAll() {
		String APIHOST = System.getenv().get("API_HOST");
		String circletoken = System.getenv().get("circle-token");
		Results results = Runner.path("src/test/java/org/springframework/api_tests/CircleCiOaiSecurity1")
			.systemProperty("API_HOST", APIHOST)
			.systemProperty("circle-token", circletoken)
			.reportDir("testReport")
			.parallel(1);
		assertEquals(0, results.getFailCount(), results.getErrorMessages());
	}

}
