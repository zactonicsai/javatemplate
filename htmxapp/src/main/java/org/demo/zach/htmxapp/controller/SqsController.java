package org.demo.zach.htmxapp.controller;

import lombok.RequiredArgsConstructor;

import org.demo.zach.htmxapp.service.SqsSenderService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/sqs")
@RequiredArgsConstructor
public class SqsController {

    private final SqsSenderService sender;

    @PostMapping("/send")
    public String send(@RequestParam String message) {
        return "Message sent. ID = " + sender.sendMessage(message);
    }
}

