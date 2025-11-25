package com.backend.careercatalyst.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class WebConfig {

    @Bean
    public WebMvcConfigurer corsConfigurer() {
        return new WebMvcConfigurer() {
            @Override
            public void addCorsMappings(CorsRegistry registry) {
                // Changed from "/api/**" to "/**" to cover ALL endpoints (including auth)
                registry.addMapping("/**") 
                        .allowedOrigins(
                            "https://career-catalyst-frontend.onrender.com",
                            "http://localhost:3000",
                            "http://localhost:5173"
                        )
                        .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
                        .allowedHeaders("*")
                        .allowCredentials(true)
                        .maxAge(3600); // Cache the CORS response for 1 hour to reduce traffic
            }
        };
    }
}