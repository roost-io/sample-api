
    package org.springframework.integration_tests;
  
    import com.intuit.karate.Results;
    import com.intuit.karate.Runner;
    // import com.intuit.karate.http.HttpServer;
    // import com.intuit.karate.http.ServerConfig;
    import org.junit.jupiter.api.Test;
  
    import static org.junit.jupiter.api.Assertions.assertEquals;
  
    class FeatureFilePetstoreV3CreateV3Test {
  
        @Test
        void testAll() {
            String petstore_v3_3273d64931_url = System.getenv().getOrDefault("PETSTORE_V3_3273D64931_URL", "http://localhost:4010");
String petstore_v3_3273d64931_auth_token = System.getenv().getOrDefault("PETSTORE_V3_3273D64931_AUTH_TOKEN", "dummy_PETSTORE_V3_3273D64931_AUTH_TOKEN");
            Results results = Runner.path("src/test/java/org/springframework/integration_tests/FeatureFilePetstoreV3CreateV3")
                    .systemProperty("PETSTORE_V3_3273D64931_URL",petstore_v3_3273d64931_url)
.systemProperty("PETSTORE_V3_3273D64931_AUTH_TOKEN", petstore_v3_3273d64931_auth_token)
                    .reportDir("testReport").parallel(1);
            assertEquals(0, results.getFailCount(), results.getErrorMessages());
        }
  
    }
