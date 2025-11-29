import psycopg2
from psycopg2 import sql
import logging
from typing import List, Dict, Any, Tuple

class CustomTypesManager:

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.logger = logging.getLogger('CustomTypesManager')

    def get_all_types(self) -> List[Dict[str, Any]]:
        query = "\n            SELECT t.typname, t.typtype, \n                   (SELECT string_agg(a.attname, ', ') FROM pg_attribute a \n                    WHERE a.attrelid = t.typrelid) as fields\n            FROM pg_type t\n            WHERE t.typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'bank_system')\n            ORDER BY t.typname\n        "
        cursor = self.db_manager.connection.cursor()
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            types = []
            for row in results:
                types.append({'name': row[0], 'type': row[1], 'fields': row[2]})
            return types
        finally:
            cursor.close()

    def create_composite_type(self, type_name: str, fields: List[Dict[str, str]]) -> bool:
        field_defs = ', '.join([f"{f['name']} {f['type']}" for f in fields])
        query = f'CREATE TYPE bank_system.{type_name} AS ({field_defs})'
        cursor = self.db_manager.connection.cursor()
        try:
            cursor.execute(query)
            self.db_manager.connection.commit()
            self.logger.info(f'Composite type {type_name} created')
            return True
        except Exception as e:
            self.db_manager.connection.rollback()
            self.logger.error(f'Error creating type: {e}')
            raise
        finally:
            cursor.close()

    def drop_type(self, type_name: str) -> bool:
        query = f'DROP TYPE IF EXISTS bank_system.{type_name} CASCADE'
        cursor = self.db_manager.connection.cursor()
        try:
            cursor.execute(query)
            self.db_manager.connection.commit()
            self.logger.info(f'Type {type_name} dropped')
            return True
        except Exception as e:
            self.db_manager.connection.rollback()
            self.logger.error(f'Error dropping type: {e}')
            raise
        finally:
            cursor.close()

    def get_type_columns(self, type_name: str) -> List[Dict[str, str]]:
        query = "\n            SELECT a.attname, t.typname\n            FROM pg_attribute a\n            JOIN pg_type t ON a.atttypid = t.oid\n            JOIN pg_type pt ON a.attrelid = pt.typrelid\n            WHERE pt.typname = %s AND pt.typnamespace = \n                  (SELECT oid FROM pg_namespace WHERE nspname = 'bank_system')\n            ORDER BY a.attnum\n        "
        cursor = self.db_manager.connection.cursor()
        try:
            cursor.execute(query, (type_name,))
            results = cursor.fetchall()
            columns = []
            for row in results:
                columns.append({'name': row[0], 'type': row[1]})
            return columns
        finally:
            cursor.close()
