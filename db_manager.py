import psycopg2
from psycopg2 import sql, errors
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple

class DatabaseManager:

    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self.connection_params = {'host': host, 'port': port, 'database': database, 'user': user, 'password': password}
        self.connection: Optional[psycopg2.extensions.connection] = None
        self.logger = logging.getLogger('DatabaseManager')

    def connect(self) -> bool:
        try:
            self.connection = psycopg2.connect(**self.connection_params, options='-c client_encoding=UTF8')
            self.connection.autocommit = False
            try:
                cursor = self.connection.cursor()
                cursor.execute('SET search_path TO bank_system, public;')
                cursor.close()
            except Exception as e:
                self.logger.warning(f'Could not set search_path to bank_system: {e}')
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
                            self.logger.info(f'bank_system schema missing — applying {schema_path}')
                            self.execute_script(sql_script)
                            self.logger.info('Database schema applied successfully')
                            try:
                                cursor = self.connection.cursor()
                                cursor.execute('SET search_path TO bank_system, public;')
                                cursor.close()
                            except Exception:
                                pass
                        except Exception as e:
                            self.logger.error(f'Failed to apply database schema from {schema_path}: {e}')
                    else:
                        self.logger.warning(f'bank_system schema does not exist and schema file not found at {schema_path}')
            except Exception:
                self.logger.debug('Could not verify or create bank_system schema after connect')
            self.logger.info(f"Connected to database {self.connection_params['database']}")
            return True
        except psycopg2.OperationalError as e:
            self.logger.error(f'Connection failed: {e}')
            raise ConnectionError(f'Не удалось подключиться к базе данных: {e}')
        except Exception as e:
            self.logger.error(f'Unexpected connection error: {e}')
            raise

    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.logger.info('Database connection closed')
            self.connection = None

    def execute_script(self, sql_script: str) -> bool:
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql_script)
            self.connection.commit()
            self.logger.info('SQL script executed successfully')
            return True
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f'Failed to execute SQL script: {e}')
            raise

    def drop_schema(self) -> bool:
        if not self.connection:
            raise ConnectionError('Database connection is not established. Call connect() first.')
        try:
            cursor = self.connection.cursor()
            cursor.execute('DROP SCHEMA IF EXISTS bank_system CASCADE;')
            self.connection.commit()
            self.logger.info('bank_system schema dropped successfully')
            return True
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f'Failed to drop bank_system schema: {e}')
            raise
        except errors.UniqueViolation as e:
            self.connection.rollback()
            self.logger.error(f'UNIQUE constraint violation: {e}')
            raise ValueError(f'Нарушение уникальности: {e.diag.message_detail or e.pgerror}')
        except errors.NotNullViolation as e:
            self.connection.rollback()
            self.logger.error(f'NOT NULL constraint violation: {e}')
            raise ValueError(f'Обязательное поле не заполнено: {e.diag.column_name}')
        except errors.CheckViolation as e:
            self.connection.rollback()
            self.logger.error(f'CHECK constraint violation: {e}')
            raise ValueError(f'Нарушение ограничения CHECK: {e.diag.message_primary}')
        except errors.ForeignKeyViolation as e:
            self.connection.rollback()
            self.logger.error(f'FOREIGN KEY constraint violation: {e}')
            raise ValueError(f'Нарушение внешнего ключа: {e.diag.message_detail or e.pgerror}')
        except psycopg2.Error as e:
            self.connection.rollback()
            self.logger.error(f'Database error: {e}')
            raise ValueError(f'Ошибка базы данных: {e.pgerror}')
        finally:
            if cursor:
                cursor.close()

    def execute_query(self, query: str, params: tuple=None) -> List[Tuple]:
        cursor = None
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            if cursor.description:
                results = cursor.fetchall()
                self.logger.info(f'Query returned {len(results)} rows')
                return results
            self.connection.commit()
            self.logger.info('Query executed successfully')
            return []
        except errors.UniqueViolation as e:
            self.connection.rollback()
            self.logger.error(f'UNIQUE constraint violation: {e}')
            raise ValueError(f'Запись с таким значением уже существует')
        except errors.NotNullViolation as e:
            self.connection.rollback()
            self.logger.error(f'NOT NULL constraint violation: {e}')
            raise ValueError(f"Поле '{e.diag.column_name}' обязательно для заполнения")
        except errors.CheckViolation as e:
            self.connection.rollback()
            self.logger.error(f'CHECK constraint violation: {e}')
            raise ValueError(f'Значение не соответствует ограничению: {e.diag.constraint_name}')
        except errors.ForeignKeyViolation as e:
            self.connection.rollback()
            self.logger.error(f'FOREIGN KEY constraint violation: {e}')
            if 'is still referenced' in str(e):
                raise ValueError(f'Невозможно удалить: на эту запись ссылаются другие данные')
            else:
                raise ValueError(f'Ссылка на несуществующую запись')
        except errors.InvalidTextRepresentation as e:
            self.connection.rollback()
            self.logger.error(f'Invalid data type: {e}')
            raise ValueError(f'Неверный тип данных: проверьте формат введенных значений')
        except psycopg2.Error as e:
            self.connection.rollback()
            self.logger.error(f'Database error: {e}')
            raise ValueError(f'Ошибка выполнения запроса: {e.pgerror}')
        finally:
            if cursor:
                cursor.close()

    def insert_currency(self, code: str, name: str, symbol: str, is_active: bool) -> int:
        if not self.connection:
            raise ConnectionError('Database connection is not established. Call connect() first.')
        query = '\n            INSERT INTO bank_system.currencies (currency_code, currency_name, symbol, is_active)\n            VALUES (%s, %s, %s, %s)\n            RETURNING currency_id\n        '
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (code, name, symbol, is_active))
            currency_id = cursor.fetchone()[0]
            self.connection.commit()
            self.logger.info(f'Currency inserted with ID: {currency_id}')
            return currency_id
        except Exception as e:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def insert_exchange_rate(self, base_currency: str, target_currency: str, buy_rate: float, sell_rate: float, updated_by: str) -> int:
        query = '\n            INSERT INTO bank_system.exchange_rates \n            (base_currency, target_currency, buy_rate, sell_rate, updated_by)\n            VALUES (%s, %s, %s, %s, %s)\n            RETURNING rate_id\n        '
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (base_currency, target_currency, buy_rate, sell_rate, updated_by))
            rate_id = cursor.fetchone()[0]
            self.connection.commit()
            self.logger.info(f'Exchange rate inserted with ID: {rate_id}')
            return rate_id
        except Exception as e:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def insert_client(self, full_name: str, passport: str, phone: str, email: str, birth_date: str, is_vip: bool, allowed_ops: List[str]) -> int:
        query = '\n            INSERT INTO bank_system.clients \n            (full_name, passport_number, phone, email, birth_date, is_vip, allowed_operations)\n            VALUES (%s, %s, %s, %s, %s, %s, %s::bank_system.transaction_type[])\n            RETURNING client_id\n        '
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (full_name, passport, phone, email, birth_date, is_vip, allowed_ops))
            client_id = cursor.fetchone()[0]
            self.connection.commit()
            self.logger.info(f'Client inserted with ID: {client_id}')
            return client_id
        except Exception as e:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def insert_account(self, client_id: int, currency_code: str, account_number: str, balance: float, status: str) -> int:
        query = '\n            INSERT INTO bank_system.currency_accounts \n            (client_id, currency_code, account_number, balance, account_status)\n            VALUES (%s, %s, %s, %s, %s::bank_system.account_status)\n            RETURNING account_id\n        '
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (client_id, currency_code, account_number, balance, status))
            account_id = cursor.fetchone()[0]
            self.connection.commit()
            self.logger.info(f'Account inserted with ID: {account_id}')
            return account_id
        except Exception as e:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def insert_transaction(self, account_id: int, trans_type: str, amount: float, currency_code: str, exchange_rate: Optional[float], commission: float, description: str, employee: str) -> int:
        query = '\n            INSERT INTO bank_system.transactions \n            (account_id, transaction_type, amount, currency_code, exchange_rate, \n             commission, description, employee_name)\n            VALUES (%s, %s::bank_system.transaction_type, %s, %s, %s, %s, %s, %s)\n            RETURNING transaction_id\n        '
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (account_id, trans_type, amount, currency_code, exchange_rate, commission, description, employee))
            trans_id = cursor.fetchone()[0]
            self.connection.commit()
            self.logger.info(f'Transaction inserted with ID: {trans_id}')
            return trans_id
        except Exception as e:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def get_currencies(self) -> List[Tuple]:
        query = 'SELECT * FROM bank_system.currencies ORDER BY currency_code'
        return self.execute_query(query)

    def get_exchange_rates(self, base_currency: str=None) -> List[Tuple]:
        if base_currency and base_currency != 'ALL':
            query = '\n                SELECT r.rate_id, r.base_currency, r.target_currency, \n                       r.buy_rate, r.sell_rate, r.rate_date, r.updated_by\n                FROM bank_system.exchange_rates r\n                WHERE r.base_currency = %s\n                ORDER BY r.rate_date DESC\n            '
            return self.execute_query(query, (base_currency,))
        else:
            query = '\n                SELECT r.rate_id, r.base_currency, r.target_currency, \n                       r.buy_rate, r.sell_rate, r.rate_date, r.updated_by\n                FROM bank_system.exchange_rates r\n                ORDER BY r.rate_date DESC\n            '
            return self.execute_query(query)

    def get_clients(self) -> List[Tuple]:
        query = '\n            SELECT client_id, full_name, passport_number, phone, email, \n                   registration_date, birth_date, is_vip, allowed_operations\n            FROM bank_system.clients\n            ORDER BY full_name\n        '
        return self.execute_query(query)

    def get_accounts(self, client_id: int=None, currency: str=None) -> List[Tuple]:
        query = '\n            SELECT a.account_id, c.full_name, a.currency_code, a.account_number,\n                   a.balance, a.account_status, a.opened_date, a.last_transaction_date\n            FROM bank_system.currency_accounts a\n            JOIN bank_system.clients c ON a.client_id = c.client_id\n            WHERE 1=1\n        '
        params = []
        if client_id:
            query += ' AND a.client_id = %s'
            params.append(client_id)
        if currency and currency != 'ALL':
            query += ' AND a.currency_code = %s'
            params.append(currency)
        query += ' ORDER BY c.full_name, a.currency_code'
        return self.execute_query(query, tuple(params) if params else None)

    def get_transactions(self, account_id: int=None, trans_type: str=None, from_date: str=None, to_date: str=None) -> List[Tuple]:
        query = '\n            SELECT t.transaction_id, c.full_name, a.account_number, \n                   t.transaction_type, t.amount, t.currency_code, t.exchange_rate,\n                   t.commission, t.transaction_date, t.description, t.employee_name\n            FROM bank_system.transactions t\n            JOIN bank_system.currency_accounts a ON t.account_id = a.account_id\n            JOIN bank_system.clients c ON a.client_id = c.client_id\n            WHERE 1=1\n        '
        params = []
        if account_id:
            query += ' AND t.account_id = %s'
            params.append(account_id)
        if trans_type and trans_type != 'ALL':
            query += ' AND t.transaction_type = %s::bank_system.transaction_type'
            params.append(trans_type)
        if from_date:
            query += ' AND t.transaction_date >= %s'
            params.append(from_date)
        if to_date:
            query += ' AND t.transaction_date <= %s'
            params.append(to_date)
        query += ' ORDER BY t.transaction_date DESC LIMIT 1000'
        return self.execute_query(query, tuple(params) if params else None)

    def get_client_balance_summary(self, client_id: int) -> List[Tuple]:
        query = "\n            SELECT a.currency_code, SUM(a.balance) as total_balance,\n                   COUNT(a.account_id) as account_count\n            FROM bank_system.currency_accounts a\n            WHERE a.client_id = %s AND a.account_status = 'ACTIVE'\n            GROUP BY a.currency_code\n            ORDER BY a.currency_code\n        "
        return self.execute_query(query, (client_id,))

    def drop_schema(self) -> bool:
        if not self.connection:
            raise ConnectionError('Database connection is not established. Call connect() first.')
        try:
            cursor = self.connection.cursor()
            cursor.execute('DROP SCHEMA IF EXISTS bank_system CASCADE;')
            self.connection.commit()
            self.logger.info('bank_system schema dropped successfully')
            return True
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f'Failed to drop bank_system schema: {e}')
            raise

    def get_tables_list(self) -> List[str]:
        query = "\n            SELECT table_name \n            FROM information_schema.tables \n            WHERE table_schema = 'bank_system' \n            ORDER BY table_name\n        "
        results = self.execute_query(query)
        return [row[0] for row in results]

    def get_table_columns(self, table_name: str) -> List[Dict[str, Any]]:
        query = "\n            SELECT column_name, data_type, character_maximum_length, \n                   is_nullable, column_default\n            FROM information_schema.columns\n            WHERE table_schema = 'bank_system' AND table_name = %s\n            ORDER BY ordinal_position\n        "
        results = self.execute_query(query, (table_name,))
        columns = []
        for row in results:
            columns.append({'name': row[0], 'type': row[1], 'max_length': row[2], 'nullable': row[3], 'default': row[4]})
        return columns

    def alter_table_add_column(self, table_name: str, column_name: str, data_type: str, constraints: str='') -> bool:
        query = f'ALTER TABLE bank_system.{table_name} ADD COLUMN {column_name} {data_type}'
        if constraints:
            query += f' {constraints}'
        self.execute_query(query)
        return True

    def alter_table_drop_column(self, table_name: str, column_name: str) -> bool:
        query = f'ALTER TABLE bank_system.{table_name} DROP COLUMN {column_name}'
        self.execute_query(query)
        return True

    def alter_table_rename_column(self, table_name: str, old_name: str, new_name: str) -> bool:
        query = f'ALTER TABLE bank_system.{table_name} RENAME COLUMN {old_name} TO {new_name}'
        self.execute_query(query)
        return True

    def alter_table_rename_table(self, old_name: str, new_name: str) -> bool:
        query = f'ALTER TABLE bank_system.{old_name} RENAME TO {new_name}'
        self.execute_query(query)
        return True

    def alter_table_change_type(self, table_name: str, column_name: str, new_type: str) -> bool:
        query = f'ALTER TABLE bank_system.{table_name} ALTER COLUMN {column_name} TYPE {new_type}'
        self.execute_query(query)
        return True

    def alter_table_set_not_null(self, table_name: str, column_name: str) -> bool:
        query = f'ALTER TABLE bank_system.{table_name} ALTER COLUMN {column_name} SET NOT NULL'
        self.execute_query(query)
        return True

    def alter_table_drop_not_null(self, table_name: str, column_name: str) -> bool:
        query = f'ALTER TABLE bank_system.{table_name} ALTER COLUMN {column_name} DROP NOT NULL'
        self.execute_query(query)
        return True

    def alter_table_add_constraint(self, table_name: str, constraint_name: str, constraint_def: str) -> bool:
        query = f'ALTER TABLE bank_system.{table_name} ADD CONSTRAINT {constraint_name} {constraint_def}'
        self.execute_query(query)
        return True

    def alter_table_drop_constraint(self, table_name: str, constraint_name: str) -> bool:
        query = f'ALTER TABLE bank_system.{table_name} DROP CONSTRAINT {constraint_name}'
        self.execute_query(query)
        return True

    def execute_advanced_select(self, table_name: str, columns: List[str]=None, where_clause: str='', order_by: str='', group_by: str='', having: str='') -> Tuple[List[Tuple], List[str]]:
        select_cols = ', '.join(columns) if columns else '*'
        query = f'SELECT {select_cols} FROM bank_system.{table_name}'
        if where_clause:
            query += f' WHERE {where_clause}'
        if group_by:
            query += f' GROUP BY {group_by}'
        if having:
            query += f' HAVING {having}'
        if order_by:
            query += f' ORDER BY {order_by}'
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            return (results, column_names)
        except psycopg2.Error as e:
            self.connection.rollback()
            self.logger.error(f'Advanced select error: {e}')
            raise ValueError(f'Ошибка запроса: {e}')
        finally:
            cursor.close()

    def execute_text_search(self, table_name: str, column_name: str, search_pattern: str, search_type: str='LIKE') -> Tuple[List[Tuple], List[str]]:
        if search_type == 'LIKE':
            query = f'SELECT * FROM bank_system.{table_name} WHERE {column_name} LIKE %s'
            params = (search_pattern,)
        elif search_type == 'ILIKE':
            query = f'SELECT * FROM bank_system.{table_name} WHERE {column_name} ILIKE %s'
            params = (search_pattern,)
        elif search_type == '~':
            query = f'SELECT * FROM bank_system.{table_name} WHERE {column_name} ~ %s'
            params = (search_pattern,)
        elif search_type == '~*':
            query = f'SELECT * FROM bank_system.{table_name} WHERE {column_name} ~* %s'
            params = (search_pattern,)
        elif search_type == '!~':
            query = f'SELECT * FROM bank_system.{table_name} WHERE {column_name} !~ %s'
            params = (search_pattern,)
        elif search_type == '!~*':
            query = f'SELECT * FROM bank_system.{table_name} WHERE {column_name} !~* %s'
            params = (search_pattern,)
        elif search_type == 'SIMILAR TO':
            query = f'SELECT * FROM bank_system.{table_name} WHERE {column_name} SIMILAR TO %s'
            params = (search_pattern,)
        elif search_type == 'NOT SIMILAR TO':
            query = f'SELECT * FROM bank_system.{table_name} WHERE {column_name} NOT SIMILAR TO %s'
            params = (search_pattern,)
        else:
            raise ValueError(f'Неподдерживаемый тип поиска: {search_type}')
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params)
            results = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            return (results, column_names)
        except psycopg2.Error as e:
            self.connection.rollback()
            self.logger.error(f'Search error: {e}')
            raise ValueError(f'Ошибка поиска: {e}')
        finally:
            cursor.close()

    def execute_string_function(self, table_name: str, column_name: str, function_type: str, params: Dict[str, Any]=None) -> Tuple[List[Tuple], List[str]]:
        if function_type == 'UPPER':
            select_expr = f'UPPER({column_name}) as upper_result'
        elif function_type == 'LOWER':
            select_expr = f'LOWER({column_name}) as lower_result'
        elif function_type == 'SUBSTRING':
            start = params.get('start', 1)
            length = params.get('length', '')
            if length:
                select_expr = f'SUBSTRING({column_name}, {start}, {length}) as substring_result'
            else:
                select_expr = f'SUBSTRING({column_name}, {start}) as substring_result'
        elif function_type == 'TRIM':
            select_expr = f'TRIM({column_name}) as trim_result'
        elif function_type == 'LTRIM':
            select_expr = f'LTRIM({column_name}) as ltrim_result'
        elif function_type == 'RTRIM':
            select_expr = f'RTRIM({column_name}) as rtrim_result'
        elif function_type == 'LPAD':
            length = params.get('length', 10)
            fill = params.get('fill', ' ')
            select_expr = f"LPAD({column_name}, {length}, '{fill}') as lpad_result"
        elif function_type == 'RPAD':
            length = params.get('length', 10)
            fill = params.get('fill', ' ')
            select_expr = f"RPAD({column_name}, {length}, '{fill}') as rpad_result"
        elif function_type == 'CONCAT':
            concat_with = params.get('concat_with', '')
            select_expr = f"CONCAT({column_name}, '{concat_with}') as concat_result"
        elif function_type == 'LENGTH':
            select_expr = f'LENGTH({column_name}) as length_result'
        else:
            raise ValueError(f'Неподдерживаемая функция: {function_type}')
        query = f'SELECT {column_name}, {select_expr} FROM bank_system.{table_name}'
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            return (results, column_names)
        except psycopg2.Error as e:
            self.connection.rollback()
            self.logger.error(f'String function error: {e}')
            raise ValueError(f'Ошибка функции: {e}')
        finally:
            cursor.close()

    def execute_join(self, table1: str, table2: str, join_column1: str, join_column2: str, join_type: str='INNER', columns: List[str]=None) -> Tuple[List[Tuple], List[str]]:
        select_cols = ', '.join(columns) if columns else '*'
        query = f'\n            SELECT {select_cols} \n            FROM bank_system.{table1} t1 \n            {join_type} JOIN bank_system.{table2} t2 \n            ON t1.{join_column1} = t2.{join_column2}\n        '
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            return (results, column_names)
        except psycopg2.Error as e:
            self.connection.rollback()
            self.logger.error(f'Join error: {e}')
            raise ValueError(f'Ошибка соединения: {e}')
        finally:
            cursor.close()

    def execute_subquery_filter(self, main_table: str, subquery_table: str, operator: str, column: str, sub_column: str) -> Tuple[List[Tuple], List[str]]:
        try:
            if operator == 'IN':
                query = f'\n                    SELECT * FROM bank_system.{main_table}\n                    WHERE {column}::text IN (SELECT {sub_column}::text FROM bank_system.{subquery_table})\n                '
            elif operator == 'ANY':
                query = f'\n                    SELECT * FROM bank_system.{main_table}\n                    WHERE {column}::text = ANY(SELECT {sub_column}::text FROM bank_system.{subquery_table})\n                '
            elif operator == 'ALL':
                query = f'\n                    SELECT * FROM bank_system.{main_table}\n                    WHERE {column}::text = ALL(SELECT {sub_column}::text FROM bank_system.{subquery_table})\n                '
            elif operator == 'EXISTS':
                query = f'\n                    SELECT * FROM bank_system.{main_table}\n                    WHERE EXISTS (SELECT 1 FROM bank_system.{subquery_table} WHERE {sub_column}::text = {column}::text)\n                '
            else:
                raise ValueError(f'Неподдерживаемый оператор: {operator}')
            cursor = self.connection.cursor()
            try:
                cursor.execute(query)
                results = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
                self.connection.commit()
                return (results, column_names)
            finally:
                cursor.close()
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f'Subquery filter error: {e}')
            raise

    def execute_aggregation(self, table: str, agg_func: str, agg_column: str, group_by_column: str=None, having: str=None) -> Tuple[List[Tuple], List[str]]:
        try:
            query = f'SELECT {agg_func}({agg_column})'
            if group_by_column:
                query += f', {group_by_column}'
            query += f' FROM bank_system.{table}'
            if group_by_column:
                query += f' GROUP BY {group_by_column}'
            if having:
                query += f' HAVING {having}'
            cursor = self.connection.cursor()
            try:
                cursor.execute(query)
                results = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
                self.connection.commit()
                return (results, column_names)
            finally:
                cursor.close()
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f'Aggregation error: {e}')
            raise

    def execute_case_expression(self, table: str, case_expr: str, select_cols: str='*') -> Tuple[List[Tuple], List[str]]:
        try:
            query = f'SELECT {select_cols}, {case_expr} as case_result FROM bank_system.{table}'
            cursor = self.connection.cursor()
            try:
                cursor.execute(query)
                results = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
                self.connection.commit()
                return (results, column_names)
            finally:
                cursor.close()
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f'CASE expression error: {e}')
            raise

    def execute_coalesce_nullif(self, table: str, func_type: str, column: str, coalesce_values: list=None, nullif_val1: str=None, nullif_val2: str=None, select_cols: str='*') -> Tuple[List[Tuple], List[str]]:
        try:
            if func_type == 'COALESCE':
                if not coalesce_values:
                    coalesce_values = ['NULL', "'default'"]
                values_str = ', '.join(coalesce_values)
                expr = f'COALESCE({column}, {values_str})'
            elif func_type == 'NULLIF':
                expr = f'NULLIF({column}, {nullif_val1})'
            else:
                raise ValueError(f'Unknown function: {func_type}')
            query = f'SELECT {select_cols}, {expr} as result FROM bank_system.{table}'
            cursor = self.connection.cursor()
            try:
                cursor.execute(query)
                results = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
                self.connection.commit()
                return (results, column_names)
            finally:
                cursor.close()
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f'NULL function error: {e}')
            raise

    def execute_advanced_grouping(self, table: str, select_cols: str, group_type: str, group_cols: list, where: str=None, having: str=None, order: str=None) -> Tuple[List[Tuple], List[str]]:
        try:
            query = f'SELECT {select_cols} FROM bank_system.{table}'
            if where:
                query += f' WHERE {where}'
            group_clause = ', '.join(group_cols)
            if group_type == 'ROLLUP':
                query += f' GROUP BY ROLLUP({group_clause})'
            elif group_type == 'CUBE':
                query += f' GROUP BY CUBE({group_clause})'
            elif group_type == 'GROUPING_SETS':
                query += f' GROUP BY GROUPING SETS (({group_clause}))'
            else:
                query += f' GROUP BY {group_clause}'
            if having:
                query += f' HAVING {having}'
            if order:
                query += f' ORDER BY {order}'
            cursor = self.connection.cursor()
            try:
                cursor.execute(query)
                results = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
                self.connection.commit()
                return (results, column_names)
            finally:
                cursor.close()
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f'Advanced grouping error: {e}')
            raise

    def create_view(self, view_name: str, sql_query: str) -> bool:
        try:
            cursor = self.connection.cursor()
            try:
                cursor.execute("SELECT EXISTS (SELECT 1 FROM pg_views WHERE viewname = %s AND schemaname = 'bank_system')", (view_name,))
                if cursor.fetchone()[0]:
                    raise Exception(f"View '{view_name}' already exists")
                create_view_sql = f'CREATE VIEW bank_system.{view_name} AS {sql_query}'
                cursor.execute(create_view_sql)
                self.connection.commit()
                return True
            finally:
                cursor.close()
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f'Create view error: {e}')
            raise

    def get_views(self) -> List[str]:
        try:
            cursor = self.connection.cursor()
            try:
                cursor.execute("SELECT viewname FROM pg_views WHERE schemaname = 'bank_system' AND viewname NOT LIKE 'pg_%' ORDER BY viewname")
                views = [row[0] for row in cursor.fetchall()]
                return views
            finally:
                cursor.close()
        except Exception as e:
            self.logger.error(f'Get views error: {e}')
            return []

    def get_view_definition(self, view_name: str) -> str:
        try:
            cursor = self.connection.cursor()
            try:
                cursor.execute("SELECT definition FROM pg_views WHERE viewname = %s AND schemaname = 'bank_system'", (view_name,))
                result = cursor.fetchone()
                return result[0] if result else ''
            finally:
                cursor.close()
        except Exception as e:
            self.logger.error(f'Get view definition error: {e}')
            raise

    def drop_view(self, view_name: str, cascade: bool=False) -> bool:
        try:
            cursor = self.connection.cursor()
            try:
                cascade_str = 'CASCADE' if cascade else 'RESTRICT'
                drop_view_sql = f'DROP VIEW bank_system.{view_name} {cascade_str}'
                cursor.execute(drop_view_sql)
                self.connection.commit()
                self.logger.info(f"View '{view_name}' dropped successfully")
                return True
            finally:
                cursor.close()
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f'Drop view error: {e}')
            raise

    def get_materialized_views(self) -> List[str]:
        try:
            cursor = self.connection.cursor()
            try:
                cursor.execute("SELECT matviewname FROM pg_matviews WHERE schemaname = 'bank_system' ORDER BY matviewname")
                mviews = [row[0] for row in cursor.fetchall()]
                return mviews
            finally:
                cursor.close()
        except Exception as e:
            self.logger.error(f'Get materialized views error: {e}')
            return []

    def create_materialized_view(self, view_name: str, sql_query: str) -> bool:
        try:
            cursor = self.connection.cursor()
            try:
                cursor.execute("SELECT EXISTS (SELECT 1 FROM pg_matviews WHERE matviewname = %s AND schemaname = 'bank_system')", (view_name,))
                if cursor.fetchone()[0]:
                    raise Exception(f"Materialized view '{view_name}' already exists")
                create_mview_sql = f'CREATE MATERIALIZED VIEW bank_system.{view_name} AS {sql_query}'
                cursor.execute(create_mview_sql)
                self.connection.commit()
                return True
            finally:
                cursor.close()
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f'Create materialized view error: {e}')
            raise

    def get_materialized_view_definition(self, view_name: str) -> str:
        try:
            cursor = self.connection.cursor()
            try:
                cursor.execute("SELECT definition FROM pg_matviews WHERE matviewname = %s AND schemaname = 'bank_system'", (view_name,))
                result = cursor.fetchone()
                return result[0] if result else 'Определение не найдено'
            finally:
                cursor.close()
        except Exception as e:
            self.logger.error(f'Get materialized view definition error: {e}')
            raise

    def refresh_materialized_view(self, view_name: str, concurrent: bool=False) -> bool:
        try:
            cursor = self.connection.cursor()
            try:
                concurrent_str = 'CONCURRENTLY' if concurrent else ''
                sql = f'REFRESH MATERIALIZED VIEW {concurrent_str} bank_system.{view_name}'
                cursor.execute(sql)
                self.connection.commit()
                return True
            finally:
                cursor.close()
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f'Refresh materialized view error: {e}')
            raise

    def drop_materialized_view(self, view_name: str, cascade: bool=False) -> bool:
        try:
            cursor = self.connection.cursor()
            try:
                cascade_str = 'CASCADE' if cascade else 'RESTRICT'
                drop_sql = f'DROP MATERIALIZED VIEW {cascade_str} bank_system.{view_name}'
                cursor.execute(drop_sql)
                self.connection.commit()
                return True
            finally:
                cursor.close()
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f'Drop materialized view error: {e}')
            raise
