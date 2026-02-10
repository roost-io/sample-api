
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
		String authtoken = System.getenv()
			.getOrDefault("AUTH_TOKEN",
					"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFrc2hhdC5qYWluIiwiaWF0IjoxNzI4OTgxMTY1LCJleHAiOjE3Mjk1ODU5NjV9.g_c5b13E-LNjo6NfiZqtUTlcWrCqcrj8EXAJanf43a8");
		Results results = Runner.path("src/test/java/org/springframework/api_tests/ApisNobel")
			.systemProperty("URL_BASE", apiHostServer)
			.systemProperty("AUTH_TOKEN", authtoken)
			.reportDir("testReport")
			.parallel(1);
		assertEquals(0, results.getFailCount(), results.getErrorMessages());
	}

}
