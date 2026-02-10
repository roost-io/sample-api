
package org.springframework.api_tests;

import com.intuit.karate.Results;
import com.intuit.karate.Runner;
// import com.intuit.karate.http.HttpServer;
// import com.intuit.karate.http.ServerConfig;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class ApisGspalmer91CustomersProfiles100ResolvedTest {

	@Test
	void testAll() {
		String apiHostServer = System.getenv().getOrDefault("customer_URL_BASE", "https://mycustomer.com");
		String customerauthtoken = System.getenv().getOrDefault("customer_AUTH_TOKEN", "dummy_customer_AUTH_TOKEN");
		Results results = Runner
			.path("src/test/java/org/springframework/api_tests/ApisGspalmer91CustomersProfiles100Resolved")
			.systemProperty("customer_URL_BASE", apiHostServer)
			.systemProperty("customer_AUTH_TOKEN", customerauthtoken)
			.reportDir("testReport")
			.parallel(1);
		assertEquals(0, results.getFailCount(), results.getErrorMessages());
	}

}
