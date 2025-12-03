package org.demo.zach.htmxapp.controller;


import lombok.RequiredArgsConstructor;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

import org.demo.zach.htmxapp.model.dto.PersonDTO;
import org.demo.zach.htmxapp.service.PersonService;

@RestController
@RequestMapping("/api/persons")
@RequiredArgsConstructor
public class PersonController {
    
    private final PersonService personService;
    
    /**
     * Get all persons
     * GET /api/persons
     */
    @GetMapping
    public ResponseEntity<List<PersonDTO>> getAllPersons() {
        List<PersonDTO> persons = personService.getAllPersons();
        return ResponseEntity.ok(persons);
    }
    
    /**
     * Get person by id
     * GET /api/persons/{id}
     */
    @GetMapping("/{id}")
    public ResponseEntity<PersonDTO> getPersonById(@PathVariable Long id) {
        PersonDTO person = personService.getPersonById(id);
        return ResponseEntity.ok(person);
    }
    
    /**
     * Create a new person
     * POST /api/persons
     */
    @PostMapping
    public ResponseEntity<PersonDTO> createPerson(@RequestBody PersonDTO personDTO) {
        PersonDTO createdPerson = personService.createPerson(personDTO);
        return ResponseEntity.status(HttpStatus.CREATED).body(createdPerson);
    }
    
    /**
     * Update an existing person
     * PUT /api/persons/{id}
     */
    @PutMapping("/{id}")
    public ResponseEntity<PersonDTO> updatePerson(
            @PathVariable Long id,
            @RequestBody PersonDTO personDTO) {
        PersonDTO updatedPerson = personService.updatePerson(id, personDTO);
        return ResponseEntity.ok(updatedPerson);
    }
    
    /**
     * Delete a person
     * DELETE /api/persons/{id}
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deletePerson(@PathVariable Long id) {
        personService.deletePerson(id);
        return ResponseEntity.noContent().build();
    }
    
    /**
     * Get all persons by city
     * GET /api/persons/search/city?name=NewYork
     */
    @GetMapping("/search/city")
    public ResponseEntity<List<PersonDTO>> getPersonsByCity(@RequestParam String name) {
        List<PersonDTO> persons = personService.findByCity(name);
        return ResponseEntity.ok(persons);
    }
    
    /**
     * Get all persons by state
     * GET /api/persons/search/state?name=NY
     */
    @GetMapping("/search/state")
    public ResponseEntity<List<PersonDTO>> getPersonsByState(@RequestParam String name) {
        List<PersonDTO> persons = personService.findByState(name);
        return ResponseEntity.ok(persons);
    }
}
