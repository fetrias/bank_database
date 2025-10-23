import psycopg2
from psycopg2 import sql, errors
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple

class DatabaseManager:
    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self.connection_params = {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password
        }
        self.connection: Optional[psycopg2.extensions.connection] = None
        self.logger = logging.getLogger('DatabaseManager')
        
    def connect(self) -> bool:
        try:
            self.connection = psycopg2.connect(**self.connection_params, options="-c client_encoding=UTF8")
            self.connection.autocommit = False
            try:
                cursor = self.connection.cursor()
                cursor.execute("SET search_path TO bank_system, public;")
                cursor.close()
            except Exception as e:
                self.logger.warning(f"Could not set search_path to bank_system: {e}")

            try:
                cursor = self.connection.cursor()
                cursor.execute("SELECT to_regclass('bank_system.currencies');")
                reg = cursor.fetchone()[0]
                cursor.close()

                if not reg:
                    import os
                    schema_path = os.path.join(os.path.dirname(__file__), 'database_schema.sql')
                    if os.path.exists(schema_path):
                        try:
                            try:
                                with open(schema_path, 'r', encoding='utf-8') as f:
                                    sql_script = f.read()
                            except UnicodeDecodeError:
                                try:
                                    with open(schema_path, 'r', encoding='utf-8-sig') as f:
                                        sql_script = f.read()
                                except UnicodeDecodeError:
                                    with open(schema_path, 'r', encoding='latin1') as f:
                                        sql_script = f.read()
                            self.logger.info(f"bank_system schema missing — applying {schema_path}")
                            self.execute_script(sql_script)
                            self.logger.info("Database schema applied successfully")
                            try:
                                cursor = self.connection.cursor()
                                cursor.execute("SET search_path TO bank_system, public;")
                                cursor.close()
                            except Exception:
                                pass
                        except Exception as e:
                            self.logger.error(f"Failed to apply database schema from {schema_path}: {e}")
                    else:
                        self.logger.warning(f"bank_system schema does not exist and schema file not found at {schema_path}")
            except Exception:
                self.logger.debug("Could not verify or create bank_system schema after connect")

            self.logger.info(f"Connected to database {self.connection_params['database']}")
            return True
        except psycopg2.OperationalError as e:
            self.logger.error(f"Connection failed: {e}")
            raise ConnectionError(f"Не удалось подключиться к базе данных: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected connection error: {e}")
            raise
    
    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.logger.info("Database connection closed")
            self.connection = None
    
    def execute_script(self, sql_script: str) -> bool:
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql_script)
            self.connection.commit()
            self.logger.info("SQL script executed successfully")
            return True
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Failed to execute SQL script: {e}")
            raise
            
    def drop_schema(self) -> bool:
        if not self.connection:
            raise ConnectionError("Database connection is not established. Call connect() first.")
            
        try:
            cursor = self.connection.cursor()
            cursor.execute("DROP SCHEMA IF EXISTS bank_system CASCADE;")
            self.connection.commit()
            self.logger.info("bank_system schema dropped successfully")
            return True
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Failed to drop bank_system schema: {e}")
            raise
        except errors.UniqueViolation as e:
            self.connection.rollback()
            self.logger.error(f"UNIQUE constraint violation: {e}")
            raise ValueError(f"Нарушение уникальности: {e.diag.message_detail or e.pgerror}")
        except errors.NotNullViolation as e:
            self.connection.rollback()
            self.logger.error(f"NOT NULL constraint violation: {e}")
            raise ValueError(f"Обязательное поле не заполнено: {e.diag.column_name}")
        except errors.CheckViolation as e:
            self.connection.rollback()
            self.logger.error(f"CHECK constraint violation: {e}")
            raise ValueError(f"Нарушение ограничения CHECK: {e.diag.message_primary}")
        except errors.ForeignKeyViolation as e:
            self.connection.rollback()
            self.logger.error(f"FOREIGN KEY constraint violation: {e}")
            raise ValueError(f"Нарушение внешнего ключа: {e.diag.message_detail or e.pgerror}")
        except psycopg2.Error as e:
            self.connection.rollback()
            self.logger.error(f"Database error: {e}")
            raise ValueError(f"Ошибка базы данных: {e.pgerror}")
        finally:
            if cursor:
                cursor.close()
    
    def execute_query(self, query: str, params: tuple = None) -> List[Tuple]:
        cursor = None
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if cursor.description:
                results = cursor.fetchall()
                self.logger.info(f"Query returned {len(results)} rows")
                return results
            
            self.connection.commit()
            self.logger.info("Query executed successfully")
            return []
        except errors.UniqueViolation as e:
            self.connection.rollback()
            self.logger.error(f"UNIQUE constraint violation: {e}")
            raise ValueError(f"Запись с таким значением уже существует")
        except errors.NotNullViolation as e:
            self.connection.rollback()
            self.logger.error(f"NOT NULL constraint violation: {e}")
            raise ValueError(f"Поле '{e.diag.column_name}' обязательно для заполнения")
        except errors.CheckViolation as e:
            self.connection.rollback()
            self.logger.error(f"CHECK constraint violation: {e}")
            raise ValueError(f"Значение не соответствует ограничению: {e.diag.constraint_name}")
        except errors.ForeignKeyViolation as e:
            self.connection.rollback()
            self.logger.error(f"FOREIGN KEY constraint violation: {e}")
            if 'is still referenced' in str(e):
                raise ValueError(f"Невозможно удалить: на эту запись ссылаются другие данные")
            else:
                raise ValueError(f"Ссылка на несуществующую запись")
        except errors.InvalidTextRepresentation as e:
            self.connection.rollback()
            self.logger.error(f"Invalid data type: {e}")
            raise ValueError(f"Неверный тип данных: проверьте формат введенных значений")
        except psycopg2.Error as e:
            self.connection.rollback()
            self.logger.error(f"Database error: {e}")
            raise ValueError(f"Ошибка выполнения запроса: {e.pgerror}")
        finally:
            if cursor:
                cursor.close()
    
    def insert_currency(self, code: str, name: str, symbol: str, is_active: bool) -> int:
        if not self.connection:
            raise ConnectionError("Database connection is not established. Call connect() first.")
            
        query = """
            INSERT INTO bank_system.currencies (currency_code, currency_name, symbol, is_active)
            VALUES (%s, %s, %s, %s)
            RETURNING currency_id
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (code, name, symbol, is_active))
            currency_id = cursor.fetchone()[0]
            self.connection.commit()
            self.logger.info(f"Currency inserted with ID: {currency_id}")
            return currency_id
        except Exception as e:
            self.connection.rollback()
            raise
        finally:
            cursor.close()
    
    def insert_exchange_rate(self, base_currency: str, target_currency: str,
                            buy_rate: float, sell_rate: float, updated_by: str) -> int:
        query = """
            INSERT INTO bank_system.exchange_rates 
            (base_currency, target_currency, buy_rate, sell_rate, updated_by)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING rate_id
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (base_currency, target_currency, buy_rate, sell_rate, updated_by))
            rate_id = cursor.fetchone()[0]
            self.connection.commit()
            self.logger.info(f"Exchange rate inserted with ID: {rate_id}")
            return rate_id
        except Exception as e:
            self.connection.rollback()
            raise
        finally:
            cursor.close()
    
    def insert_client(self, full_name: str, passport: str, phone: str, email: str,
                     birth_date: str, is_vip: bool, allowed_ops: List[str]) -> int:
        query = """
            INSERT INTO bank_system.clients 
            (full_name, passport_number, phone, email, birth_date, is_vip, allowed_operations)
            VALUES (%s, %s, %s, %s, %s, %s, %s::bank_system.transaction_type[])
            RETURNING client_id
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (full_name, passport, phone, email, birth_date, is_vip, allowed_ops))
            client_id = cursor.fetchone()[0]
            self.connection.commit()
            self.logger.info(f"Client inserted with ID: {client_id}")
            return client_id
        except Exception as e:
            self.connection.rollback()
            raise
        finally:
            cursor.close()
    
    def insert_account(self, client_id: int, currency_code: str, account_number: str,
                      balance: float, status: str) -> int:
        query = """
            INSERT INTO bank_system.currency_accounts 
            (client_id, currency_code, account_number, balance, account_status)
            VALUES (%s, %s, %s, %s, %s::bank_system.account_status)
            RETURNING account_id
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (client_id, currency_code, account_number, balance, status))
            account_id = cursor.fetchone()[0]
            self.connection.commit()
            self.logger.info(f"Account inserted with ID: {account_id}")
            return account_id
        except Exception as e:
            self.connection.rollback()
            raise
        finally:
            cursor.close()
    
    def insert_transaction(self, account_id: int, trans_type: str, amount: float,
                          currency_code: str, exchange_rate: Optional[float],
                          commission: float, description: str, employee: str) -> int:
        query = """
            INSERT INTO bank_system.transactions 
            (account_id, transaction_type, amount, currency_code, exchange_rate, 
             commission, description, employee_name)
            VALUES (%s, %s::bank_system.transaction_type, %s, %s, %s, %s, %s, %s)
            RETURNING transaction_id
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (account_id, trans_type, amount, currency_code, 
                                  exchange_rate, commission, description, employee))
            trans_id = cursor.fetchone()[0]
            self.connection.commit()
            self.logger.info(f"Transaction inserted with ID: {trans_id}")
            return trans_id
        except Exception as e:
            self.connection.rollback()
            raise
        finally:
            cursor.close()
    
    def get_currencies(self) -> List[Tuple]:
        query = "SELECT * FROM bank_system.currencies ORDER BY currency_code"
        return self.execute_query(query)
    
    def get_exchange_rates(self, base_currency: str = None) -> List[Tuple]:
        if base_currency and base_currency != "ALL":
            query = """
                SELECT r.rate_id, r.base_currency, r.target_currency, 
                       r.buy_rate, r.sell_rate, r.rate_date, r.updated_by
                FROM bank_system.exchange_rates r
                WHERE r.base_currency = %s
                ORDER BY r.rate_date DESC
            """
            return self.execute_query(query, (base_currency,))
        else:
            query = """
                SELECT r.rate_id, r.base_currency, r.target_currency, 
                       r.buy_rate, r.sell_rate, r.rate_date, r.updated_by
                FROM bank_system.exchange_rates r
                ORDER BY r.rate_date DESC
            """
            return self.execute_query(query)
    
    def get_clients(self) -> List[Tuple]:
        query = """
            SELECT client_id, full_name, passport_number, phone, email, 
                   registration_date, birth_date, is_vip, allowed_operations
            FROM bank_system.clients
            ORDER BY full_name
        """
        return self.execute_query(query)
    
    def get_accounts(self, client_id: int = None, currency: str = None) -> List[Tuple]:
        query = """
            SELECT a.account_id, c.full_name, a.currency_code, a.account_number,
                   a.balance, a.account_status, a.opened_date, a.last_transaction_date
            FROM bank_system.currency_accounts a
            JOIN bank_system.clients c ON a.client_id = c.client_id
            WHERE 1=1
        """
        params = []
        
        if client_id:
            query += " AND a.client_id = %s"
            params.append(client_id)
        
        if currency and currency != "ALL":
            query += " AND a.currency_code = %s"
            params.append(currency)
        
        query += " ORDER BY c.full_name, a.currency_code"
        
        return self.execute_query(query, tuple(params) if params else None)
    
    def get_transactions(self, account_id: int = None, trans_type: str = None,
                        from_date: str = None, to_date: str = None) -> List[Tuple]:
        query = """
            SELECT t.transaction_id, c.full_name, a.account_number, 
                   t.transaction_type, t.amount, t.currency_code, t.exchange_rate,
                   t.commission, t.transaction_date, t.description, t.employee_name
            FROM bank_system.transactions t
            JOIN bank_system.currency_accounts a ON t.account_id = a.account_id
            JOIN bank_system.clients c ON a.client_id = c.client_id
            WHERE 1=1
        """
        params = []
        
        if account_id:
            query += " AND t.account_id = %s"
            params.append(account_id)
        
        if trans_type and trans_type != "ALL":
            query += " AND t.transaction_type = %s::bank_system.transaction_type"
            params.append(trans_type)
        
        if from_date:
            query += " AND t.transaction_date >= %s"
            params.append(from_date)
        
        if to_date:
            query += " AND t.transaction_date <= %s"
            params.append(to_date)
        
        query += " ORDER BY t.transaction_date DESC LIMIT 1000"
        
        return self.execute_query(query, tuple(params) if params else None)
    
    def get_client_balance_summary(self, client_id: int) -> List[Tuple]:
        query = """
            SELECT a.currency_code, SUM(a.balance) as total_balance,
                   COUNT(a.account_id) as account_count
            FROM bank_system.currency_accounts a
            WHERE a.client_id = %s AND a.account_status = 'ACTIVE'
            GROUP BY a.currency_code
            ORDER BY a.currency_code
        """
        return self.execute_query(query, (client_id,))
        
    def drop_schema(self) -> bool:
        if not self.connection:
            raise ConnectionError("Database connection is not established. Call connect() first.")
            
        try:
            cursor = self.connection.cursor()
            cursor.execute("DROP SCHEMA IF EXISTS bank_system CASCADE;")
            self.connection.commit()
            self.logger.info("bank_system schema dropped successfully")
            return True
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Failed to drop bank_system schema: {e}")
            raise
