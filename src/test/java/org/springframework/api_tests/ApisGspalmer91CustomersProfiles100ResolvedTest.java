
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
		String apiHostServer = System.getenv()
			.getOrDefault("customer_profile_URL_BASE", "https://customer-profile.com/v2/");
		String customerprofileauthtoken = System.getenv()
			.getOrDefault("customer_profile_AUTH_TOKEN", "dummy_customer_profile_AUTH_TOKEN");
		Results results = Runner
			.path("src/test/java/org/springframework/api_tests/ApisGspalmer91CustomersProfiles100Resolved")
			.systemProperty("customer_profile_URL_BASE", apiHostServer)
			.systemProperty("customer_profile_AUTH_TOKEN", customerprofileauthtoken)
			.reportDir("testReport")
			.parallel(1);
		assertEquals(0, results.getFailCount(), results.getErrorMessages());
	}

}
