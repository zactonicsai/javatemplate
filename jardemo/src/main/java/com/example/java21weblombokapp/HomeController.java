package com.example.java21weblombokapp;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ResponseBody;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

@Controller
public class HomeController {

    @GetMapping("/")
    public String home(Model model) {
        model.addAttribute("projectName", "Java21WebLombokApp");
        model.addAttribute("message", "Auto-generated template");
        model.addAttribute("timestamp", LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")));
        return "home";
    }

    @GetMapping("/api/info")
    @ResponseBody
    public ProjectInfo info() {
        return new ProjectInfo(
            "Java21WebLombokApp",
            "Auto-generated template",
            LocalDateTime.now().toString()
        );
    }

    // Simple response class for API
    record ProjectInfo(String name, String description, String timestamp) {}
}
