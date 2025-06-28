
package org.springframework.api_tests;

import com.intuit.karate.Results;
import com.intuit.karate.Runner;
// import com.intuit.karate.http.HttpServer;
// import com.intuit.karate.http.ServerConfig;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class ApisKuveraTest {

	@Test
	void testAll() {
		String urlbase = System.getenv().get("URL_BASE");
		String authtoken = System.getenv().get("AUTH_TOKEN");
		Results results = Runner.path("src/test/java/org/springframework/api_tests/ApisKuvera")
			.systemProperty("URL_BASE", urlbase)
			.systemProperty("AUTH_TOKEN", authtoken)
			.reportDir("testReport")
			.parallel(1);
		assertEquals(0, results.getFailCount(), results.getErrorMessages());
	}

}
