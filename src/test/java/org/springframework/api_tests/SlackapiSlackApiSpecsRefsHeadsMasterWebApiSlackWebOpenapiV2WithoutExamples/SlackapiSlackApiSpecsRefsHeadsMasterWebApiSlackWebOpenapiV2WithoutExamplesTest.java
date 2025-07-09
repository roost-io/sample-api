
package org.springframework.api_tests.SlackapiSlackApiSpecsRefsHeadsMasterWebApiSlackWebOpenapiV2WithoutExamples;

import com.intuit.karate.Results;
import com.intuit.karate.Runner;
// import com.intuit.karate.http.HttpServer;
// import com.intuit.karate.http.ServerConfig;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class SlackapiSlackApiSpecsRefsHeadsMasterWebApiSlackWebOpenapiV2WithoutExamplesTest {

	@Test
	void testAll() {
		String APIHOST = System.getenv().get("API_HOST");
		String AUTHTOKEN = System.getenv().get("AUTH_TOKEN");
		Results results = Runner.path(
				"src/test/java/org/springframework/api_tests/SlackapiSlackApiSpecsRefsHeadsMasterWebApiSlackWebOpenapiV2WithoutExamples")
			.systemProperty("API_HOST", APIHOST)
			.systemProperty("AUTH_TOKEN", AUTHTOKEN)
			.reportDir("testReport")
			.parallel(1);
		assertEquals(0, results.getFailCount(), results.getErrorMessages());
	}

}
