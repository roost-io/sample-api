
package org.springframework.api_tests;

import com.intuit.karate.Results;
import com.intuit.karate.Runner;
// import com.intuit.karate.http.HttpServer;
// import com.intuit.karate.http.ServerConfig;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class ApisNobelTest {

	@Test
	void testAll() {
		String apiHostServer = System.getenv().getOrDefault("URL1_URL_BASE", "ApiURL1");
		String url1authtoken = System.getenv().getOrDefault("URL1_AUTH_TOKEN", "dummy_URL1_AUTH_TOKEN");
		String url1url1authtoken = System.getenv().getOrDefault("URL1_URL1_AUTH_TOKEN", "dummy_URL1_URL1_AUTH_TOKEN");
		Results results = Runner.path("src/test/java/org/springframework/api_tests/ApisNobel")
			.systemProperty("URL1_URL_BASE", apiHostServer)
			.systemProperty("URL1_AUTH_TOKEN", url1authtoken)
			.systemProperty("URL1_URL1_AUTH_TOKEN", url1url1authtoken)
			.reportDir("testReport")
			.parallel(1);
		assertEquals(0, results.getFailCount(), results.getErrorMessages());
	}

}
