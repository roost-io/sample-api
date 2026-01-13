
package org.springframework.api_tests.CircleCi;

import com.intuit.karate.Results;
import com.intuit.karate.Runner;
// import com.intuit.karate.http.HttpServer;
// import com.intuit.karate.http.ServerConfig;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class CircleCiTest {

	@Test
	void testAll() {
		String apihost = System.getenv().get("API_HOST");
		String circleuser = System.getenv().get("CIRCLE_USER");
		String circlepass = System.getenv().get("CIRCLE_PASS");
		Results results = Runner.path("src/test/java/org/springframework/api_tests/CircleCi")
			.systemProperty("API_HOST", apihost)
			.systemProperty("CIRCLE_USER", circleuser)
			.systemProperty("CIRCLE_PASS", circlepass)
			.reportDir("testReport")
			.parallel(1);
		assertEquals(0, results.getFailCount(), results.getErrorMessages());
	}

}
