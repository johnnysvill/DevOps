CREATE ROLE repl_user with LOGIN REPLICATION ENCRYPTED PASSWORD '1';
SELECT pg_create_physical_replication_slot('replication_slot');
CREATE TABLE hba ( lines text );
COPY hba FROM '/var/lib/postgresql/data/pg_hba.conf';
INSERT INTO hba (lines) VALUES ('host replication all 0.0.0.0/0 md5');
COPY hba TO '/var/lib/postgresql/data/pg_hba.conf';
SELECT pg_reload_conf();


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
