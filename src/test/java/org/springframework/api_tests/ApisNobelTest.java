
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
		String apiHostServer = System.getenv().getOrDefault("URL_BASE", "http://127.0.0.1:4010");
		Results results = Runner.path("src/test/java/org/springframework/api_tests/ApisNobel")
			.systemProperty("URL_BASE", apiHostServer)
			.reportDir("testReport")
			.parallel(1);
		assertEquals(0, results.getFailCount(), results.getErrorMessages());
	}

}
