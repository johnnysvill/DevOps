CREATE DATABASE bot_db;

CREATE TABLE IF NOT EXISTS email (
        email_id SERIAL PRIMARY KEY,
        email_address VARCHAR(255) NOT NULL
);
CREATE TABLE IF NOT EXISTS phone_number (
        number_id SERIAL PRIMARY KEY,
        phone_number VARCHAR(255) NOT NULL
);

INSERT INTO email(email_address) VALUES('test@test.ru');
INSERT INTO email(email_address) VALUES('erty@gmail.com');
INSERT INTO phone_number(phone_number) VALUES('8926789032');
INSERT INTO phone_number(phone_number) VALUES('+78956736523');
