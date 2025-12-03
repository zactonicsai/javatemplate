package org.demo.zach.htmxapp.service;

import lombok.RequiredArgsConstructor;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

import org.demo.zach.htmxapp.model.dto.PersonDTO;
import org.demo.zach.htmxapp.model.entity.Person;
import org.demo.zach.htmxapp.model.mapper.PersonMapper;
import org.demo.zach.htmxapp.repository.PersonRepository;

@Service
@RequiredArgsConstructor
@Transactional
public class PersonService {
    
    private final PersonRepository personRepository;
    private final PersonMapper personMapper;
    
    /**
     * Get all persons
     */
    @Transactional(readOnly = true)
    public List<PersonDTO> getAllPersons() {
        return personRepository.findAll()
                .stream()
                .map(personMapper::toDTO)
                .collect(Collectors.toList());
    }
    
    /**
     * Get person by id
     */
    @Transactional(readOnly = true)
    public PersonDTO getPersonById(Long id) {
        return personRepository.findById(id)
                .map(personMapper::toDTO)
                .orElseThrow(() -> new RuntimeException("Person not found with id: " + id));
    }
    
    /**
     * Create a new person
     */
    public PersonDTO createPerson(PersonDTO personDTO) {
        Person person = personMapper.toEntity(personDTO);
        Person savedPerson = personRepository.save(person);
        return personMapper.toDTO(savedPerson);
    }
    
    /**
     * Update an existing person
     */
    public PersonDTO updatePerson(Long id, PersonDTO personDTO) {
        Person person = personRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Person not found with id: " + id));
        
        person.setFirstName(personDTO.getFirstName());
        person.setLastName(personDTO.getLastName());
        person.setStreetAddress(personDTO.getStreetAddress());
        person.setCity(personDTO.getCity());
        person.setState(personDTO.getState());
        person.setZipCode(personDTO.getZipCode());
        person.setCountry(personDTO.getCountry());
        
        Person updatedPerson = personRepository.save(person);
        return personMapper.toDTO(updatedPerson);
    }
    
    /**
     * Delete a person
     */
    public void deletePerson(Long id) {
        if (!personRepository.existsById(id)) {
            throw new RuntimeException("Person not found with id: " + id);
        }
        personRepository.deleteById(id);
    }
    
    /**
     * Find persons by city
     */
    @Transactional(readOnly = true)
    public List<PersonDTO> findByCity(String city) {
        return personRepository.findByCity(city)
                .stream()
                .map(personMapper::toDTO)
                .collect(Collectors.toList());
    }
    
    /**
     * Find persons by state
     */
    @Transactional(readOnly = true)
    public List<PersonDTO> findByState(String state) {
        return personRepository.findByState(state)
                .stream()
                .map(personMapper::toDTO)
                .collect(Collectors.toList());
    }
}