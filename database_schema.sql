CREATE SCHEMA IF NOT EXISTS bank_system;

SET search_path TO bank_system;

CREATE TYPE transaction_type AS ENUM ('BUY', 'SELL', 'TRANSFER', 'DEPOSIT', 'WITHDRAWAL');

CREATE TYPE account_status AS ENUM ('ACTIVE', 'BLOCKED', 'CLOSED');

CREATE TABLE currencies (
    currency_id SERIAL PRIMARY KEY,
    currency_code VARCHAR(3) NOT NULL UNIQUE,
    currency_name VARCHAR(50) NOT NULL,
    symbol VARCHAR(5),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE exchange_rates (
    rate_id SERIAL PRIMARY KEY,
    base_currency VARCHAR(3) NOT NULL,
    target_currency VARCHAR(3) NOT NULL,
    buy_rate NUMERIC(12, 6) NOT NULL CHECK (buy_rate > 0),
    sell_rate NUMERIC(12, 6) NOT NULL CHECK (sell_rate > 0),
    rate_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100) NOT NULL,
    FOREIGN KEY (base_currency) REFERENCES currencies(currency_code) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (target_currency) REFERENCES currencies(currency_code) ON DELETE RESTRICT ON UPDATE CASCADE,
    CHECK (base_currency != target_currency)
);

CREATE TABLE clients (
    client_id SERIAL PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    passport_number VARCHAR(20) NOT NULL UNIQUE,
    phone VARCHAR(20),
    email VARCHAR(100),
    registration_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    birth_date DATE NOT NULL,
    is_vip BOOLEAN NOT NULL DEFAULT FALSE,
    allowed_operations transaction_type[] NOT NULL,
    CHECK (birth_date < CURRENT_DATE)
);

