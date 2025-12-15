package zac.demo.apps.dynamicclass.controller;

import jakarta.annotation.PostConstruct;
import zac.example.lib.DocConverter;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.ApplicationContext;
import org.springframework.context.ApplicationContextAware;
import org.springframework.stereotype.Component;

import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

@Component
public class DocConverterRegistry implements ApplicationContextAware {

    private static final Logger log = LoggerFactory.getLogger(DocConverterRegistry.class);

    private ApplicationContext applicationContext;

    private final Map<String, DocConverter> converters = new HashMap<>();

    // ✅ Null / no-args constructor
    public DocConverterRegistry() {
    }

    @Override
    public void setApplicationContext(ApplicationContext applicationContext) {
        this.applicationContext = applicationContext;
    }

    @PostConstruct
    public void init() {

        log.info("Post Construct *****************************");
        log.info("Post Construct *****************************");
        log.info("Post Construct *****************************");
        log.info("Post Construct *****************************");
        log.info("Post Construct *****************************");
    
        Map<String, DocConverter> beans = applicationContext.getBeansOfType(DocConverter.class);
       
        for (DocConverter converter : beans.values()) {
            String key = converter.getSupportedType();
            log.info(key);
             log.info("Post Construct *****************************");
            if (key == null || key.isBlank()) {
                throw new IllegalStateException(
                        "Converter " + converter.getClass().getName() +
                                " returned blank supportedType()");
            }

            DocConverter existing = converters.putIfAbsent(key, converter);
            if (existing != null) {
                throw new IllegalStateException(
                        "Duplicate DocConverter for type '" + key + "'");
            }
        }

        log.info("Registered DocConverters: {}", converters.keySet());
    }

    public DocConverter getRequiredConverter(String type) {
        DocConverter converter = converters.get(type);
        if (converter == null) {
            throw new IllegalArgumentException(
                    "No converter registered for type '" + type + "'. Available: " + converters.keySet());
        }
        return converter;
    }

    public DocConverter getConverterOrNull(String type) {
        return converters.get(type);
    }

    public Map<String, DocConverter> getAllConverters() {
        return Collections.unmodifiableMap(converters);
    }
}
