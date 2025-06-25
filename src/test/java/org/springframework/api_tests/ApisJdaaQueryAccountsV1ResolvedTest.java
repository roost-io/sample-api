
package org.springframework.api_tests;

import com.intuit.karate.Results;
import com.intuit.karate.Runner;
// import com.intuit.karate.http.HttpServer;
// import com.intuit.karate.http.ServerConfig;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class ApisJdaaQueryAccountsV1ResolvedTest {

	@Test
	void testAll() {
		String apiHostServer = System.getenv().getOrDefault("accounts_URL_BASE", "https://myaccount.com");
		String accountsauthtoken = System.getenv().getOrDefault("accounts_AUTH_TOKEN", "mycustomtoken");
		Results results = Runner.path("src/test/java/org/springframework/api_tests/ApisJdaaQueryAccountsV1Resolved")
			.systemProperty("accounts_URL_BASE", apiHostServer)
			.systemProperty("accounts_AUTH_TOKEN", accountsauthtoken)
			.reportDir("testReport")
			.parallel(1);
		assertEquals(0, results.getFailCount(), results.getErrorMessages());
	}

}
