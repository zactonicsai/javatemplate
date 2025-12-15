package zac.demo.apps.dynamicclass.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloController {

    @GetMapping("/hello-json")
    public Greeting sayHelloJson() {
        DocConverterRegistry d1 = new DocConverterRegistry();
        int size = d1.getAllConverters().size();
        return new Greeting(1, "Hello JSON World!: " + size);
    }

}