package zac.demo.apps.dynamicclass;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import zac.example.converter.DocxConverter;

@Configuration
public class ConverterAutoConfiguration {
    
    
    @Bean
    public DocxConverter excelDocConverter() {
        return new DocxConverter();
    }
}
