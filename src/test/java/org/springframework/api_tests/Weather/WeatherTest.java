
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
		String APIHOST = System.getenv().get("API_HOST");
		String key = System.getenv().get("key");
		Results results = Runner.path("src/test/java/org/springframework/api_tests/Weather")
			.systemProperty("API_HOST", APIHOST)
			.systemProperty("key", key)
			.reportDir("testReport")
			.parallel(1);
		assertEquals(0, results.getFailCount(), results.getErrorMessages());
	}

}
