package org.demo.zach.htmxapp.model;

import org.demo.zach.htmxapp.model.dto.PersonDTO;
import org.demo.zach.htmxapp.model.entity.Person;
import org.springframework.stereotype.Component;

@Component
public class PersonMapper {
    
    public PersonDTO toDTO(Person person) {
        if (person == null) {
            return null;
        }
        
        return PersonDTO.builder()
                .id(person.getId())
                .firstName(person.getFirstName())
                .lastName(person.getLastName())
                .streetAddress(person.getStreetAddress())
                .city(person.getCity())
                .state(person.getState())
                .zipCode(person.getZipCode())
                .country(person.getCountry())
                .createdAt(person.getCreatedAt())
                .updatedAt(person.getUpdatedAt())
                .build();
    }
    
    public Person toEntity(PersonDTO dto) {
        if (dto == null) {
            return null;
        }
        
        return Person.builder()
                .id(dto.getId())
                .firstName(dto.getFirstName())
                .lastName(dto.getLastName())
                .streetAddress(dto.getStreetAddress())
                .city(dto.getCity())
                .state(dto.getState())
                .zipCode(dto.getZipCode())
                .country(dto.getCountry())
                .createdAt(dto.getCreatedAt())
                .updatedAt(dto.getUpdatedAt())
                .build();
    }
}
