
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
		String apiHostServer = System.getenv().getOrDefault("url1_nobel_URL_BASE", "https://api.nobelprize.org/2.1");
		String url1nobelauthtoken = System.getenv()
			.getOrDefault("url1_nobel_AUTH_TOKEN", "dummy_url1_nobel_AUTH_TOKEN");
		Results results = Runner.path("src/test/java/org/springframework/api_tests/ApisNobel")
			.systemProperty("url1_nobel_URL_BASE", apiHostServer)
			.systemProperty("url1_nobel_AUTH_TOKEN", url1nobelauthtoken)
			.reportDir("testReport")
			.parallel(1);
		assertEquals(0, results.getFailCount(), results.getErrorMessages());
	}

}
