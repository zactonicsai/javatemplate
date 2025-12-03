package org.demo.zach.htmxapp.repository;

import org.demo.zach.htmxapp.model.entity.Person;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface PersonRepository extends JpaRepository<Person, Long> {
    
    /**
     * Find a person by first and last name
     */
    Optional<Person> findByFirstNameAndLastName(String firstName, String lastName);
    
    /**
     * Find all persons by city
     */
    List<Person> findByCity(String city);
    
    /**
     * Find all persons by state
     */
    List<Person> findByState(String state);
    
    /**
     * Find all persons by country
     */
    List<Person> findByCountry(String country);
    
    /**
     * Custom query to find persons by city and state
     */
    @Query("SELECT p FROM Person p WHERE p.city = :city AND p.state = :state")
    List<Person> findByCityAndState(@Param("city") String city, @Param("state") String state);
    
    /**
     * Find all persons by first name (case-insensitive)
     */
    List<Person> findByFirstNameIgnoreCase(String firstName);
    
    /**
     * Find all persons by last name (case-insensitive)
     */
    List<Person> findByLastNameIgnoreCase(String lastName);
}