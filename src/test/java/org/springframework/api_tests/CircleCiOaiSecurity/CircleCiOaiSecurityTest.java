
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
		String APIHOSTURL = System.getenv().get("API_HOST_URL");
		String BASICUSERNAME = System.getenv().get("BASIC_USER_NAME");
		String BASICPASSWORD = System.getenv().get("BASIC_PASSWORD");
		String circletoken = System.getenv().get("circle-token");
		String CircleToken = System.getenv().get("Circle-Token");
		Results results = Runner.path("src/test/java/org/springframework/api_tests/CircleCiOaiSecurity")
			.systemProperty("API_HOST_URL", APIHOSTURL)
			.systemProperty("BASIC_USER_NAME", BASICUSERNAME)
			.systemProperty("BASIC_PASSWORD", BASICPASSWORD)
			.systemProperty("circle-token", circletoken)
			.systemProperty("Circle-Token", CircleToken)
			.reportDir("testReport")
			.parallel(1);
		assertEquals(0, results.getFailCount(), results.getErrorMessages());
	}

}
