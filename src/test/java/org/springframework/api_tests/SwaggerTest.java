
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
		String apiHostServer = System.getenv()
			.getOrDefault("userprofile-file_URL_BASE", "https://userprofile-file.com");
		String userprofilefileauthtoken = System.getenv()
			.getOrDefault("userprofile-file_AUTH_TOKEN", "dummy_userprofile-file_AUTH_TOKEN");
		String apiHostServer = System.getenv()
			.getOrDefault("userprofile-file_ACCOUNT_JDAA_URL_BASE", "http://127.0.0.1:4010");
		String userprofilefileaccountjdaaauthtoken = System.getenv()
			.getOrDefault("userprofile-file_ACCOUNT_JDAA_AUTH_TOKEN", "dummy_userprofile-file_ACCOUNT_JDAA_AUTH_TOKEN");
		Results results = Runner.path("src/test/java/org/springframework/api_tests/Swagger")
			.systemProperty("userprofile-file_URL_BASE", apiHostServer)
			.systemProperty("userprofile-file_AUTH_TOKEN", userprofilefileauthtoken)
			.systemProperty("userprofile-file_ACCOUNT_JDAA_URL_BASE", apiHostServer)
			.systemProperty("userprofile-file_ACCOUNT_JDAA_AUTH_TOKEN", userprofilefileaccountjdaaauthtoken)
			.reportDir("testReport")
			.parallel(1);
		assertEquals(0, results.getFailCount(), results.getErrorMessages());
	}

}
