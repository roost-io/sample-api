
package org.springframework.api_tests.Weather;

import com.intuit.karate.Results;
import com.intuit.karate.Runner;
// import com.intuit.karate.http.HttpServer;
// import com.intuit.karate.http.ServerConfig;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class WeatherTest {

	@Test
	void testAll() {
		String apihost = System.getenv().get("API_HOST");
		String authtoken = System.getenv().get("AUTH_TOKEN");
		String key = System.getenv().get("KEY");
		String exceededquotatoken = System.getenv().get("EXCEEDED_QUOTA_TOKEN");
		Results results = Runner.path("src/test/java/org/springframework/api_tests/Weather")
			.systemProperty("API_HOST", apihost)
			.systemProperty("AUTH_TOKEN", authtoken)
			.systemProperty("KEY", key)
			.systemProperty("EXCEEDED_QUOTA_TOKEN", exceededquotatoken)
			.reportDir("testReport")
			.parallel(1);
		assertEquals(0, results.getFailCount(), results.getErrorMessages());
	}

}
