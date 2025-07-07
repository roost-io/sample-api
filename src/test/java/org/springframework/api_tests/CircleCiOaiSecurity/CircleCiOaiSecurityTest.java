
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
		String authtoken = System.getenv().get("AUTH_TOKEN");
		Results results = Runner.path("src/test/java/org/springframework/api_tests/CircleCiOaiSecurity")
			.systemProperty("API_HOST_URL", apihosturl)
			.systemProperty("AUTH_TOKEN", authtoken)
			.reportDir("testReport")
			.parallel(1);
		assertEquals(0, results.getFailCount(), results.getErrorMessages());
	}

}
