package zac.example.converter;
import org.springframework.stereotype.Component;

import zac.example.lib.DocConverter;

@Component
public class DocxConverter implements DocConverter {
    @Override
    public void convert(String input, String output) {
        // PDF conversion logic
    }
    
    @Override
    public String getSupportedType() {
        return "docx";
    }
}