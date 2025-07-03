
package org.springframework.api_tests;

import com.intuit.karate.Results;
import com.intuit.karate.Runner;
// import com.intuit.karate.http.HttpServer;
// import com.intuit.karate.http.ServerConfig;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class ApisSmarterSortingMarketplaceApi008ResolvedTest {

	@Test
	void testAll() {
		String apihost = System.getenv().get("API_HOST");
		String apikey = System.getenv().get("API_KEY");
		Results results = Runner
			.path("src/test/java/org/springframework/api_tests/ApisSmarterSortingMarketplaceApi008Resolved")
			.systemProperty("API_HOST", apihost)
			.systemProperty("API_KEY", apikey)
			.reportDir("testReport")
			.parallel(1);
		assertEquals(0, results.getFailCount(), results.getErrorMessages());
	}

}
