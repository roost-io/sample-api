
package org.springframework.api_tests;

import com.intuit.karate.Results;
import com.intuit.karate.Runner;
// import com.intuit.karate.http.HttpServer;
// import com.intuit.karate.http.ServerConfig;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class ApisJdaaQueryAccountsV1ResolvedTest {

	@Test
	void testAll() {
		String urlbase = System.getenv().getOrDefault("url_base", "dummy_url_base");
		String authtoken = System.getenv().getOrDefault("AUTH_TOKEN", "dummy_AUTH_TOKEN");
		Results results = Runner.path("src/test/java/org/springframework/api_tests/ApisJdaaQueryAccountsV1Resolved")
			.systemProperty("url_base", urlbase)
			.systemProperty("AUTH_TOKEN", authtoken)
			.reportDir("testReport")
			.parallel(1);
		assertEquals(0, results.getFailCount(), results.getErrorMessages());
	}

}
