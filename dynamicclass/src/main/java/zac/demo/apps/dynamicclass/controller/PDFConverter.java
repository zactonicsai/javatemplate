package zac.demo.apps.dynamicclass.controller;

import org.springframework.stereotype.Component;

@Component
public class PDFConverter implements DocConverter {
    @Override
    public void convert(String input, String output) {
        // PDF conversion logic
    }
    
    @Override
    public String getSupportedType() {
        return "pdf";
    }
}

/* 
@Component
public class DOCXConverter implements DocConverter {
    @Override
    public void convert(String input, String output) {
        // DOCX conversion logic
    }
    
    @Override
    public String getSupportedType() {
        return "docx";
    }
}

@Component
public class MDConverter implements DocConverter {
    @Override
    public void convert(String input, String output) {
        // Markdown conversion logic
    }
    
    @Override
    public String getSupportedType() {
        return "md";
    }
     
}
*/