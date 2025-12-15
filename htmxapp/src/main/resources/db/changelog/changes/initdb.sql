DROP TABLE IF EXISTS person;

CREATE TABLE person (
    id BIGSERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    street_address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    country VARCHAR(100),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

DROP INDEX IF EXISTS idx_person_name;

CREATE INDEX idx_person_name ON person(last_name, first_name);

INSERT INTO person (
    first_name,
    last_name,
    street_address,
    city,
    state,
    zip_code,
    country
)
VALUES (
    'Alice',
    'Johnson',
    '456 Oak Lane',
    'Springfield',
    'IL',
    '62704',
    'USA'
);

