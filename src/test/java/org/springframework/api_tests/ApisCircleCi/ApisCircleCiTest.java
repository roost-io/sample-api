
package org.springframework.api_tests.ApisCircleCi;

import com.intuit.karate.Results;
import com.intuit.karate.Runner;
// import com.intuit.karate.http.HttpServer;
// import com.intuit.karate.http.ServerConfig;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class ApisCircleCiTest {

	@Test
	void testAll() {
		String APIHOST = System.getenv().get("API_HOST");
		String CircleToken = System.getenv().get("Circle-Token");
		String AUTHTOKEN = System.getenv().get("AUTH_TOKEN");
		Results results = Runner.path("src/test/java/org/springframework/api_tests/ApisCircleCi")
			.systemProperty("API_HOST", APIHOST)
			.systemProperty("Circle-Token", CircleToken)
			.systemProperty("AUTH_TOKEN", AUTHTOKEN)
			.reportDir("testReport")
			.parallel(1);
		assertEquals(0, results.getFailCount(), results.getErrorMessages());
	}

}
