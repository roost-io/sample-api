
    package org.springframework.integration_tests;
  
    import com.intuit.karate.Results;
    import com.intuit.karate.Runner;
    // import com.intuit.karate.http.HttpServer;
    // import com.intuit.karate.http.ServerConfig;
    import org.junit.jupiter.api.Test;
  
    import static org.junit.jupiter.api.Assertions.assertEquals;
  
    class FeatureFileGherkinCredentialAllTest {
  
        @Test
        void testAll() {
            String swagger_184f1d2b61_url = System.getenv().getOrDefault("SWAGGER_184F1D2B61_URL", "https://127.0.0.1:4010");
String rafaelmathieu_income_calculator_api_2_0_0_swagger_ef8a7d9541_url = System.getenv().getOrDefault("RAFAELMATHIEU_INCOME_CALCULATOR_API_2_0_0_SWAGGER_EF8A7D9541_URL", "https://127.0.0.1:4011");
String auth_token = System.getenv().getOrDefault("AUTH_TOKEN", "dummy_AUTH_TOKEN");
            Results results = Runner.path("src/test/java/org/springframework/integration_tests/FeatureFileGherkinCredentialAll")
                    .systemProperty("SWAGGER_184F1D2B61_URL",swagger_184f1d2b61_url)
.systemProperty("RAFAELMATHIEU_INCOME_CALCULATOR_API_2_0_0_SWAGGER_EF8A7D9541_URL",rafaelmathieu_income_calculator_api_2_0_0_swagger_ef8a7d9541_url)
.systemProperty("AUTH_TOKEN", auth_token)
                    .reportDir("testReport").parallel(1);
            assertEquals(0, results.getFailCount(), results.getErrorMessages());
        }
  
    }