CREATE TABLE currency_accounts (
    account_id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL,
    currency_code VARCHAR(3) NOT NULL,
    account_number VARCHAR(20) NOT NULL UNIQUE,
    balance NUMERIC(15, 2) NOT NULL DEFAULT 0 CHECK (balance >= 0),
    account_status account_status NOT NULL DEFAULT 'ACTIVE',
    opened_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_transaction_date TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(client_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (currency_code) REFERENCES currencies(currency_code) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE transactions (
    transaction_id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL,
    transaction_type transaction_type NOT NULL,
    amount NUMERIC(15, 2) NOT NULL CHECK (amount > 0),
    currency_code VARCHAR(3) NOT NULL,
    exchange_rate NUMERIC(12, 6),
    commission NUMERIC(8, 2) CHECK (commission >= 0),
    transaction_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    employee_name VARCHAR(100) NOT NULL,
    is_completed BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (account_id) REFERENCES currency_accounts(account_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (currency_code) REFERENCES currencies(currency_code) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX idx_exchange_rates_currencies ON exchange_rates(base_currency, target_currency);
CREATE INDEX idx_exchange_rates_date ON exchange_rates(rate_date);
CREATE INDEX idx_accounts_client ON currency_accounts(client_id);
CREATE INDEX idx_accounts_currency ON currency_accounts(currency_code);
CREATE INDEX idx_transactions_account ON transactions(account_id);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_type ON transactions(transaction_type);

INSERT INTO currencies (currency_code, currency_name, symbol, is_active) VALUES
('RUB', 'Российский рубль', '₽', TRUE),
('USD', 'Доллар США', '$', TRUE),
('EUR', 'Евро', '€', TRUE),
('GBP', 'Фунт стерлингов', '£', TRUE),
('CNY', 'Китайский юань', '¥', TRUE),
('JPY', 'Японская йена', '¥', TRUE),
('CHF', 'Швейцарский франк', 'Fr', TRUE),
('TRY', 'Турецкая лира', '₺', FALSE);

INSERT INTO exchange_rates (base_currency, target_currency, buy_rate, sell_rate, rate_date, updated_by) VALUES
('USD', 'RUB', 92.50, 93.80, '2024-10-09 09:00:00', 'Иванов И.И.'),
('EUR', 'RUB', 100.20, 101.50, '2024-10-09 09:00:00', 'Иванов И.И.'),
('GBP', 'RUB', 118.30, 120.10, '2024-10-09 09:00:00', 'Иванов И.И.'),
('CNY', 'RUB', 12.95, 13.15, '2024-10-09 09:00:00', 'Петрова А.С.'),
('USD', 'EUR', 0.92, 0.94, '2024-10-09 09:00:00', 'Иванов И.И.'),
('USD', 'GBP', 0.78, 0.80, '2024-10-09 09:00:00', 'Сидоров П.К.'),
('JPY', 'RUB', 0.62, 0.64, '2024-10-09 09:00:00', 'Петрова А.С.'),
('CHF', 'RUB', 105.40, 107.20, '2024-10-09 09:00:00', 'Сидоров П.К.');

INSERT INTO clients (full_name, passport_number, phone, email, birth_date, is_vip, allowed_operations) VALUES
('Смирнов Алексей Петрович', '4512 678901', '+7-916-234-5678', 'smirnov@mail.ru', '1985-03-15', TRUE, ARRAY['BUY','SELL','TRANSFER','DEPOSIT']::transaction_type[]),
('Кузнецова Мария Ивановна', '4513 123456', '+7-925-876-5432', 'kuznetsova@gmail.com', '1992-07-22', FALSE, ARRAY['BUY','SELL','DEPOSIT']::transaction_type[]),
('Попов Дмитрий Сергеевич', '4514 789012', '+7-903-456-7890', 'popov@yandex.ru', '1978-11-30', TRUE, ARRAY['BUY','SELL','TRANSFER','DEPOSIT','WITHDRAWAL']::transaction_type[]),
('Васильева Елена Николаевна', '4515 345678', '+7-917-234-8901', 'vasilyeva@mail.ru', '1988-05-18', FALSE, ARRAY['BUY','SELL']::transaction_type[]),
('Петров Игорь Владимирович', '4516 901234', '+7-926-789-0123', 'petrov.igor@gmail.com', '1995-09-25', FALSE, ARRAY['BUY','SELL','DEPOSIT']::transaction_type[]),
('Новикова Ольга Александровна', '4517 567890', '+7-905-345-6789', 'novikova@yandex.ru', '1983-12-08', TRUE, ARRAY['BUY','SELL','TRANSFER','DEPOSIT']::transaction_type[]);

INSERT INTO currency_accounts (client_id, currency_code, account_number, balance, account_status) VALUES
(1, 'RUB', '40817810100000000001', 250000.00, 'ACTIVE'),
(1, 'USD', '40817840100000000001', 5000.00, 'ACTIVE'),
(1, 'EUR', '40817978100000000001', 3000.00, 'ACTIVE'),
(2, 'RUB', '40817810200000000002', 180000.00, 'ACTIVE'),
(2, 'USD', '40817840200000000002', 2000.00, 'ACTIVE'),
(3, 'RUB', '40817810300000000003', 520000.00, 'ACTIVE'),
(3, 'USD', '40817840300000000003', 10000.00, 'ACTIVE'),
(3, 'EUR', '40817978300000000003', 8000.00, 'ACTIVE'),
(3, 'GBP', '40817826300000000003', 2500.00, 'ACTIVE'),
(4, 'RUB', '40817810400000000004', 95000.00, 'ACTIVE'),
(4, 'EUR', '40817978400000000004', 1500.00, 'ACTIVE'),
(5, 'RUB', '40817810500000000005', 75000.00, 'ACTIVE'),
(5, 'USD', '40817840500000000005', 800.00, 'ACTIVE'),
(6, 'RUB', '40817810600000000006', 420000.00, 'ACTIVE'),
(6, 'USD', '40817840600000000006', 7500.00, 'ACTIVE'),
(6, 'EUR', '40817978600000000006', 5000.00, 'BLOCKED');

INSERT INTO transactions (account_id, transaction_type, amount, currency_code, exchange_rate, commission, transaction_date, description, employee_name, is_completed) VALUES
(1, 'DEPOSIT', 250000.00, 'RUB', NULL, 0.00, '2024-09-01 10:30:00', 'Первоначальное пополнение счета', 'Иванов И.И.', TRUE),
(2, 'BUY', 5000.00, 'USD', 92.50, 150.00, '2024-09-15 14:20:00', 'Покупка долларов', 'Петрова А.С.', TRUE),
(3, 'BUY', 3000.00, 'EUR', 100.20, 200.00, '2024-09-20 11:45:00', 'Покупка евро', 'Иванов И.И.', TRUE),
(4, 'DEPOSIT', 180000.00, 'RUB', NULL, 0.00, '2024-09-05 09:15:00', 'Пополнение счета', 'Сидоров П.К.', TRUE),
(5, 'BUY', 2000.00, 'USD', 92.80, 100.00, '2024-09-25 16:30:00', 'Покупка долларов', 'Петрова А.С.', TRUE),
(6, 'DEPOSIT', 520000.00, 'RUB', NULL, 0.00, '2024-08-15 10:00:00', 'Открытие счета', 'Иванов И.И.', TRUE),
(7, 'BUY', 10000.00, 'USD', 91.50, 300.00, '2024-09-10 12:15:00', 'Покупка долларов для инвестиций', 'Иванов И.И.', TRUE),
(8, 'BUY', 8000.00, 'EUR', 99.80, 250.00, '2024-09-18 15:40:00', 'Покупка евро', 'Петрова А.С.', TRUE),
(9, 'BUY', 2500.00, 'GBP', 118.30, 200.00, '2024-09-28 11:20:00', 'Покупка фунтов', 'Сидоров П.К.', TRUE),
(7, 'SELL', 1000.00, 'USD', 93.80, 50.00, '2024-10-02 14:10:00', 'Продажа части долларов', 'Иванов И.И.', TRUE),
(10, 'DEPOSIT', 95000.00, 'RUB', NULL, 0.00, '2024-09-12 10:30:00', 'Открытие счета', 'Петрова А.С.', TRUE),
(11, 'BUY', 1500.00, 'EUR', 100.50, 80.00, '2024-09-22 13:25:00', 'Покупка евро', 'Иванов И.И.', TRUE),
(12, 'DEPOSIT', 75000.00, 'RUB', NULL, 0.00, '2024-09-08 09:45:00', 'Пополнение счета', 'Сидоров П.К.', TRUE),
(13, 'BUY', 800.00, 'USD', 92.30, 40.00, '2024-09-30 15:50:00', 'Покупка долларов', 'Петрова А.С.', TRUE),
(14, 'DEPOSIT', 420000.00, 'RUB', NULL, 0.00, '2024-08-20 11:00:00', 'Открытие счета', 'Иванов И.И.', TRUE),
(15, 'BUY', 7500.00, 'USD', 91.80, 250.00, '2024-09-05 16:20:00', 'Покупка долларов', 'Иванов И.И.', TRUE),
(16, 'BUY', 5000.00, 'EUR', 100.00, 220.00, '2024-09-14 12:30:00', 'Покупка евро для поездки', 'Петрова А.С.', TRUE),
(8, 'TRANSFER', 500.00, 'EUR', NULL, 30.00, '2024-10-05 10:15:00', 'Перевод на другой счет', 'Сидоров П.К.', TRUE),
(2, 'SELL', 200.00, 'USD', 93.50, 20.00, '2024-10-07 14:35:00', 'Продажа долларов', 'Иванов И.И.', TRUE),
(11, 'SELL', 300.00, 'EUR', 101.20, 25.00, '2024-10-08 11:45:00', 'Продажа евро', 'Петрова А.С.', TRUE);
