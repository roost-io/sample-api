
package org.springframework.api_tests;

import com.intuit.karate.Results;
import com.intuit.karate.Runner;
// import com.intuit.karate.http.HttpServer;
// import com.intuit.karate.http.ServerConfig;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class SwaggerTest {

	@Test
	void testAll() {
		String apiHostServer = System.getenv().getOrDefault("URL_BASE", "http://127.0.0.1:4010");
		String authtoken = System.getenv().getOrDefault("AUTH_TOKEN", "dummy_AUTH_TOKEN");
		Results results = Runner.path("src/test/java/org/springframework/api_tests/Swagger")
			.systemProperty("URL_BASE", apiHostServer)
			.systemProperty("AUTH_TOKEN", authtoken)
			.reportDir("testReport")
			.parallel(1);
		assertEquals(0, results.getFailCount(), results.getErrorMessages());
	}

}
