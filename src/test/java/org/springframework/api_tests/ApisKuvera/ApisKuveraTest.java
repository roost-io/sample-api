
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
		String kuveraapihost = System.getenv().get("KUVERA_API_HOST");
		String kuverabearertoken = System.getenv().get("KUVERA_BEARER_TOKEN");
		Results results = Runner.path("src/test/java/org/springframework/api_tests/ApisKuvera")
			.systemProperty("KUVERA_API_HOST", kuveraapihost)
			.systemProperty("KUVERA_BEARER_TOKEN", kuverabearertoken)
			.reportDir("testReport")
			.parallel(1);
		assertEquals(0, results.getFailCount(), results.getErrorMessages());
	}

}
