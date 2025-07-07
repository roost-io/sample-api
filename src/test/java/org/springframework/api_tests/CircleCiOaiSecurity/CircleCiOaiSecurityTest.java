
package org.springframework.api_tests.CircleCiOaiSecurity;

import com.intuit.karate.Results;
import com.intuit.karate.Runner;
// import com.intuit.karate.http.HttpServer;
// import com.intuit.karate.http.ServerConfig;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class CircleCiOaiSecurityTest {

	@Test
	void testAll() {
		String apibaseurl = System.getenv().get("API_BASE_URL");
		String authtoken = System.getenv().get("AUTH_TOKEN");
		String circletoken = System.getenv().get("CIRCLE-TOKEN");
		Results results = Runner.path("src/test/java/org/springframework/api_tests/CircleCiOaiSecurity")
			.systemProperty("API_BASE_URL", apibaseurl)
			.systemProperty("AUTH_TOKEN", authtoken)
			.systemProperty("CIRCLE-TOKEN", circletoken)
			.reportDir("testReport")
			.parallel(1);
		assertEquals(0, results.getFailCount(), results.getErrorMessages());
	}

}
