
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
		String apihosturl = System.getenv().get("API_HOST_URL");
		String apiauthusername = System.getenv().get("API_AUTH_USERNAME");
		String api2authpassword = System.getenv().get("API2_AUTH_PASSWORD");
		String circletoken = System.getenv().get("CIRCLE-TOKEN");
		Results results = Runner.path("src/test/java/org/springframework/api_tests/CircleCiOaiSecurity")
			.systemProperty("API_HOST_URL", apihosturl)
			.systemProperty("API_AUTH_USERNAME", apiauthusername)
			.systemProperty("API2_AUTH_PASSWORD", api2authpassword)
			.systemProperty("CIRCLE-TOKEN", circletoken)
			.reportDir("testReport")
			.parallel(1);
		assertEquals(0, results.getFailCount(), results.getErrorMessages());
	}

}
