
package org.springframework.api_tests.CircleciOai4SecureEndpointsCopy;

import com.intuit.karate.Results;
import com.intuit.karate.Runner;
// import com.intuit.karate.http.HttpServer;
// import com.intuit.karate.http.ServerConfig;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class CircleciOai4SecureEndpointsCopyTest {

	@Test
	void testAll() {
		String APIHOSTURL = System.getenv().get("API_HOST_URL");
		String circletoken = System.getenv().get("circle-token");
		String CircleToken = System.getenv().get("Circle-Token");
		String APIAUTHUSERNAME = System.getenv().get("API_AUTH_USERNAME");
		String APIAUTHPASSWORD = System.getenv().get("API_AUTH_PASSWORD");
		Results results = Runner.path("src/test/java/org/springframework/api_tests/CircleciOai4SecureEndpointsCopy")
			.systemProperty("API_HOST_URL", APIHOSTURL)
			.systemProperty("circle-token", circletoken)
			.systemProperty("Circle-Token", CircleToken)
			.systemProperty("API_AUTH_USERNAME", APIAUTHUSERNAME)
			.systemProperty("API_AUTH_PASSWORD", APIAUTHPASSWORD)
			.reportDir("testReport")
			.parallel(1);
		assertEquals(0, results.getFailCount(), results.getErrorMessages());
	}

}
