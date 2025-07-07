
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
		String apihosturl = System.getenv().get("api_host_url");
		String authtoken = System.getenv().get("AUTH_TOKEN");
		String circletoken = System.getenv().get("circle-token");
		String circletoken = System.getenv().get("Circle-Token");
		Results results = Runner.path("src/test/java/org/springframework/api_tests/CircleCiOaiSecurity")
			.systemProperty("api_host_url", apihosturl)
			.systemProperty("AUTH_TOKEN", authtoken)
			.systemProperty("circle-token", circletoken)
			.systemProperty("Circle-Token", circletoken)
			.reportDir("testReport")
			.parallel(1);
		assertEquals(0, results.getFailCount(), results.getErrorMessages());
	}

}
