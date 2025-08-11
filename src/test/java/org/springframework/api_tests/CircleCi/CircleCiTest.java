
package org.springframework.api_tests;

import com.intuit.karate.Results;
import com.intuit.karate.Runner;
// import com.intuit.karate.http.HttpServer;
// import com.intuit.karate.http.ServerConfig;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class CircleCiTest {

	@Test
	void testAll() {
		String urlbase = System.getenv().get("URL_BASE");
		Results results = Runner.path("src/test/java/org/springframework/api_tests/CircleCi")
			.systemProperty("URL_BASE", urlbase)
			.reportDir("testReport")
			.parallel(1);
		assertEquals(0, results.getFailCount(), results.getErrorMessages());
	}

}
