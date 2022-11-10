/* Create Database */
CREATE DATABASE bankapp;

/* Connect to database */
\c bankapp

/* customers table */
CREATE TABLE customers(
    customer_id BIGSERIAL PRIMARY KEY,
    customer_name VARCHAR(150) NOT NULL,
    customer_email VARCHAR(100) UNIQUE NOT NULL,
    customer_address VARCHAR(200),
    customer_phone VARCHAR(20),
    customer_bvn CHAR(12) NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    clearance VARCHAR(30) DEFAULT 'customer',
    created_at TIMESTAMP DEFAULT NOW()
);

/* sample customers */
INSERT INTO customers(customer_name, customer_email, customer_address, customer_bvn, password, clearance)
VALUES ('Mahadi Abuhuraira', 'mamt4real@bank.com', 'Number 1 at address city', '123456689011', '12345pass', 'admin');
INSERT INTO customers(customer_name, customer_email, customer_address, customer_bvn, password)
VALUES ('Random User One', 'user1@bank.com', 'Number 1 at address city', '123456689011', '12345pass');
INSERT INTO customers(customer_name, customer_email, customer_address, customer_bvn, password)
VALUES ('Random User Two', 'user2@bank.com', 'Number 2 at address city', '123456689012',  '12345pass');
INSERT INTO customers(customer_name, customer_email, customer_address, customer_bvn, password)
VALUES ('Random User Three', 'user3@bank.com', 'Number 3 at address city', '123456689013',  '12345pass');
INSERT INTO customers(customer_name, customer_email, customer_address, customer_bvn, password)
VALUES ('Random User Four', 'user4@bank.com', 'Number 4 at address city', '123456689014', '12345pass');

/* accounts table and account no sequence */
CREATE SEQUENCE account_no_seq
    INCREMENT 1
    MINVALUE 5000000000
    MAXVALUE 5999999999
    START 5000000000;

CREATE TABLE accounts (
    account_no CHAR(10) PRIMARY KEY DEFAULT nextval('account_no_seq'::regclass),
    account_name VARCHAR(150) NOT NULL,
    account_type VARCHAR(50) NOT NULL DEFAULT 'Savings',
    account_balance NUMERIC DEFAULT 0 CHECK(account_balance >= 0),
    created_at TIMESTAMP DEFAULT NOW(),
    customer_id BIGSERIAL NOT NULL REFERENCES customers(customer_id)
);

/* sample accounts */
INSERT INTO accounts(account_name, account_balance, customer_id) VALUES ('Mahadi Abuhuraira', 3500.23, 1);
INSERT INTO accounts(account_name, account_balance, customer_id, account_type) VALUES ('Mahadi Abuhuraira', 155500.23, 1, 'Current');
INSERT INTO accounts(account_name, account_balance, customer_id) VALUES ('Random User Two', 40500.00, 2);
INSERT INTO accounts(account_name, account_balance, customer_id) VALUES ('Random User Three', 1500.23, 3);
INSERT INTO accounts(account_name, account_balance, customer_id) VALUES ('Random User Four', 877.23, 4);

CREATE SEQUENCE card_no_seq
    INCREMENT 1
    MINVALUE 5555000000000000
    MAXVALUE 5555999999999999
    START 5555000000000000;


CREATE TABLE credit_cards(
    id BIGSERIAL PRIMARY KEY,
    card_no CHAR(16) UNIQUE NOT NULL DEFAULT nextval('card_no_seq'::regclass),
    card_cvv CHAR(3) NOT NULL,
    card_pin CHAR(4) NOT NULL,
    issued_date DATE DEFAULT NOW(),
    exipiry_date DATE DEFAULT NOW() + INTERVAL '4 years',
    account_no CHAR(10) NOT NULL REFERENCES accounts(account_no)
);

/* sample credit cards */
INSERT INTO credit_cards(card_cvv, card_pin, account_no) VALUES (567, 1234, 5000000001);
INSERT INTO credit_cards(card_cvv, card_pin, account_no) VALUES (568, 4321, 5000000003);
INSERT INTO credit_cards(card_cvv, card_pin, account_no) VALUES (467, 1990, 5000000002);


CREATE TABLE transactions (
    transaction_id BIGSERIAL PRIMARY KEY,
    transaction_type CHAR(2) NOT NULL CHECK(transaction_type IN ('CR', 'DR', 'Dr', 'Cr', 'cr', 'dr')),
    transaction_amount NUMERIC,
    transaction_status VARCHAR(20),
    transaction_date TIMESTAMP DEFAULT NOW(),
    transaction_desc VARCHAR(200),
    account_no CHAR(10) NOT NULL REFERENCES accounts(account_no),
    account_involved CHAR(10) REFERENCES accounts(account_no)
);