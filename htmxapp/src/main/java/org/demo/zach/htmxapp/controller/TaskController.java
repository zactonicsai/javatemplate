package org.demo.zach.htmxapp.controller;

import org.demo.zach.model.Task;
import org.demo.zach.htmxapp.repository.*;
import jakarta.validation.Valid;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.*;

@Controller
@RequestMapping("/")
public class TaskController {
    
    private final TaskRepository taskRepository;
    
    public TaskController(TaskRepository taskRepository) {
        this.taskRepository = taskRepository;
    }
    
    @GetMapping
    public String index(Model model) {
        model.addAttribute("tasks", taskRepository.findAll());
        model.addAttribute("task", new Task());
        return "index";
    }
    
    @PostMapping("/tasks")
    public String createTask(@Valid @ModelAttribute Task task, BindingResult result, Model model) {
        if (result.hasErrors()) {
            model.addAttribute("tasks", taskRepository.findAll());
            return "index";
        }
        taskRepository.save(task);
        model.addAttribute("tasks", taskRepository.findAll());
        model.addAttribute("task", new Task());
        return "fragments/task-list :: task-list";
    }
    
    @GetMapping("/tasks/{id}/edit")
    public String editTask(@PathVariable Long id, Model model) {
        Task task = taskRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Task not found"));
        model.addAttribute("task", task);
        return "fragments/task-form :: edit-form";
    }
    
    @PutMapping("/tasks/{id}")
    public String updateTask(@PathVariable Long id, @Valid @ModelAttribute Task task, 
                           BindingResult result, Model model) {
        if (result.hasErrors()) {
            return "fragments/task-form :: edit-form";
        }
        task.setId(id);
        taskRepository.save(task);
        model.addAttribute("tasks", taskRepository.findAll());
        model.addAttribute("task", new Task());
        return "fragments/task-list :: task-list";
    }
    
    @DeleteMapping("/tasks/{id}")
    public String deleteTask(@PathVariable Long id, Model model) {
        taskRepository.deleteById(id);
        model.addAttribute("tasks", taskRepository.findAll());
        return "fragments/task-list :: task-list";
    }
    
    @GetMapping("/tasks/{id}/cancel")
    public String cancelEdit(@PathVariable Long id, Model model) {
        model.addAttribute("tasks", taskRepository.findAll());
        return "fragments/task-list :: task-list";
    }
}