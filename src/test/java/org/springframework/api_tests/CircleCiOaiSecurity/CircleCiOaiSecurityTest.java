
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
		String APIHOST = System.getenv().get("API_HOST");
		String AUTHUSERNAME = System.getenv().get("AUTH_USERNAME");
		String AUTHPASSWORD = System.getenv().get("AUTH_PASSWORD");
		String CircleToken = System.getenv().get("Circle-Token");
		String circletoken = System.getenv().get("circle-token");
		Results results = Runner.path("src/test/java/org/springframework/api_tests/CircleCiOaiSecurity")
			.systemProperty("API_HOST", APIHOST)
			.systemProperty("AUTH_USERNAME", AUTHUSERNAME)
			.systemProperty("AUTH_PASSWORD", AUTHPASSWORD)
			.systemProperty("Circle-Token", CircleToken)
			.systemProperty("circle-token", circletoken)
			.reportDir("testReport")
			.parallel(1);
		assertEquals(0, results.getFailCount(), results.getErrorMessages());
	}

}
