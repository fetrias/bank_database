from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QGridLayout, QTextEdit,
                               QComboBox, QMessageBox, QTabWidget, QWidget,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QGroupBox, QScrollArea)
from PySide6.QtCore import Qt
from typing import Callable
import logging


class ConnectionDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.connection_params = None

        self.setWindowTitle("Подключение к PostgreSQL")
        self.setModal(True)
        self.setMinimumWidth(400)

        self.setup_ui()

    def setup_ui(self):
        """Настроить пользовательский интерфейс"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        self.setStyleSheet("""
            QPushButton {
                background-color: #2E86AB;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1B5B7E;
            }
        """)

        grid = QGridLayout()
        grid.setSpacing(10)

        self.host_edit = QLineEdit("localhost")
        self.port_edit = QLineEdit("5433")
        self.database_edit = QLineEdit("postgres")
        self.user_edit = QLineEdit("postgres")
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)

        grid.addWidget(QLabel("Хост:"), 0, 0)
        grid.addWidget(self.host_edit, 0, 1)

        grid.addWidget(QLabel("Порт:"), 1, 0)
        grid.addWidget(self.port_edit, 1, 1)

        grid.addWidget(QLabel("База данных:"), 2, 0)
        grid.addWidget(self.database_edit, 2, 1)

        grid.addWidget(QLabel("Пользователь:"), 3, 0)
        grid.addWidget(self.user_edit, 3, 1)

        grid.addWidget(QLabel("Пароль:"), 4, 0)
        grid.addWidget(self.password_edit, 4, 1)

        layout.addLayout(grid)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        connect_btn = QPushButton("Подключиться")
        connect_btn.clicked.connect(self.on_connect)
        buttons_layout.addWidget(connect_btn)

        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("background-color: #6c757d;")
        buttons_layout.addWidget(cancel_btn)

        layout.addLayout(buttons_layout)

    def on_connect(self):
        self.connection_params = {
            'host': self.host_edit.text().strip(),
            'port': self.port_edit.text().strip(),
            'database': self.database_edit.text().strip(),
            'user': self.user_edit.text().strip(),
            'password': self.password_edit.text()
        }

        if not all([self.connection_params['host'], self.connection_params['port'],
                    self.connection_params['database'], self.connection_params['user']]):
            QMessageBox.critical(self, "Ошибка", "Заполните все поля (кроме пароля)")
            return

        self.accept()

    def get_connection_params(self):
        return self.connection_params


class AddDataDialog(QDialog):

    def __init__(self, parent, db_manager, log_callback: Callable):
        super().__init__(parent)
        self.db_manager = db_manager
        self.log_callback = log_callback
        self.logger = logging.getLogger('AddDataDialog')

        self.setWindowTitle("Добавить данные")
        self.setModal(True)
        self.resize(700, 750)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)

        title = QLabel("Выберите таблицу для добавления данных:")
        title.setStyleSheet("font-weight: bold; font-size: 11pt;")
        layout.addWidget(title)

        self.tabs = QTabWidget()

        self.create_currency_tab()
        self.create_exchange_rate_tab()
        self.create_client_tab()
        self.create_account_tab()
        self.create_transaction_tab()

        layout.addWidget(self.tabs)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("background-color: #6c757d;")
        layout.addWidget(close_btn)

    def create_currency_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        grid = QGridLayout(scroll_content)
        grid.setSpacing(8)

        self.currency_entries = {}

        row = 0
        grid.addWidget(QLabel("Код валюты (3 буквы):"), row, 0)
        self.currency_entries['code'] = QLineEdit()
        self.currency_entries['code'].setMaxLength(3)
        self.currency_entries['code'].setPlaceholderText("USD")
        grid.addWidget(self.currency_entries['code'], row, 1)

        row += 1
        grid.addWidget(QLabel("Название валюты:"), row, 0)
        self.currency_entries['name'] = QLineEdit()
        self.currency_entries['name'].setPlaceholderText("Доллар США")
        grid.addWidget(self.currency_entries['name'], row, 1)

        row += 1
        grid.addWidget(QLabel("Символ:"), row, 0)
        self.currency_entries['symbol'] = QLineEdit()
        self.currency_entries['symbol'].setPlaceholderText("$")
        grid.addWidget(self.currency_entries['symbol'], row, 1)

        row += 1
        grid.addWidget(QLabel("Активна:"), row, 0)
        self.currency_entries['is_active'] = QComboBox()
        self.currency_entries['is_active'].addItems(['True', 'False'])
        grid.addWidget(self.currency_entries['is_active'], row, 1)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        add_btn = QPushButton("Добавить валюту")
        add_btn.clicked.connect(self.insert_currency)
        layout.addWidget(add_btn)

        self.tabs.addTab(widget, "Валюты")

    def create_exchange_rate_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        grid = QGridLayout(scroll_content)
        grid.setSpacing(8)

        self.rate_entries = {}

        row = 0
        grid.addWidget(QLabel("Базовая валюта:"), row, 0)
        self.rate_entries['base_currency'] = QLineEdit()
        self.rate_entries['base_currency'].setMaxLength(3)
        self.rate_entries['base_currency'].setPlaceholderText("USD")
        grid.addWidget(self.rate_entries['base_currency'], row, 1)

        row += 1
        grid.addWidget(QLabel("Целевая валюта:"), row, 0)
        self.rate_entries['target_currency'] = QLineEdit()
        self.rate_entries['target_currency'].setMaxLength(3)
        self.rate_entries['target_currency'].setPlaceholderText("RUB")
        grid.addWidget(self.rate_entries['target_currency'], row, 1)

        row += 1
        grid.addWidget(QLabel("Курс покупки:"), row, 0)
        self.rate_entries['buy_rate'] = QLineEdit()
        self.rate_entries['buy_rate'].setPlaceholderText("75.50")
        grid.addWidget(self.rate_entries['buy_rate'], row, 1)

        row += 1
        grid.addWidget(QLabel("Курс продажи:"), row, 0)
        self.rate_entries['sell_rate'] = QLineEdit()
        self.rate_entries['sell_rate'].setPlaceholderText("76.50")
        grid.addWidget(self.rate_entries['sell_rate'], row, 1)

        row += 1
        grid.addWidget(QLabel("Обновил (ФИО):"), row, 0)
        self.rate_entries['updated_by'] = QLineEdit()
        self.rate_entries['updated_by'].setPlaceholderText("Иванов И.И.")
        grid.addWidget(self.rate_entries['updated_by'], row, 1)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        add_btn = QPushButton("Добавить курс")
        add_btn.clicked.connect(self.insert_exchange_rate)
        layout.addWidget(add_btn)

        self.tabs.addTab(widget, "Курсы валют")

    def create_client_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        grid = QGridLayout(scroll_content)
        grid.setSpacing(8)

        self.client_entries = {}

        row = 0
        grid.addWidget(QLabel("ФИО клиента:"), row, 0)
        self.client_entries['full_name'] = QLineEdit()
        self.client_entries['full_name'].setPlaceholderText("Иванов Иван Иванович")
        grid.addWidget(self.client_entries['full_name'], row, 1)

        row += 1
        grid.addWidget(QLabel("Номер паспорта:"), row, 0)
        self.client_entries['passport'] = QLineEdit()
        self.client_entries['passport'].setPlaceholderText("1234 567890")
        grid.addWidget(self.client_entries['passport'], row, 1)

        row += 1
        grid.addWidget(QLabel("Телефон:"), row, 0)
        self.client_entries['phone'] = QLineEdit()
        self.client_entries['phone'].setPlaceholderText("+7 (999) 123-45-67")
        grid.addWidget(self.client_entries['phone'], row, 1)

        row += 1
        grid.addWidget(QLabel("Email:"), row, 0)
        self.client_entries['email'] = QLineEdit()
        self.client_entries['email'].setPlaceholderText("ivanov@example.com")
        grid.addWidget(self.client_entries['email'], row, 1)

        row += 1
        grid.addWidget(QLabel("Дата рождения:"), row, 0)
        self.client_entries['birth_date'] = QLineEdit()
        self.client_entries['birth_date'].setPlaceholderText("1990-01-01")
        grid.addWidget(self.client_entries['birth_date'], row, 1)

        row += 1
        grid.addWidget(QLabel("VIP клиент:"), row, 0)
        self.client_entries['is_vip'] = QComboBox()
        self.client_entries['is_vip'].addItems(['False', 'True'])
        grid.addWidget(self.client_entries['is_vip'], row, 1)

        row += 1
        grid.addWidget(QLabel("Разрешенные операции:"), row, 0)
        self.client_entries['allowed_ops'] = QLineEdit()
        self.client_entries['allowed_ops'].setPlaceholderText("BUY,SELL,TRANSFER")
        grid.addWidget(self.client_entries['allowed_ops'], row, 1)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        add_btn = QPushButton("Добавить клиента")
        add_btn.clicked.connect(self.insert_client)
        layout.addWidget(add_btn)

        self.tabs.addTab(widget, "Клиенты")

    def create_account_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        grid = QGridLayout(scroll_content)
        grid.setSpacing(8)

        self.account_entries = {}

        row = 0
        grid.addWidget(QLabel("ID клиента:"), row, 0)
        self.account_entries['client_id'] = QLineEdit()
        self.account_entries['client_id'].setPlaceholderText("1")
        grid.addWidget(self.account_entries['client_id'], row, 1)

        row += 1
        grid.addWidget(QLabel("Код валюты:"), row, 0)
        self.account_entries['currency_code'] = QLineEdit()
        self.account_entries['currency_code'].setMaxLength(3)
        self.account_entries['currency_code'].setPlaceholderText("USD")
        grid.addWidget(self.account_entries['currency_code'], row, 1)

        row += 1
        grid.addWidget(QLabel("Номер счета:"), row, 0)
        self.account_entries['account_number'] = QLineEdit()
        self.account_entries['account_number'].setPlaceholderText("40702810500000012345")
        grid.addWidget(self.account_entries['account_number'], row, 1)

        row += 1
        grid.addWidget(QLabel("Начальный баланс:"), row, 0)
        self.account_entries['balance'] = QLineEdit()
        self.account_entries['balance'].setText("0.00")
        grid.addWidget(self.account_entries['balance'], row, 1)

        row += 1
        grid.addWidget(QLabel("Статус счета:"), row, 0)
        self.account_entries['status'] = QComboBox()
        self.account_entries['status'].addItems(['ACTIVE', 'BLOCKED', 'CLOSED'])
        grid.addWidget(self.account_entries['status'], row, 1)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        add_btn = QPushButton("Добавить счет")
        add_btn.clicked.connect(self.insert_account)
        layout.addWidget(add_btn)

        self.tabs.addTab(widget, "Валютные счета")

    def create_transaction_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        grid = QGridLayout(scroll_content)
        grid.setSpacing(8)

        self.trans_entries = {}

        row = 0
        grid.addWidget(QLabel("ID счета:"), row, 0)
        self.trans_entries['account_id'] = QLineEdit()
        self.trans_entries['account_id'].setPlaceholderText("1")
        grid.addWidget(self.trans_entries['account_id'], row, 1)

        row += 1
        grid.addWidget(QLabel("Тип операции:"), row, 0)
        self.trans_entries['trans_type'] = QComboBox()
        self.trans_entries['trans_type'].addItems(['BUY', 'SELL', 'TRANSFER', 'DEPOSIT', 'WITHDRAWAL'])
        grid.addWidget(self.trans_entries['trans_type'], row, 1)

        row += 1
        grid.addWidget(QLabel("Сумма:"), row, 0)
        self.trans_entries['amount'] = QLineEdit()
        self.trans_entries['amount'].setPlaceholderText("1000.00")
        grid.addWidget(self.trans_entries['amount'], row, 1)

        row += 1
        grid.addWidget(QLabel("Валюта:"), row, 0)
        self.trans_entries['currency_code'] = QLineEdit()
        self.trans_entries['currency_code'].setMaxLength(3)
        self.trans_entries['currency_code'].setPlaceholderText("USD")
        grid.addWidget(self.trans_entries['currency_code'], row, 1)

        row += 1
        grid.addWidget(QLabel("Курс обмена (опц):"), row, 0)
        self.trans_entries['exchange_rate'] = QLineEdit()
        self.trans_entries['exchange_rate'].setPlaceholderText("75.50")
        grid.addWidget(self.trans_entries['exchange_rate'], row, 1)

        row += 1
        grid.addWidget(QLabel("Комиссия:"), row, 0)
        self.trans_entries['commission'] = QLineEdit()
        self.trans_entries['commission'].setText("0.00")
        grid.addWidget(self.trans_entries['commission'], row, 1)

        row += 1
        grid.addWidget(QLabel("Описание:"), row, 0, Qt.AlignmentFlag.AlignTop)
        self.trans_entries['description'] = QTextEdit()
        self.trans_entries['description'].setMaximumHeight(60)
        self.trans_entries['description'].setPlaceholderText("Описание операции...")
        grid.addWidget(self.trans_entries['description'], row, 1)

        row += 1
        grid.addWidget(QLabel("Сотрудник (ФИО):"), row, 0)
        self.trans_entries['employee'] = QLineEdit()
        self.trans_entries['employee'].setPlaceholderText("Петров П.П.")
        grid.addWidget(self.trans_entries['employee'], row, 1)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        add_btn = QPushButton("Добавить транзакцию")
        add_btn.clicked.connect(self.insert_transaction)
        layout.addWidget(add_btn)

        self.tabs.addTab(widget, "Транзакции")

    def insert_currency(self):
        try:
            code = self.currency_entries['code'].text().strip().upper()
            name = self.currency_entries['name'].text().strip()
            symbol = self.currency_entries['symbol'].text().strip()
            is_active = self.currency_entries['is_active'].currentText() == 'True'

            currency_id = self.db_manager.insert_currency(code, name, symbol, is_active)

            QMessageBox.information(self, "Успех", f"Валюта добавлена с ID: {currency_id}")
            self.log_callback(f"Добавлена валюта '{code}' (ID: {currency_id})")
            self.clear_entries(self.currency_entries)

        except ValueError as e:
            QMessageBox.critical(self, "Ошибка", str(e))
            self.logger.error(f"Insert currency error: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Неверный формат данных:\n{str(e)}")
            self.logger.error(f"Insert currency error: {e}")

    def insert_exchange_rate(self):
        try:
            base_currency = self.rate_entries['base_currency'].text().strip().upper()
            target_currency = self.rate_entries['target_currency'].text().strip().upper()
            buy_rate = float(self.rate_entries['buy_rate'].text().strip())
            sell_rate = float(self.rate_entries['sell_rate'].text().strip())
            updated_by = self.rate_entries['updated_by'].text().strip()

            rate_id = self.db_manager.insert_exchange_rate(
                base_currency, target_currency, buy_rate, sell_rate, updated_by
            )

            QMessageBox.information(self, "Успех", f"Курс добавлен с ID: {rate_id}")
            self.log_callback(f"Добавлен курс {base_currency}/{target_currency} (ID: {rate_id})")
            self.clear_entries(self.rate_entries)

        except ValueError as e:
            QMessageBox.critical(self, "Ошибка", str(e))
            self.logger.error(f"Insert exchange rate error: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Неверный формат данных:\n{str(e)}")
            self.logger.error(f"Insert exchange rate error: {e}")

    def insert_client(self):
        try:
            full_name = self.client_entries['full_name'].text().strip()
            passport = self.client_entries['passport'].text().strip()
            phone = self.client_entries['phone'].text().strip()
            email = self.client_entries['email'].text().strip()
            birth_date = self.client_entries['birth_date'].text().strip()
            is_vip = self.client_entries['is_vip'].currentText() == 'True'
            allowed_ops_str = self.client_entries['allowed_ops'].text().strip()
            allowed_ops = [x.strip() for x in allowed_ops_str.split(',')]

            client_id = self.db_manager.insert_client(
                full_name, passport, phone, email, birth_date, is_vip, allowed_ops
            )

            QMessageBox.information(self, "Успех", f"Клиент добавлен с ID: {client_id}")
            self.log_callback(f"Добавлен клиент '{full_name}' (ID: {client_id})")
            self.clear_entries(self.client_entries)

        except ValueError as e:
            QMessageBox.critical(self, "Ошибка", str(e))
            self.logger.error(f"Insert client error: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Неверный формат данных:\n{str(e)}")
            self.logger.error(f"Insert client error: {e}")

    def insert_account(self):
        try:
            client_id = int(self.account_entries['client_id'].text().strip())
            currency_code = self.account_entries['currency_code'].text().strip().upper()
            account_number = self.account_entries['account_number'].text().strip()
            balance = float(self.account_entries['balance'].text().strip())
            status = self.account_entries['status'].currentText()

            account_id = self.db_manager.insert_account(
                client_id, currency_code, account_number, balance, status
            )

            QMessageBox.information(self, "Успех", f"Счет добавлен с ID: {account_id}")
            self.log_callback(f"Добавлен счет '{account_number}' (ID: {account_id})")
            self.clear_entries(self.account_entries)

        except ValueError as e:
            QMessageBox.critical(self, "Ошибка", str(e))
            self.logger.error(f"Insert account error: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Неверный формат данных:\n{str(e)}")
            self.logger.error(f"Insert account error: {e}")

    def insert_transaction(self):
        try:
            account_id = int(self.trans_entries['account_id'].text().strip())
            trans_type = self.trans_entries['trans_type'].currentText()
            amount = float(self.trans_entries['amount'].text().strip())
            currency_code = self.trans_entries['currency_code'].text().strip().upper()

            exchange_rate_str = self.trans_entries['exchange_rate'].text().strip()
            exchange_rate = float(exchange_rate_str) if exchange_rate_str else None

            commission = float(self.trans_entries['commission'].text().strip())
            description = self.trans_entries['description'].toPlainText().strip()
            employee = self.trans_entries['employee'].text().strip()

            trans_id = self.db_manager.insert_transaction(
                account_id, trans_type, amount, currency_code,
                exchange_rate, commission, description, employee
            )

            QMessageBox.information(self, "Успех", f"Транзакция добавлена с ID: {trans_id}")
            self.log_callback(f"Добавлена транзакция {trans_type} (ID: {trans_id})")
            self.clear_entries(self.trans_entries)

        except ValueError as e:
            QMessageBox.critical(self, "Ошибка", str(e))
            self.logger.error(f"Insert transaction error: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Неверный формат данных:\n{str(e)}")
            self.logger.error(f"Insert transaction error: {e}")

    def clear_entries(self, entries_dict):
        for key, widget in entries_dict.items():
            if isinstance(widget, QLineEdit):
                widget.clear()
            elif isinstance(widget, QTextEdit):
                widget.clear()
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)


class ViewDataDialog(QDialog):

    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager
        self.logger = logging.getLogger('ViewDataDialog')

        self.setWindowTitle("Просмотр данных")
        self.setModal(True)
        self.resize(1300, 750)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
            /* СТИЛИ ДЛЯ ТАБЛИЦ */
            QTableWidget {
                background-color: white;
                gridline-color: #d0d0d0;
                border: 1px solid #cccccc;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTableWidget::item:selected {
                background-color: #2E86AB;
                color: white;
            }
            QHeaderView::section {
                background-color: #2E86AB;
                color: white;
                padding: 8px;
                font-weight: bold;
                border: none;
            }
        """)

        title = QLabel("Просмотр данных из базы")
        title.setStyleSheet("font-weight: bold; font-size: 12pt;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.tabs = QTabWidget()

        self.create_currencies_tab()
        self.create_exchange_rates_tab()
        self.create_clients_tab()
        self.create_accounts_tab()
        self.create_transactions_tab()

        layout.addWidget(self.tabs)

        buttons_layout = QHBoxLayout()

        drop_btn = QPushButton("Удалить схему")
        drop_btn.clicked.connect(self.drop_schema)
        drop_btn.setStyleSheet("background-color: #dc3545;")
        buttons_layout.addWidget(drop_btn)

        buttons_layout.addStretch()

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("background-color: #6c757d;")
        buttons_layout.addWidget(close_btn)

        layout.addLayout(buttons_layout)

    def create_currencies_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        load_btn = QPushButton("Загрузить данные")
        load_btn.clicked.connect(self.load_currencies)
        layout.addWidget(load_btn)

        self.currencies_table = QTableWidget()
        self.currencies_table.setColumnCount(5)
        self.currencies_table.setHorizontalHeaderLabels([
            'ID', 'Код', 'Название', 'Символ', 'Активна'
        ])
        self.currencies_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.currencies_table.verticalHeader().setDefaultSectionSize(30)
        layout.addWidget(self.currencies_table)

        self.tabs.addTab(widget, "Валюты")

    def create_exchange_rates_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        controls_layout = QHBoxLayout()

        controls_layout.addWidget(QLabel("Базовая валюта:"))
        self.base_currency_filter = QComboBox()
        self.base_currency_filter.addItems(['ALL', 'USD', 'EUR', 'RUB', 'GBP', 'CNY', 'JPY', 'CHF'])
        controls_layout.addWidget(self.base_currency_filter)

        load_btn = QPushButton("Применить фильтр")
        load_btn.clicked.connect(self.load_exchange_rates)
        controls_layout.addWidget(load_btn)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        self.rates_table = QTableWidget()
        self.rates_table.setColumnCount(7)
        self.rates_table.setHorizontalHeaderLabels([
            'ID', 'Базовая', 'Целевая', 'Курс покупки', 'Курс продажи', 'Дата', 'Обновил'
        ])
        self.rates_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.rates_table.verticalHeader().setDefaultSectionSize(30)
        layout.addWidget(self.rates_table)

        self.tabs.addTab(widget, "Курсы валют")

    def create_clients_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        load_btn = QPushButton("Загрузить данные")
        load_btn.clicked.connect(self.load_clients)
        layout.addWidget(load_btn)

        self.clients_table = QTableWidget()
        self.clients_table.setColumnCount(9)
        self.clients_table.setHorizontalHeaderLabels([
            'ID', 'ФИО', 'Паспорт', 'Телефон', 'Email',
            'Дата регистрации', 'Дата рождения', 'VIP', 'Разрешенные операции'
        ])
        self.clients_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.clients_table.verticalHeader().setDefaultSectionSize(30)
        layout.addWidget(self.clients_table)

        self.tabs.addTab(widget, "Клиенты")

    def create_accounts_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        controls_layout = QHBoxLayout()

        controls_layout.addWidget(QLabel("Валюта:"))
        self.account_currency_filter = QComboBox()
        self.account_currency_filter.addItems(['ALL', 'RUB', 'USD', 'EUR', 'GBP', 'CNY', 'JPY'])
        controls_layout.addWidget(self.account_currency_filter)

        load_btn = QPushButton("Применить фильтр")
        load_btn.clicked.connect(self.load_accounts)
        controls_layout.addWidget(load_btn)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        self.accounts_table = QTableWidget()
        self.accounts_table.setColumnCount(8)
        self.accounts_table.setHorizontalHeaderLabels([
            'ID', 'Клиент', 'Валюта', 'Номер счета',
            'Баланс', 'Статус', 'Дата открытия', 'Последняя операция'
        ])
        self.accounts_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.accounts_table.verticalHeader().setDefaultSectionSize(30)
        layout.addWidget(self.accounts_table)

        self.tabs.addTab(widget, "Валютные счета")

    def create_transactions_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        controls_layout = QHBoxLayout()

        controls_layout.addWidget(QLabel("Тип:"))
        self.trans_type_filter = QComboBox()
        self.trans_type_filter.addItems(['ALL', 'BUY', 'SELL', 'TRANSFER', 'DEPOSIT', 'WITHDRAWAL'])
        controls_layout.addWidget(self.trans_type_filter)

        controls_layout.addWidget(QLabel("От даты:"))
        self.from_date_edit = QLineEdit("2024-01-01")
        self.from_date_edit.setMaximumWidth(100)
        controls_layout.addWidget(self.from_date_edit)

        controls_layout.addWidget(QLabel("До даты:"))
        self.to_date_edit = QLineEdit("2025-12-31")
        self.to_date_edit.setMaximumWidth(100)
        controls_layout.addWidget(self.to_date_edit)

        load_btn = QPushButton("Применить фильтр")
        load_btn.clicked.connect(self.load_transactions)
        controls_layout.addWidget(load_btn)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(11)
        self.transactions_table.setHorizontalHeaderLabels([
            'ID', 'Клиент', 'Счет', 'Тип', 'Сумма',
            'Валюта', 'Курс', 'Комиссия', 'Дата', 'Описание', 'Сотрудник'
        ])
        self.transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.transactions_table.verticalHeader().setDefaultSectionSize(30)
        layout.addWidget(self.transactions_table)

        self.tabs.addTab(widget, "Транзакции")

    def load_currencies(self):
        try:
            self.currencies_table.setRowCount(0)
            data = self.db_manager.get_currencies()

            self.currencies_table.setRowCount(len(data))
            for row_idx, row_data in enumerate(data):
                for col_idx, value in enumerate(row_data):
                    self.currencies_table.setItem(row_idx, col_idx,
                                                  QTableWidgetItem(str(value)))

            QMessageBox.information(self, "Успех", f"Загружено записей: {len(data)}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные:\n{str(e)}")
            self.logger.error(f"Load currencies error: {e}")

    def load_exchange_rates(self):
        try:
            self.rates_table.setRowCount(0)
            base_currency = self.base_currency_filter.currentText()
            data = self.db_manager.get_exchange_rates(base_currency)

            self.rates_table.setRowCount(len(data))
            for row_idx, row_data in enumerate(data):
                for col_idx, value in enumerate(row_data):
                    self.rates_table.setItem(row_idx, col_idx,
                                             QTableWidgetItem(str(value)))

            QMessageBox.information(self, "Успех", f"Загружено записей: {len(data)}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные:\n{str(e)}")
            self.logger.error(f"Load exchange rates error: {e}")

    def load_clients(self):
        try:
            self.clients_table.setRowCount(0)
            data = self.db_manager.get_clients()

            self.clients_table.setRowCount(len(data))
            for row_idx, row_data in enumerate(data):
                for col_idx, value in enumerate(row_data):
                    self.clients_table.setItem(row_idx, col_idx,
                                               QTableWidgetItem(str(value)))

            QMessageBox.information(self, "Успех", f"Загружено записей: {len(data)}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные:\n{str(e)}")
            self.logger.error(f"Load clients error: {e}")

    def load_accounts(self):
        try:
            self.accounts_table.setRowCount(0)
            currency = self.account_currency_filter.currentText()
            data = self.db_manager.get_accounts(currency=currency)

            self.accounts_table.setRowCount(len(data))
            for row_idx, row_data in enumerate(data):
                for col_idx, value in enumerate(row_data):
                    self.accounts_table.setItem(row_idx, col_idx,
                                                QTableWidgetItem(str(value)))

            QMessageBox.information(self, "Успех", f"Загружено записей: {len(data)}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные:\n{str(e)}")
            self.logger.error(f"Load accounts error: {e}")

    def load_transactions(self):
        try:
            self.transactions_table.setRowCount(0)

            trans_type = self.trans_type_filter.currentText()
            from_date = self.from_date_edit.text().strip()
            to_date = self.to_date_edit.text().strip()

            data = self.db_manager.get_transactions(
                trans_type=trans_type, from_date=from_date, to_date=to_date
            )

            self.transactions_table.setRowCount(len(data))
            for row_idx, row_data in enumerate(data):
                for col_idx, value in enumerate(row_data):
                    self.transactions_table.setItem(row_idx, col_idx,
                                                    QTableWidgetItem(str(value)))

            QMessageBox.information(self, "Успех", f"Загружено записей: {len(data)}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные:\n{str(e)}")
            self.logger.error(f"Load transactions error: {e}")

    def drop_schema(self):
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите удалить схему bank_system?\n\n"
            "Это действие удалит ВСЕ данные в схеме bank_system и не может быть отменено!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                if self.db_manager.drop_schema():
                    QMessageBox.information(
                        self,
                        "Успех",
                        "Схема bank_system успешно удалена.\n\n"
                        "Приложение может потребоваться перезапустить для полного обновления."
                    )
                    self.logger.info("Схема успешно удалена")
                else:
                    QMessageBox.warning(
                        self,
                        "Предупреждение",
                        "Не удалось удалить схему bank_system"
                    )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Ошибка",
                    f"Не удалось удалить схему:\n{str(e)}"
                )
                self.logger.error(f"Ошибка удаления схема: {e}")