from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QGridLayout, QTextEdit,
                               QComboBox, QMessageBox, QTabWidget, QWidget,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QGroupBox, QScrollArea, QCheckBox, QFormLayout, QApplication,
                               QListWidget)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QClipboard
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
        self.port_edit = QLineEdit("5432")
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


class AlterTableDialog(QDialog):
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager
        self.logger = logging.getLogger('AlterTableDialog')
        
        self.setWindowTitle("ALTER TABLE - Изменение структуры таблиц")
        self.setModal(True)
        self.resize(900, 700)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("Изменение структуры базы данных")
        title.setStyleSheet("font-weight: bold; font-size: 12pt;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        self.tabs = QTabWidget()
        
        self.create_add_column_tab()
        self.create_drop_column_tab()
        self.create_rename_column_tab()
        self.create_rename_table_tab()
        self.create_change_type_tab()
        self.create_constraints_tab()
        
        layout.addWidget(self.tabs)
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("background-color: #6c757d; color: white; padding: 8px;")
        layout.addWidget(close_btn)
    
    def create_add_column_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        grid = QGridLayout()
        
        grid.addWidget(QLabel("Таблица:"), 0, 0)
        self.add_col_table = QComboBox()
        self.add_col_table.addItems(self.get_tables())
        grid.addWidget(self.add_col_table, 0, 1)
        
        grid.addWidget(QLabel("Имя столбца:"), 1, 0)
        self.add_col_name = QLineEdit()
        grid.addWidget(self.add_col_name, 1, 1)
        
        grid.addWidget(QLabel("Тип данных:"), 2, 0)
        self.add_col_type = QComboBox()
        self.add_col_type.addItems(['VARCHAR(50)', 'VARCHAR(100)', 'INTEGER', 'NUMERIC(10,2)', 'BOOLEAN', 'DATE', 'TIMESTAMP', 'TEXT'])
        self.add_col_type.setEditable(True)
        grid.addWidget(self.add_col_type, 2, 1)
        
        grid.addWidget(QLabel("Ограничения:"), 3, 0)
        self.add_col_constraints = QLineEdit()
        self.add_col_constraints.setPlaceholderText("NOT NULL, DEFAULT 0, CHECK (...)")
        grid.addWidget(self.add_col_constraints, 3, 1)
        
        layout.addLayout(grid)
        
        btn = QPushButton("Добавить столбец")
        btn.clicked.connect(self.add_column)
        btn.setStyleSheet("background-color: #28a745; color: white; padding: 10px;")
        layout.addWidget(btn)
        
        layout.addStretch()
        self.tabs.addTab(widget, "Добавить столбец")
    
    def create_drop_column_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        grid = QGridLayout()
        
        grid.addWidget(QLabel("Таблица:"), 0, 0)
        self.drop_col_table = QComboBox()
        self.drop_col_table.addItems(self.get_tables())
        self.drop_col_table.currentTextChanged.connect(self.update_drop_columns)
        grid.addWidget(self.drop_col_table, 0, 1)
        
        grid.addWidget(QLabel("Столбец:"), 1, 0)
        self.drop_col_name = QComboBox()
        grid.addWidget(self.drop_col_name, 1, 1)
        
        layout.addLayout(grid)
        
        btn = QPushButton("Удалить столбец")
        btn.clicked.connect(self.drop_column)
        btn.setStyleSheet("background-color: #dc3545; color: white; padding: 10px;")
        layout.addWidget(btn)
        
        layout.addStretch()
        self.tabs.addTab(widget, "Удалить столбец")
        
        self.update_drop_columns()
    
    def create_rename_column_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        grid = QGridLayout()
        
        grid.addWidget(QLabel("Таблица:"), 0, 0)
        self.rename_col_table = QComboBox()
        self.rename_col_table.addItems(self.get_tables())
        self.rename_col_table.currentTextChanged.connect(self.update_rename_columns)
        grid.addWidget(self.rename_col_table, 0, 1)
        
        grid.addWidget(QLabel("Старое имя:"), 1, 0)
        self.rename_col_old = QComboBox()
        grid.addWidget(self.rename_col_old, 1, 1)
        
        grid.addWidget(QLabel("Новое имя:"), 2, 0)
        self.rename_col_new = QLineEdit()
        grid.addWidget(self.rename_col_new, 2, 1)
        
        layout.addLayout(grid)
        
        btn = QPushButton("Переименовать столбец")
        btn.clicked.connect(self.rename_column)
        btn.setStyleSheet("background-color: #17a2b8; color: white; padding: 10px;")
        layout.addWidget(btn)
        
        layout.addStretch()
        self.tabs.addTab(widget, "Переименовать столбец")
        
        self.update_rename_columns()
    
    def create_rename_table_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        grid = QGridLayout()
        
        grid.addWidget(QLabel("Старое имя таблицы:"), 0, 0)
        self.rename_table_old = QComboBox()
        self.rename_table_old.addItems(self.get_tables())
        grid.addWidget(self.rename_table_old, 0, 1)
        
        grid.addWidget(QLabel("Новое имя таблицы:"), 1, 0)
        self.rename_table_new = QLineEdit()
        grid.addWidget(self.rename_table_new, 1, 1)
        
        layout.addLayout(grid)
        
        btn = QPushButton("Переименовать таблицу")
        btn.clicked.connect(self.rename_table)
        btn.setStyleSheet("background-color: #ffc107; color: black; padding: 10px;")
        layout.addWidget(btn)
        
        layout.addStretch()
        self.tabs.addTab(widget, "Переименовать таблицу")
    
    def create_change_type_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        grid = QGridLayout()
        
        grid.addWidget(QLabel("Таблица:"), 0, 0)
        self.change_type_table = QComboBox()
        self.change_type_table.addItems(self.get_tables())
        self.change_type_table.currentTextChanged.connect(self.update_change_type_columns)
        grid.addWidget(self.change_type_table, 0, 1)
        
        grid.addWidget(QLabel("Столбец:"), 1, 0)
        self.change_type_column = QComboBox()
        grid.addWidget(self.change_type_column, 1, 1)
        
        grid.addWidget(QLabel("Новый тип:"), 2, 0)
        self.change_type_new = QComboBox()
        self.change_type_new.addItems(['VARCHAR(50)', 'VARCHAR(100)', 'INTEGER', 'NUMERIC(10,2)', 'BOOLEAN', 'DATE', 'TIMESTAMP', 'TEXT'])
        self.change_type_new.setEditable(True)
        grid.addWidget(self.change_type_new, 2, 1)
        
        layout.addLayout(grid)
        
        btn = QPushButton("Изменить тип данных")
        btn.clicked.connect(self.change_type)
        btn.setStyleSheet("background-color: #6610f2; color: white; padding: 10px;")
        layout.addWidget(btn)
        
        layout.addStretch()
        self.tabs.addTab(widget, "Изменить тип")
        
        self.update_change_type_columns()
    
    def create_constraints_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        constraint_tabs = QTabWidget()
        
        not_null_widget = QWidget()
        not_null_layout = QVBoxLayout(not_null_widget)
        grid1 = QGridLayout()
        grid1.addWidget(QLabel("Таблица:"), 0, 0)
        self.nn_table = QComboBox()
        self.nn_table.addItems(self.get_tables())
        self.nn_table.currentTextChanged.connect(self.update_nn_columns)
        grid1.addWidget(self.nn_table, 0, 1)
        grid1.addWidget(QLabel("Столбец:"), 1, 0)
        self.nn_column = QComboBox()
        grid1.addWidget(self.nn_column, 1, 1)
        not_null_layout.addLayout(grid1)
        btn1 = QPushButton("Установить NOT NULL")
        btn1.clicked.connect(self.set_not_null)
        btn1.setStyleSheet("background-color: #28a745; color: white; padding: 8px;")
        not_null_layout.addWidget(btn1)
        btn2 = QPushButton("Убрать NOT NULL")
        btn2.clicked.connect(self.drop_not_null)
        btn2.setStyleSheet("background-color: #dc3545; color: white; padding: 8px;")
        not_null_layout.addWidget(btn2)
        not_null_layout.addStretch()
        constraint_tabs.addTab(not_null_widget, "NOT NULL")
        self.update_nn_columns()
        
        add_constraint_widget = QWidget()
        add_constraint_layout = QVBoxLayout(add_constraint_widget)
        grid2 = QGridLayout()
        grid2.addWidget(QLabel("Таблица:"), 0, 0)
        self.add_constr_table = QComboBox()
        self.add_constr_table.addItems(self.get_tables())
        grid2.addWidget(self.add_constr_table, 0, 1)
        grid2.addWidget(QLabel("Имя ограничения:"), 1, 0)
        self.add_constr_name = QLineEdit()
        self.add_constr_name.setPlaceholderText("chk_balance_positive")
        grid2.addWidget(self.add_constr_name, 1, 1)
        grid2.addWidget(QLabel("Определение:"), 2, 0)
        self.add_constr_def = QLineEdit()
        self.add_constr_def.setPlaceholderText("CHECK (balance >= 0)")
        grid2.addWidget(self.add_constr_def, 2, 1)
        add_constraint_layout.addLayout(grid2)
        btn3 = QPushButton("Добавить ограничение")
        btn3.clicked.connect(self.add_constraint)
        btn3.setStyleSheet("background-color: #28a745; color: white; padding: 8px;")
        add_constraint_layout.addWidget(btn3)
        add_constraint_layout.addStretch()
        constraint_tabs.addTab(add_constraint_widget, "Добавить ограничение")
        
        drop_constraint_widget = QWidget()
        drop_constraint_layout = QVBoxLayout(drop_constraint_widget)
        grid3 = QGridLayout()
        grid3.addWidget(QLabel("Таблица:"), 0, 0)
        self.drop_constr_table = QComboBox()
        self.drop_constr_table.addItems(self.get_tables())
        grid3.addWidget(self.drop_constr_table, 0, 1)
        grid3.addWidget(QLabel("Имя ограничения:"), 1, 0)
        self.drop_constr_name = QLineEdit()
        self.drop_constr_name.setPlaceholderText("chk_balance_positive")
        grid3.addWidget(self.drop_constr_name, 1, 1)
        drop_constraint_layout.addLayout(grid3)
        btn4 = QPushButton("Удалить ограничение")
        btn4.clicked.connect(self.drop_constraint)
        btn4.setStyleSheet("background-color: #dc3545; color: white; padding: 8px;")
        drop_constraint_layout.addWidget(btn4)
        drop_constraint_layout.addStretch()
        constraint_tabs.addTab(drop_constraint_widget, "Удалить ограничение")
        
        layout.addWidget(constraint_tabs)
        
        self.tabs.addTab(widget, "Ограничения")
    
    def get_tables(self):
        try:
            return self.db_manager.get_tables_list()
        except:
            return []
    
    def get_columns(self, table_name):
        try:
            columns = self.db_manager.get_table_columns(table_name)
            return [col['name'] for col in columns]
        except:
            return []
    
    def update_drop_columns(self):
        table = self.drop_col_table.currentText()
        self.drop_col_name.clear()
        if table:
            self.drop_col_name.addItems(self.get_columns(table))
    
    def update_rename_columns(self):
        table = self.rename_col_table.currentText()
        self.rename_col_old.clear()
        if table:
            self.rename_col_old.addItems(self.get_columns(table))
    
    def update_change_type_columns(self):
        table = self.change_type_table.currentText()
        self.change_type_column.clear()
        if table:
            self.change_type_column.addItems(self.get_columns(table))
    
    def update_nn_columns(self):
        table = self.nn_table.currentText()
        self.nn_column.clear()
        if table:
            self.nn_column.addItems(self.get_columns(table))
    
    def add_column(self):
        try:
            table = self.add_col_table.currentText()
            col_name = self.add_col_name.text().strip()
            col_type = self.add_col_type.currentText().strip()
            constraints = self.add_col_constraints.text().strip()
            
            if not col_name or not col_type:
                QMessageBox.warning(self, "Ошибка", "Заполните все обязательные поля")
                return
            
            self.db_manager.alter_table_add_column(table, col_name, col_type, constraints)
            QMessageBox.information(self, "Успех", f"Столбец '{col_name}' добавлен в таблицу '{table}'")
            self.add_col_name.clear()
            self.add_col_constraints.clear()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить столбец:\n{str(e)}")
    
    def drop_column(self):
        try:
            table = self.drop_col_table.currentText()
            col_name = self.drop_col_name.currentText()
            
            reply = QMessageBox.question(self, "Подтверждение", 
                                        f"Удалить столбец '{col_name}' из таблицы '{table}'?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.db_manager.alter_table_drop_column(table, col_name)
                QMessageBox.information(self, "Успех", f"Столбец '{col_name}' удален")
                self.update_drop_columns()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить столбец:\n{str(e)}")
    
    def rename_column(self):
        try:
            table = self.rename_col_table.currentText()
            old_name = self.rename_col_old.currentText()
            new_name = self.rename_col_new.text().strip()
            
            if not new_name:
                QMessageBox.warning(self, "Ошибка", "Укажите новое имя")
                return
            
            self.db_manager.alter_table_rename_column(table, old_name, new_name)
            QMessageBox.information(self, "Успех", f"Столбец переименован: '{old_name}' → '{new_name}'")
            self.rename_col_new.clear()
            self.update_rename_columns()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось переименовать столбец:\n{str(e)}")
    
    def rename_table(self):
        try:
            old_name = self.rename_table_old.currentText()
            new_name = self.rename_table_new.text().strip()
            
            if not new_name:
                QMessageBox.warning(self, "Ошибка", "Укажите новое имя таблицы")
                return
            
            reply = QMessageBox.question(self, "Подтверждение", 
                                        f"Переименовать таблицу '{old_name}' в '{new_name}'?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.db_manager.alter_table_rename_table(old_name, new_name)
                QMessageBox.information(self, "Успех", f"Таблица переименована: '{old_name}' → '{new_name}'")
                self.rename_table_new.clear()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось переименовать таблицу:\n{str(e)}")
    
    def change_type(self):
        try:
            table = self.change_type_table.currentText()
            column = self.change_type_column.currentText()
            new_type = self.change_type_new.currentText().strip()
            
            if not new_type:
                QMessageBox.warning(self, "Ошибка", "Укажите новый тип данных")
                return
            
            reply = QMessageBox.question(self, "Подтверждение", 
                                        f"Изменить тип столбца '{column}' на '{new_type}'?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.db_manager.alter_table_change_type(table, column, new_type)
                QMessageBox.information(self, "Успех", f"Тип столбца '{column}' изменен на '{new_type}'")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось изменить тип:\n{str(e)}")
    
    def set_not_null(self):
        try:
            table = self.nn_table.currentText()
            column = self.nn_column.currentText()
            
            self.db_manager.alter_table_set_not_null(table, column)
            QMessageBox.information(self, "Успех", f"NOT NULL установлен для столбца '{column}'")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось установить NOT NULL:\n{str(e)}")
    
    def drop_not_null(self):
        try:
            table = self.nn_table.currentText()
            column = self.nn_column.currentText()
            
            self.db_manager.alter_table_drop_not_null(table, column)
            QMessageBox.information(self, "Успех", f"NOT NULL убран для столбца '{column}'")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось убрать NOT NULL:\n{str(e)}")
    
    def add_constraint(self):
        try:
            table = self.add_constr_table.currentText()
            name = self.add_constr_name.text().strip()
            definition = self.add_constr_def.text().strip()
            
            if not name or not definition:
                QMessageBox.warning(self, "Ошибка", "Заполните все поля")
                return
            
            self.db_manager.alter_table_add_constraint(table, name, definition)
            QMessageBox.information(self, "Успех", f"Ограничение '{name}' добавлено")
            self.add_constr_name.clear()
            self.add_constr_def.clear()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить ограничение:\n{str(e)}")
    
    def drop_constraint(self):
        try:
            table = self.drop_constr_table.currentText()
            name = self.drop_constr_name.text().strip()
            
            if not name:
                QMessageBox.warning(self, "Ошибка", "Укажите имя ограничения")
                return
            
            reply = QMessageBox.question(self, "Подтверждение", 
                                        f"Удалить ограничение '{name}' из таблицы '{table}'?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.db_manager.alter_table_drop_constraint(table, name)
                QMessageBox.information(self, "Успех", f"Ограничение '{name}' удалено")
                self.drop_constr_name.clear()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить ограничение:\n{str(e)}")


class AdvancedSelectDialog(QDialog):
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager
        self.logger = logging.getLogger('AdvancedSelectDialog')
        
        self.setWindowTitle("Расширенный SELECT")
        self.setModal(True)
        self.resize(1200, 800)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("Расширенные запросы SELECT")
        title.setStyleSheet("font-weight: bold; font-size: 12pt;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        controls_group = QGroupBox("Параметры запроса")
        controls_layout = QGridLayout()
        
        controls_layout.addWidget(QLabel("Таблица:"), 0, 0)
        self.table_combo = QComboBox()
        self.table_combo.addItems(self.get_tables())
        self.table_combo.currentTextChanged.connect(self.update_columns)
        controls_layout.addWidget(self.table_combo, 0, 1, 1, 3)
        
        controls_layout.addWidget(QLabel("SELECT столбцы:"), 1, 0)
        self.columns_list = QListWidget()
        self.columns_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        controls_layout.addWidget(self.columns_list, 1, 1, 1, 3)
        self.select_all_columns_chk = QCheckBox("Выбрать все")
        self.select_all_columns_chk.stateChanged.connect(self.on_select_all_columns)
        controls_layout.addWidget(self.select_all_columns_chk, 1, 4)
        
        controls_layout.addWidget(QLabel("WHERE условие:"), 2, 0)
        # Filter area: column, operator, value and add button
        self.where_col_combo = QComboBox()
        controls_layout.addWidget(self.where_col_combo, 2, 1)
        self.where_op_combo = QComboBox()
        self.where_op_combo.addItems(['=', '!=', '>', '<', '>=', '<=', 'LIKE', 'ILIKE'])
        controls_layout.addWidget(self.where_op_combo, 2, 2)
        self.where_value_edit = QLineEdit()
        self.where_value_edit.setPlaceholderText("Значение фильтра")
        controls_layout.addWidget(self.where_value_edit, 2, 3)
        add_filter_btn = QPushButton("Добавить фильтр")
        add_filter_btn.clicked.connect(self.add_where_filter)
        controls_layout.addWidget(add_filter_btn, 2, 4)
        # List of filters
        self.where_list = QListWidget()
        controls_layout.addWidget(self.where_list, 3, 1, 1, 4)
        
        controls_layout.addWidget(QLabel("ORDER BY:"), 4, 0)
        self.order_col_combo = QComboBox()
        controls_layout.addWidget(self.order_col_combo, 4, 1)
        self.order_dir_combo = QComboBox()
        self.order_dir_combo.addItems(['ASC', 'DESC'])
        controls_layout.addWidget(self.order_dir_combo, 4, 2)
        clear_order_btn = QPushButton("Очистить сортировку")
        clear_order_btn.clicked.connect(lambda: self.order_col_combo.setCurrentIndex(0))
        controls_layout.addWidget(clear_order_btn, 4, 3)
        
        controls_layout.addWidget(QLabel("GROUP BY:"), 5, 0)
        self.group_list = QListWidget()
        self.group_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        controls_layout.addWidget(self.group_list, 5, 1, 1, 3)
        
        controls_layout.addWidget(QLabel("HAVING:"), 6, 0)
        self.having_func_combo = QComboBox()
        self.having_func_combo.addItems(['', 'COUNT', 'SUM', 'AVG', 'MIN', 'MAX'])
        controls_layout.addWidget(self.having_func_combo, 6, 1)
        self.having_col_combo = QComboBox()
        controls_layout.addWidget(self.having_col_combo, 6, 2)
        self.having_op_combo = QComboBox()
        self.having_op_combo.addItems(['', '>', '<', '>=', '<=', '=', '!='])
        controls_layout.addWidget(self.having_op_combo, 6, 3)
        self.having_value_edit = QLineEdit()
        controls_layout.addWidget(self.having_value_edit, 6, 4)
        
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)
        
        execute_btn = QPushButton("Выполнить запрос")
        execute_btn.clicked.connect(self.execute_query)
        execute_btn.setStyleSheet("background-color: #28a745; color: white; padding: 10px; font-weight: bold;")
        layout.addWidget(execute_btn)
        
        self.result_table = QTableWidget()
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.result_table)
        
        self.sql_label = QLabel()
        self.sql_label.setStyleSheet("font-family: monospace; background-color: #f0f0f0; padding: 5px;")
        self.sql_label.setWordWrap(True)
        layout.addWidget(self.sql_label)
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("background-color: #6c757d; color: white; padding: 8px;")
        layout.addWidget(close_btn)
    
    def get_tables(self):
        try:
            return self.db_manager.get_tables_list()
        except:
            return []

    def on_select_all_columns(self, state):
        if state:
            for i in range(self.columns_list.count()):
                item = self.columns_list.item(i)
                item.setSelected(True)
        else:
            for i in range(self.columns_list.count()):
                item = self.columns_list.item(i)
                item.setSelected(False)

    def update_columns(self):
        table = self.table_combo.currentText()
        # clear
        self.columns_list.clear()
        self.where_col_combo.clear()
        self.order_col_combo.clear()
        self.group_list.clear()
        self.having_col_combo.clear()

        if table:
            try:
                columns = self.db_manager.get_table_columns(table)
                col_names = [col['name'] for col in columns]
                # populate columns list and other combos
                for name in col_names:
                    self.columns_list.addItem(name)
                    self.group_list.addItem(name)
                self.where_col_combo.addItems(col_names)
                self.order_col_combo.addItems([''] + col_names)
                self.having_col_combo.addItems([''] + col_names)
            except Exception:
                pass
    
    def execute_query(self):
        try:
            table = self.table_combo.currentText()
            # columns
            selected_cols = [item.text() for item in self.columns_list.selectedItems()]
            columns = selected_cols if selected_cols else None

            # where filters (AND)
            where_clauses = []
            for i in range(self.where_list.count()):
                where_clauses.append(self.where_list.item(i).text())
            where_clause = ' AND '.join(where_clauses)

            # group by
            group_cols = [item.text() for item in self.group_list.selectedItems()]
            group_by = ', '.join(group_cols) if group_cols else ''

            # having
            having = ''
            func = self.having_func_combo.currentText()
            hcol = self.having_col_combo.currentText()
            hop = self.having_op_combo.currentText()
            hval = self.having_value_edit.text().strip()
            if func and hcol and hop and hval:
                having = f"{func}({hcol}) {hop} {hval}"

            # order by
            order_col = self.order_col_combo.currentText()
            order_dir = self.order_dir_combo.currentText()
            order_by = f"{order_col} {order_dir}" if order_col else ''

            sql = f"SELECT {', '.join(columns) if columns else '*'} FROM bank_system.{table}"
            if where_clause:
                sql += f" WHERE {where_clause}"
            if group_by:
                sql += f" GROUP BY {group_by}"
            if having:
                sql += f" HAVING {having}"
            if order_by:
                sql += f" ORDER BY {order_by}"

            results, column_names = self.db_manager.execute_advanced_select(
                table, columns, where_clause, order_by, group_by, having
            )

            self.sql_label.setText(f"SQL: {sql}")

            self.result_table.setRowCount(len(results))
            self.result_table.setColumnCount(len(column_names))
            self.result_table.setHorizontalHeaderLabels(column_names)

            for row_idx, row_data in enumerate(results):
                for col_idx, value in enumerate(row_data):
                    self.result_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

            QMessageBox.information(self, "Успех", f"Найдено записей: {len(results)}")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось выполнить запрос:\n{str(e)}")
            self.logger.error(f"Query error: {e}")

    def add_where_filter(self):
        col = self.where_col_combo.currentText()
        op = self.where_op_combo.currentText()
        val = self.where_value_edit.text().strip()
        if not col or not op or val == '':
            QMessageBox.warning(self, "Ошибка", "Заполните колонки фильтра")
            return
        # Quote value if it looks like text
        try:
            float(val)
            val_formatted = val
        except:
            val_formatted = f"'{val}'"

        clause = f"{col} {op} {val_formatted}"
        self.where_list.addItem(clause)
        self.where_value_edit.clear()


class TextSearchDialog(QDialog):
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager
        self.logger = logging.getLogger('TextSearchDialog')
        
        self.setWindowTitle("Поиск по тексту")
        self.setModal(True)
        self.resize(1000, 700)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("Поиск по тексту (LIKE и POSIX регулярные выражения)")
        title.setStyleSheet("font-weight: bold; font-size: 12pt;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        controls_group = QGroupBox("Параметры поиска")
        controls_layout = QGridLayout()
        
        controls_layout.addWidget(QLabel("Таблица:"), 0, 0)
        self.table_combo = QComboBox()
        self.table_combo.addItems(self.get_tables())
        self.table_combo.currentTextChanged.connect(self.update_columns)
        controls_layout.addWidget(self.table_combo, 0, 1)
        
        controls_layout.addWidget(QLabel("Столбец:"), 1, 0)
        self.column_combo = QComboBox()
        controls_layout.addWidget(self.column_combo, 1, 1)
        
        controls_layout.addWidget(QLabel("Тип поиска:"), 2, 0)
        self.search_type_combo = QComboBox()
        self.search_type_combo.addItems([
            'LIKE (шаблон)',
            'ILIKE (регистронезависимый)',
            '~ (regex)',
            '~* (regex без учета регистра)',
            '!~ (не соответствует regex)',
            '!~* (не соответствует regex без учета регистра)'
        ])
        controls_layout.addWidget(self.search_type_combo, 2, 1)
        
        controls_layout.addWidget(QLabel("Шаблон/Регулярное выражение:"), 3, 0)
        self.pattern_edit = QLineEdit()
        self.pattern_edit.setPlaceholderText("%текст%, ^[A-Z], .*@gmail\\.com")
        controls_layout.addWidget(self.pattern_edit, 3, 1)
        
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)
        
        info_label = QLabel(
            "LIKE: используйте % (любые символы), _ (один символ)\n"
            "POSIX regex: ^ (начало), $ (конец), . (любой), * (повтор), [A-Z] (класс)"
        )
        info_label.setStyleSheet("background-color: #e7f3ff; padding: 5px; border: 1px solid #b3d9ff;")
        layout.addWidget(info_label)
        
        search_btn = QPushButton("Выполнить поиск")
        search_btn.clicked.connect(self.execute_search)
        search_btn.setStyleSheet("background-color: #28a745; color: white; padding: 10px; font-weight: bold;")
        layout.addWidget(search_btn)
        
        self.result_table = QTableWidget()
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.result_table)
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("background-color: #6c757d; color: white; padding: 8px;")
        layout.addWidget(close_btn)
        
        self.update_columns()
    
    def get_tables(self):
        try:
            return self.db_manager.get_tables_list()
        except:
            return []
    
    def update_columns(self):
        table = self.table_combo.currentText()
        self.column_combo.clear()
        if table:
            try:
                columns = self.db_manager.get_table_columns(table)
                self.column_combo.addItems([col['name'] for col in columns])
            except:
                pass
    
    def execute_search(self):
        try:
            table = self.table_combo.currentText()
            column = self.column_combo.currentText()
            pattern = self.pattern_edit.text()
            search_type_text = self.search_type_combo.currentText()
            
            type_map = {
                'LIKE (шаблон)': 'LIKE',
                'ILIKE (регистронезависимый)': 'ILIKE',
                '~ (regex)': '~',
                '~* (regex без учета регистра)': '~*',
                '!~ (не соответствует regex)': '!~',
                '!~* (не соответствует regex без учета регистра)': '!~*'
            }
            search_type = type_map[search_type_text]
            
            if not pattern:
                QMessageBox.warning(self, "Ошибка", "Введите шаблон для поиска")
                return
            
            results, column_names = self.db_manager.execute_text_search(
                table, column, pattern, search_type
            )
            
            self.result_table.setRowCount(len(results))
            self.result_table.setColumnCount(len(column_names))
            self.result_table.setHorizontalHeaderLabels(column_names)
            
            for row_idx, row_data in enumerate(results):
                for col_idx, value in enumerate(row_data):
                    self.result_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
            
            QMessageBox.information(self, "Успех", f"Найдено записей: {len(results)}")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось выполнить поиск:\n{str(e)}")
            self.logger.error(f"Search error: {e}")


class StringFunctionsDialog(QDialog):
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager
        self.logger = logging.getLogger('StringFunctionsDialog')
        
        self.setWindowTitle("Функции работы со строками")
        self.setModal(True)
        self.resize(1000, 700)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("Функции работы со строками")
        title.setStyleSheet("font-weight: bold; font-size: 12pt;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        controls_group = QGroupBox("Параметры")
        controls_layout = QGridLayout()
        
        controls_layout.addWidget(QLabel("Таблица:"), 0, 0)
        self.table_combo = QComboBox()
        self.table_combo.addItems(self.get_tables())
        self.table_combo.currentTextChanged.connect(self.update_columns)
        controls_layout.addWidget(self.table_combo, 0, 1)
        
        controls_layout.addWidget(QLabel("Столбец:"), 1, 0)
        self.column_combo = QComboBox()
        controls_layout.addWidget(self.column_combo, 1, 1)
        
        controls_layout.addWidget(QLabel("Функция:"), 2, 0)
        self.function_combo = QComboBox()
        self.function_combo.addItems([
            'UPPER (верхний регистр)',
            'LOWER (нижний регистр)',
            'SUBSTRING (подстрока)',
            'TRIM (убрать пробелы)',
            'LTRIM (убрать слева)',
            'RTRIM (убрать справа)',
            'LPAD (дополнить слева)',
            'RPAD (дополнить справа)',
            'CONCAT (объединить)',
            'LENGTH (длина строки)'
        ])
        self.function_combo.currentTextChanged.connect(self.update_param_fields)
        controls_layout.addWidget(self.function_combo, 2, 1)
        
        self.params_widget = QWidget()
        self.params_layout = QGridLayout(self.params_widget)
        controls_layout.addWidget(self.params_widget, 3, 0, 1, 2)
        
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)
        
        execute_btn = QPushButton("Применить функцию")
        execute_btn.clicked.connect(self.execute_function)
        execute_btn.setStyleSheet("background-color: #28a745; color: white; padding: 10px; font-weight: bold;")
        layout.addWidget(execute_btn)
        
        self.result_table = QTableWidget()
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.result_table)
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("background-color: #6c757d; color: white; padding: 8px;")
        layout.addWidget(close_btn)
        
        self.update_columns()
        self.update_param_fields()
    
    def get_tables(self):
        try:
            return self.db_manager.get_tables_list()
        except:
            return []
    
    def update_columns(self):
        table = self.table_combo.currentText()
        self.column_combo.clear()
        if table:
            try:
                columns = self.db_manager.get_table_columns(table)
                self.column_combo.addItems([col['name'] for col in columns])
            except:
                pass
    
    def update_param_fields(self):
        while self.params_layout.count():
            child = self.params_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        func_text = self.function_combo.currentText()
        
        if 'SUBSTRING' in func_text:
            self.params_layout.addWidget(QLabel("Начало (start):"), 0, 0)
            self.start_edit = QLineEdit("1")
            self.params_layout.addWidget(self.start_edit, 0, 1)
            self.params_layout.addWidget(QLabel("Длина (length):"), 1, 0)
            self.length_edit = QLineEdit()
            self.length_edit.setPlaceholderText("Оставьте пустым для всей строки")
            self.params_layout.addWidget(self.length_edit, 1, 1)
        elif 'LPAD' in func_text or 'RPAD' in func_text:
            self.params_layout.addWidget(QLabel("Длина:"), 0, 0)
            self.pad_length_edit = QLineEdit("10")
            self.params_layout.addWidget(self.pad_length_edit, 0, 1)
            self.params_layout.addWidget(QLabel("Символ заполнения:"), 1, 0)
            self.pad_fill_edit = QLineEdit(" ")
            self.params_layout.addWidget(self.pad_fill_edit, 1, 1)
        elif 'CONCAT' in func_text:
            self.params_layout.addWidget(QLabel("Добавить текст:"), 0, 0)
            self.concat_edit = QLineEdit()
            self.concat_edit.setPlaceholderText("Текст для добавления")
            self.params_layout.addWidget(self.concat_edit, 0, 1)
    
    def execute_function(self):
        try:
            table = self.table_combo.currentText()
            column = self.column_combo.currentText()
            func_text = self.function_combo.currentText()
            
            func_map = {
                'UPPER (верхний регистр)': 'UPPER',
                'LOWER (нижний регистр)': 'LOWER',
                'SUBSTRING (подстрока)': 'SUBSTRING',
                'TRIM (убрать пробелы)': 'TRIM',
                'LTRIM (убрать слева)': 'LTRIM',
                'RTRIM (убрать справа)': 'RTRIM',
                'LPAD (дополнить слева)': 'LPAD',
                'RPAD (дополнить справа)': 'RPAD',
                'CONCAT (объединить)': 'CONCAT',
                'LENGTH (длина строки)': 'LENGTH'
            }
            func_type = func_map[func_text]
            
            params = {}
            if func_type == 'SUBSTRING':
                params['start'] = int(self.start_edit.text())
                if self.length_edit.text():
                    params['length'] = int(self.length_edit.text())
            elif func_type in ['LPAD', 'RPAD']:
                params['length'] = int(self.pad_length_edit.text())
                params['fill'] = self.pad_fill_edit.text()
            elif func_type == 'CONCAT':
                params['concat_with'] = self.concat_edit.text()
            
            results, column_names = self.db_manager.execute_string_function(
                table, column, func_type, params
            )
            
            self.result_table.setRowCount(len(results))
            self.result_table.setColumnCount(len(column_names))
            self.result_table.setHorizontalHeaderLabels(column_names)
            
            for row_idx, row_data in enumerate(results):
                for col_idx, value in enumerate(row_data):
                    self.result_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
            
            QMessageBox.information(self, "Успех", f"Обработано записей: {len(results)}")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось выполнить функцию:\n{str(e)}")
            self.logger.error(f"Function error: {e}")


class JoinWizardDialog(QDialog):
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager
        self.logger = logging.getLogger('JoinWizardDialog')
        
        self.setWindowTitle("Мастер соединений (JOIN)")
        self.setModal(True)
        self.resize(1200, 800)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("Мастер соединений таблиц")
        title.setStyleSheet("font-weight: bold; font-size: 12pt;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        controls_group = QGroupBox("Параметры соединения")
        controls_layout = QGridLayout()
        
        controls_layout.addWidget(QLabel("Первая таблица:"), 0, 0)
        self.table1_combo = QComboBox()
        self.table1_combo.addItems(self.get_tables())
        self.table1_combo.currentTextChanged.connect(self.update_columns1)
        controls_layout.addWidget(self.table1_combo, 0, 1)
        
        controls_layout.addWidget(QLabel("Поле связи (таблица 1):"), 1, 0)
        self.column1_combo = QComboBox()
        controls_layout.addWidget(self.column1_combo, 1, 1)
        
        controls_layout.addWidget(QLabel("Вторая таблица:"), 2, 0)
        self.table2_combo = QComboBox()
        self.table2_combo.addItems(self.get_tables())
        self.table2_combo.currentTextChanged.connect(self.update_columns2)
        controls_layout.addWidget(self.table2_combo, 2, 1)
        
        controls_layout.addWidget(QLabel("Поле связи (таблица 2):"), 3, 0)
        self.column2_combo = QComboBox()
        controls_layout.addWidget(self.column2_combo, 3, 1)
        
        controls_layout.addWidget(QLabel("Тип соединения:"), 4, 0)
        self.join_type_combo = QComboBox()
        self.join_type_combo.addItems([
            'INNER (внутреннее)',
            'LEFT (левое)',
            'RIGHT (правое)',
            'FULL (полное)'
        ])
        controls_layout.addWidget(self.join_type_combo, 4, 1)
        
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)
        
        # Выбор столбцов из таблиц
        columns_group = QGroupBox("Столбцы для вывода")
        columns_layout = QHBoxLayout()
        
        self.columns_list = QListWidget()
        self.columns_list.setSelectionMode(QAbstractItemModel.SelectionMode.MultiSelection)
        columns_layout.addWidget(self.columns_list)
        columns_group.setLayout(columns_layout)
        layout.addWidget(columns_group)
        
        info_label = QLabel(
            "INNER: только совпадающие записи | LEFT: все из 1-й + совпадения из 2-й\n"
            "RIGHT: все из 2-й + совпадения из 1-й | FULL: все записи из обеих таблиц"
        )
        info_label.setStyleSheet("background-color: #e7f3ff; padding: 5px; border: 1px solid #b3d9ff;")
        layout.addWidget(info_label)
        
        execute_btn = QPushButton("Выполнить соединение")
        execute_btn.clicked.connect(self.execute_join)
        execute_btn.setStyleSheet("background-color: #28a745; color: white; padding: 10px; font-weight: bold;")
        layout.addWidget(execute_btn)
        
        self.result_table = QTableWidget()
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.result_table)
        
        self.sql_label = QLabel()
        self.sql_label.setStyleSheet("font-family: monospace; background-color: #f0f0f0; padding: 5px;")
        self.sql_label.setWordWrap(True)
        layout.addWidget(self.sql_label)
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("background-color: #6c757d; color: white; padding: 8px;")
        layout.addWidget(close_btn)
        
        self.update_columns1()
        self.update_columns2()
    
    def get_tables(self):
        try:
            return self.db_manager.get_tables_list()
        except:
            return []
    
    def update_columns1(self):
        table = self.table1_combo.currentText()
        self.column1_combo.clear()
        if table:
            try:
                columns = self.db_manager.get_table_columns(table)
                self.column1_combo.addItems([col['name'] for col in columns])
            except:
                pass
        self.update_join_columns()
    
    def update_columns2(self):
        table = self.table2_combo.currentText()
        self.column2_combo.clear()
        if table:
            try:
                columns = self.db_manager.get_table_columns(table)
                self.column2_combo.addItems([col['name'] for col in columns])
            except:
                pass
        self.update_join_columns()
    
    def update_join_columns(self):
        """Обновить список доступных столбцов из обеих таблиц"""
        self.columns_list.clear()
        table1 = self.table1_combo.currentText()
        table2 = self.table2_combo.currentText()
        
        if not table1 or not table2:
            return
        
        try:
            cols1 = self.db_manager.get_table_columns(table1)
            cols2 = self.db_manager.get_table_columns(table2)
            
            for col in cols1:
                self.columns_list.addItem(f"t1.{col['name']}")
            for col in cols2:
                self.columns_list.addItem(f"t2.{col['name']}")
        except:
            pass
    
    def execute_join(self):
        try:
            table1 = self.table1_combo.currentText()
            table2 = self.table2_combo.currentText()
            column1 = self.column1_combo.currentText()
            column2 = self.column2_combo.currentText()
            join_type_text = self.join_type_combo.currentText()
            
            # Получить выбранные столбцы из списка
            selected_items = self.columns_list.selectedItems()
            if selected_items:
                columns_str = ', '.join([item.text() for item in selected_items])
            else:
                columns_str = '*'
            
            join_map = {
                'INNER (внутреннее)': 'INNER',
                'LEFT (левое)': 'LEFT',
                'RIGHT (правое)': 'RIGHT',
                'FULL (полное)': 'FULL'
            }
            join_type = join_map[join_type_text]
            
            sql = f"SELECT {columns_str} FROM bank_system.{table1} t1 {join_type} JOIN bank_system.{table2} t2 ON t1.{column1} = t2.{column2}"
            self.sql_label.setText(f"SQL: {sql}")
            
            # Для db_manager, если нужны конкретные столбцы, преобразуем в список
            columns = None
            if columns_str != '*':
                columns = [c.strip() for c in columns_str.split(',')]
            
            results, column_names = self.db_manager.execute_join(
                table1, table2, column1, column2, join_type, columns
            )
            
            self.result_table.setRowCount(len(results))
            self.result_table.setColumnCount(len(column_names))
            self.result_table.setHorizontalHeaderLabels(column_names)
            
            for row_idx, row_data in enumerate(results):
                for col_idx, value in enumerate(row_data):
                    self.result_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
            
            QMessageBox.information(self, "Успех", f"Найдено записей: {len(results)}")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось выполнить соединение:\n{str(e)}")
            self.logger.error(f"Join error: {e}")


class SubqueryFilterDialog(QDialog):
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager
        self.logger = logging.getLogger('SubqueryFilterDialog')
        
        self.setWindowTitle("Фильтры подзапросами")
        self.setModal(True)
        self.resize(1200, 700)
        
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
        """)
        
        title = QLabel("Применить фильтры на основе подзапросов")
        title.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(title)
        
        filter_layout = QGridLayout()
        
        filter_layout.addWidget(QLabel("Основная таблица:"), 0, 0)
        self.main_table = QComboBox()
        self.main_table.addItems(['currencies', 'exchange_rates', 'clients', 'accounts', 'transactions'])
        self.main_table.currentTextChanged.connect(self.on_main_table_changed)
        filter_layout.addWidget(self.main_table, 0, 1)
        
        filter_layout.addWidget(QLabel("Колонка:"), 0, 2)
        self.main_column = QComboBox()
        filter_layout.addWidget(self.main_column, 0, 3)
        
        filter_layout.addWidget(QLabel("Оператор:"), 1, 0)
        self.operator = QComboBox()
        self.operator.addItems(['IN', 'ANY', 'ALL', 'EXISTS'])
        filter_layout.addWidget(self.operator, 1, 1)
        
        filter_layout.addWidget(QLabel("Таблица подзапроса:"), 1, 2)
        self.sub_table = QComboBox()
        self.sub_table.addItems(['currencies', 'exchange_rates', 'clients', 'accounts', 'transactions'])
        self.sub_table.currentTextChanged.connect(self.on_sub_table_changed)
        filter_layout.addWidget(self.sub_table, 1, 3)
        
        filter_layout.addWidget(QLabel("Колонка подзапроса:"), 2, 0)
        self.sub_column = QComboBox()
        filter_layout.addWidget(self.sub_column, 2, 1)
        
        apply_btn = QPushButton("Применить фильтр")
        apply_btn.clicked.connect(self.apply_filter)
        filter_layout.addWidget(apply_btn, 2, 3)
        
        layout.addLayout(filter_layout)
        
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(0)
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.result_table.verticalHeader().setDefaultSectionSize(30)
        layout.addWidget(self.result_table)
        
        self.sql_label = QLabel("SQL:")
        self.sql_label.setStyleSheet("color: #666; font-size: 9pt;")
        layout.addWidget(self.sql_label)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("background-color: #6c757d;")
        buttons_layout.addWidget(close_btn)
        layout.addLayout(buttons_layout)
        
        self.on_main_table_changed()
        self.on_sub_table_changed()
    
    def on_main_table_changed(self):
        table = self.main_table.currentText()
        self.main_column.clear()
        try:
            columns = self.db_manager.get_table_columns(table)
            self.main_column.addItems([col['name'] for col in columns])
        except Exception as e:
            self.logger.error(f"Error loading columns: {e}")
    
    def on_sub_table_changed(self):
        table = self.sub_table.currentText()
        self.sub_column.clear()
        try:
            columns = self.db_manager.get_table_columns(table)
            self.sub_column.addItems([col['name'] for col in columns])
        except Exception as e:
            self.logger.error(f"Error loading columns: {e}")
    
    def apply_filter(self):
        try:
            main_table = self.main_table.currentText()
            main_col = self.main_column.currentText()
            operator = self.operator.currentText()
            sub_table = self.sub_table.currentText()
            sub_col = self.sub_column.currentText()
            
            results, column_names = self.db_manager.execute_subquery_filter(
                main_table, sub_table, operator, main_col, sub_col
            )
            
            sql = f"SELECT * FROM bank_system.{main_table} WHERE {main_col} {operator} (SELECT {sub_col} FROM bank_system.{sub_table})"
            self.sql_label.setText(f"SQL: {sql}")
            
            self.result_table.setRowCount(len(results))
            self.result_table.setColumnCount(len(column_names))
            self.result_table.setHorizontalHeaderLabels(column_names)
            
            for row_idx, row_data in enumerate(results):
                for col_idx, value in enumerate(row_data):
                    self.result_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
            
            QMessageBox.information(self, "Успех", f"Найдено записей: {len(results)}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка фильтра:\n{str(e)}")
            self.logger.error(f"Subquery filter error: {e}")


class CustomTypesDialog(QDialog):
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager
        self.logger = logging.getLogger('CustomTypesDialog')
        
        from custom_types_manager import CustomTypesManager
        self.types_manager = CustomTypesManager(db_manager)
        
        self.setWindowTitle("Пользовательские типы данных")
        self.setModal(True)
        self.resize(1000, 600)
        
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
        """)
        
        title = QLabel("Управление пользовательскими типами")
        title.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(title)
        
        tabs = QTabWidget()
        
        view_tab = QWidget()
        view_layout = QVBoxLayout(view_tab)
        
        btn_layout = QHBoxLayout()
        load_btn = QPushButton("Загрузить типы")
        load_btn.clicked.connect(self.load_types)
        btn_layout.addWidget(load_btn)
        btn_layout.addStretch()
        view_layout.addLayout(btn_layout)
        
        self.types_table = QTableWidget()
        self.types_table.setColumnCount(3)
        self.types_table.setHorizontalHeaderLabels(['Имя', 'Тип', 'Поля'])
        self.types_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.types_table.verticalHeader().setDefaultSectionSize(30)
        view_layout.addWidget(self.types_table)
        
        tabs.addTab(view_tab, "Просмотр типов")
        
        create_tab = QWidget()
        create_layout = QVBoxLayout(create_tab)
        
        form_layout = QGridLayout()
        form_layout.addWidget(QLabel("Имя типа:"), 0, 0)
        self.type_name_edit = QLineEdit()
        form_layout.addWidget(self.type_name_edit, 0, 1)
        
        form_layout.addWidget(QLabel("Поля (имя:тип):"), 1, 0, Qt.AlignmentFlag.AlignTop)
        self.fields_edit = QTextEdit()
        self.fields_edit.setPlaceholderText("Введите поля в формате:\nимя1:тип1\nимя2:тип2")
        self.fields_edit.setMaximumHeight(150)
        form_layout.addWidget(self.fields_edit, 1, 1)
        
        create_btn = QPushButton("Создать тип")
        create_btn.clicked.connect(self.create_type)
        form_layout.addWidget(create_btn, 2, 1)
        
        create_layout.addLayout(form_layout)
        create_layout.addStretch()
        
        tabs.addTab(create_tab, "Создание типа")
        
        delete_tab = QWidget()
        delete_layout = QVBoxLayout(delete_tab)
        
        delete_layout.addWidget(QLabel("Выберите тип для удаления:"))
        self.delete_type_combo = QComboBox()
        delete_layout.addWidget(self.delete_type_combo)
        
        delete_btn = QPushButton("Удалить тип")
        delete_btn.clicked.connect(self.delete_type)
        delete_btn.setStyleSheet("background-color: #dc3545;")
        delete_layout.addWidget(delete_btn)
        delete_layout.addStretch()
        
        tabs.addTab(delete_tab, "Удаление типа")
        
        layout.addWidget(tabs)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("background-color: #6c757d;")
        buttons_layout.addWidget(close_btn)
        layout.addLayout(buttons_layout)
        
        self.load_types()
    
    def load_types(self):
        try:
            types = self.types_manager.get_all_types()
            
            self.types_table.setRowCount(len(types))
            for row_idx, t in enumerate(types):
                self.types_table.setItem(row_idx, 0, QTableWidgetItem(t['name']))
                self.types_table.setItem(row_idx, 1, QTableWidgetItem(t['type']))
                self.types_table.setItem(row_idx, 2, QTableWidgetItem(t['fields'] or ''))
            
            self.delete_type_combo.clear()
            self.delete_type_combo.addItems([t['name'] for t in types])
            
            QMessageBox.information(self, "Успех", f"Загружено типов: {len(types)}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить типы:\n{str(e)}")
            self.logger.error(f"Load types error: {e}")
    
    def create_type(self):
        try:
            type_name = self.type_name_edit.text().strip()
            fields_text = self.fields_edit.toPlainText().strip()
            
            if not type_name:
                QMessageBox.warning(self, "Предупреждение", "Введите имя типа")
                return
            
            if not fields_text:
                QMessageBox.warning(self, "Предупреждение", "Введите поля типа")
                return
            
            fields = []
            for line in fields_text.split('\n'):
                if ':' in line:
                    name, ftype = line.split(':')
                    fields.append({
                        'name': name.strip(),
                        'type': ftype.strip()
                    })
            
            if not fields:
                QMessageBox.warning(self, "Предупреждение", "Неверный формат полей")
                return
            
            self.types_manager.create_composite_type(type_name, fields)
            QMessageBox.information(self, "Успех", f"Тип {type_name} создан")
            self.type_name_edit.clear()
            self.fields_edit.clear()
            self.load_types()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать тип:\n{str(e)}")
            self.logger.error(f"Create type error: {e}")
    
    def delete_type(self):
        try:
            type_name = self.delete_type_combo.currentText()
            
            if not type_name:
                QMessageBox.warning(self, "Предупреждение", "Выберите тип")
                return
            
            reply = QMessageBox.question(
                self,
                "Подтверждение",
                f"Удалить тип {type_name}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.types_manager.drop_type(type_name)
                QMessageBox.information(self, "Успех", f"Тип {type_name} удален")
                self.load_types()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить тип:\n{str(e)}")
            self.logger.error(f"Delete type error: {e}")


class SimilarToDialog(QDialog):
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager
        self.logger = logging.getLogger('SimilarToDialog')
        
        self.setWindowTitle("Поиск SIMILAR TO")
        self.setModal(True)
        self.resize(1200, 700)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.setStyleSheet("""
            QPushButton {
                background-color: #FF8C00;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #E67E00;
            }
        """)
        
        title = QLabel("Поиск по шаблону SIMILAR TO")
        title.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(title)
        
        filter_layout = QGridLayout()
        
        filter_layout.addWidget(QLabel("Таблица:"), 0, 0)
        self.table_combo = QComboBox()
        self.table_combo.addItems(['currencies', 'exchange_rates', 'clients', 'accounts', 'transactions'])
        self.table_combo.currentTextChanged.connect(self.on_table_changed)
        filter_layout.addWidget(self.table_combo, 0, 1)
        
        filter_layout.addWidget(QLabel("Колонка:"), 0, 2)
        self.column_combo = QComboBox()
        filter_layout.addWidget(self.column_combo, 0, 3)
        
        filter_layout.addWidget(QLabel("Шаблон:"), 1, 0)
        self.pattern_edit = QLineEdit()
        self.pattern_edit.setPlaceholderText("Например: %ab% или _def%")
        filter_layout.addWidget(self.pattern_edit, 1, 1, 1, 2)
        
        filter_layout.addWidget(QLabel("Оператор:"), 1, 3)
        self.operator_combo = QComboBox()
        self.operator_combo.addItems(['SIMILAR TO', 'NOT SIMILAR TO'])
        filter_layout.addWidget(self.operator_combo, 1, 4)
        
        apply_btn = QPushButton("Поиск")
        apply_btn.clicked.connect(self.apply_search)
        filter_layout.addWidget(apply_btn, 2, 4)
        
        layout.addLayout(filter_layout)
        
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(0)
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.result_table.verticalHeader().setDefaultSectionSize(30)
        layout.addWidget(self.result_table)
        
        self.sql_label = QLabel("SQL:")
        self.sql_label.setStyleSheet("color: #666; font-size: 9pt;")
        layout.addWidget(self.sql_label)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("background-color: #6c757d;")
        buttons_layout.addWidget(close_btn)
        layout.addLayout(buttons_layout)
        
        self.on_table_changed()
        
        # Установка данных по умолчанию
        self.table_combo.setCurrentText('clients')
        self.on_table_changed()
        self.column_combo.setCurrentText('full_name')
        self.pattern_edit.setText('%ов%')
    
    def on_table_changed(self):
        table = self.table_combo.currentText()
        self.column_combo.clear()
        try:
            columns = self.db_manager.get_table_columns(table)
            self.column_combo.addItems([col['name'] for col in columns])
        except Exception as e:
            self.logger.error(f"Error loading columns: {e}")
    
    def apply_search(self):
        try:
            table = self.table_combo.currentText()
            column = self.column_combo.currentText()
            pattern = self.pattern_edit.text().strip()
            operator = self.operator_combo.currentText()
            
            if not pattern:
                QMessageBox.warning(self, "Предупреждение", "Введите шаблон поиска")
                return
            
            results, column_names = self.db_manager.execute_text_search(
                table, column, pattern, operator
            )
            
            sql = f"SELECT * FROM bank_system.{table} WHERE {column} {operator} '{pattern}'"
            self.sql_label.setText(f"SQL: {sql}")
            
            self.result_table.setRowCount(len(results))
            self.result_table.setColumnCount(len(column_names))
            self.result_table.setHorizontalHeaderLabels(column_names)
            
            for row_idx, row_data in enumerate(results):
                for col_idx, value in enumerate(row_data):
                    self.result_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
            
            QMessageBox.information(self, "Успех", f"Найдено записей: {len(results)}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка поиска:\n{str(e)}")
            self.logger.error(f"SIMILAR TO search error: {e}")


class AggregationDialog(QDialog):
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager
        self.logger = logging.getLogger('AggregationDialog')
        
        self.setWindowTitle("Агрегирование и группировка")
        self.setModal(True)
        self.resize(1200, 700)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.setStyleSheet("""
            QPushButton {
                background-color: #FF8C00;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #E67E00;
            }
        """)
        
        title = QLabel("Агрегирование и группировка данных")
        title.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(title)
        
        filter_layout = QGridLayout()
        
        filter_layout.addWidget(QLabel("Таблица:"), 0, 0)
        self.table_combo = QComboBox()
        self.table_combo.addItems(['currencies', 'exchange_rates', 'clients', 'accounts', 'transactions'])
        self.table_combo.currentTextChanged.connect(self.on_table_changed)
        filter_layout.addWidget(self.table_combo, 0, 1)
        
        filter_layout.addWidget(QLabel("Агрегатная функция:"), 0, 2)
        self.agg_func_combo = QComboBox()
        self.agg_func_combo.addItems(['COUNT', 'SUM', 'AVG', 'MIN', 'MAX'])
        filter_layout.addWidget(self.agg_func_combo, 0, 3)
        
        filter_layout.addWidget(QLabel("Колонка для агрегации:"), 1, 0)
        self.agg_column_combo = QComboBox()
        filter_layout.addWidget(self.agg_column_combo, 1, 1)
        
        filter_layout.addWidget(QLabel("GROUP BY колонка:"), 1, 2)
        self.group_combo = QComboBox()
        self.group_combo.addItem("(нет)")
        filter_layout.addWidget(self.group_combo, 1, 3)
        
        filter_layout.addWidget(QLabel("HAVING условие:"), 2, 0)
        self.having_func_combo = QComboBox()
        self.having_func_combo.addItems(['', 'COUNT', 'SUM', 'AVG', 'MIN', 'MAX'])
        filter_layout.addWidget(self.having_func_combo, 2, 1)
        self.having_col_combo = QComboBox()
        filter_layout.addWidget(self.having_col_combo, 2, 2)
        self.having_op_combo = QComboBox()
        self.having_op_combo.addItems(['', '>', '<', '>=', '<=', '=', '!='])
        filter_layout.addWidget(self.having_op_combo, 2, 3)
        self.having_value_edit = QLineEdit()
        self.having_value_edit.setPlaceholderText("Значение")
        filter_layout.addWidget(self.having_value_edit, 2, 4)
        
        apply_btn = QPushButton("Выполнить")
        apply_btn.clicked.connect(self.apply_aggregation)
        filter_layout.addWidget(apply_btn, 3, 3)
        
        layout.addLayout(filter_layout)
        
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(0)
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.result_table.verticalHeader().setDefaultSectionSize(30)
        layout.addWidget(self.result_table)
        
        self.sql_label = QLabel("SQL:")
        self.sql_label.setStyleSheet("color: #666; font-size: 9pt;")
        layout.addWidget(self.sql_label)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("background-color: #6c757d;")
        buttons_layout.addWidget(close_btn)
        layout.addLayout(buttons_layout)
        
        self.on_table_changed()
    
    def on_table_changed(self):
        table = self.table_combo.currentText()
        self.agg_column_combo.clear()
        self.group_combo.clear()
        self.group_combo.addItem("(нет)")
        try:
            columns = self.db_manager.get_table_columns(table)
            col_names = [col['name'] for col in columns]
            self.agg_column_combo.addItems(col_names)
            self.group_combo.addItems(col_names)
            # populate having column combo as well
            self.having_col_combo.clear()
            self.having_col_combo.addItems([''] + col_names)
        except Exception as e:
            self.logger.error(f"Error loading columns: {e}")
    
    def apply_aggregation(self):
        try:
            table = self.table_combo.currentText()
            agg_func = self.agg_func_combo.currentText()
            agg_column = self.agg_column_combo.currentText()
            group_by = self.group_combo.currentText()
            func = self.having_func_combo.currentText()
            hcol = self.having_col_combo.currentText()
            hop = self.having_op_combo.currentText()
            hval = self.having_value_edit.text().strip()

            if group_by == "(нет)":
                group_by = None

            having = None
            if func and hcol and hop and hval:
                # quote non-numeric value
                try:
                    float(hval)
                    val_formatted = hval
                except:
                    val_formatted = f"'{hval}'"
                having = f"{func}({hcol}) {hop} {val_formatted}"
            
            results, column_names = self.db_manager.execute_aggregation(
                table, agg_func, agg_column, group_by, having
            )
            
            sql = f"SELECT {agg_func}({agg_column})"
            if group_by:
                sql += f", {group_by}"
            sql += f" FROM bank_system.{table}"
            if group_by:
                sql += f" GROUP BY {group_by}"
            if having:
                sql += f" HAVING {having}"
            
            self.sql_label.setText(f"SQL: {sql}")
            
            self.result_table.setRowCount(len(results))
            self.result_table.setColumnCount(len(column_names))
            self.result_table.setHorizontalHeaderLabels(column_names)
            
            for row_idx, row_data in enumerate(results):
                for col_idx, value in enumerate(row_data):
                    self.result_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
            
            QMessageBox.information(self, "Успех", f"Найдено записей: {len(results)}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка агрегирования:\n{str(e)}")
            self.logger.error(f"Aggregation error: {e}")


class CaseConstructorDialog(QDialog):
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager
        self.logger = logging.getLogger('CaseConstructorDialog')
        self.when_then_pairs = []
        
        self.setWindowTitle("Конструктор CASE выражений")
        self.setModal(True)
        self.resize(1200, 700)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.setStyleSheet("""
            QPushButton {
                background-color: #FF8C00;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #E67E00;
            }
        """)
        
        title = QLabel("Конструктор CASE выражений")
        title.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(title)
        
        filter_layout = QGridLayout()
        
        filter_layout.addWidget(QLabel("Таблица:"), 0, 0)
        self.table_combo = QComboBox()
        self.table_combo.addItems(['currencies', 'exchange_rates', 'clients', 'accounts', 'transactions'])
        self.table_combo.currentTextChanged.connect(self.on_table_changed)
        filter_layout.addWidget(self.table_combo, 0, 1)
        
        filter_layout.addWidget(QLabel("Выбрать столбцы:"), 0, 2)
        self.select_edit = QLineEdit()
        self.select_edit.setText("*")
        self.select_edit.setPlaceholderText("*, col1, col2")
        filter_layout.addWidget(self.select_edit, 0, 3)
        
        filter_layout.addWidget(QLabel("WHEN - столбец:"), 1, 0)
        self.when_col_combo = QComboBox()
        filter_layout.addWidget(self.when_col_combo, 1, 1)

        filter_layout.addWidget(QLabel("Оператор:"), 1, 2)
        self.when_op_combo = QComboBox()
        self.when_op_combo.addItems(['=', '!=', '>', '<', '>=', '<=', 'LIKE', 'ILIKE'])
        filter_layout.addWidget(self.when_op_combo, 1, 3)

        filter_layout.addWidget(QLabel("Значение:"), 2, 0)
        self.when_value_edit = QLineEdit()
        filter_layout.addWidget(self.when_value_edit, 2, 1)

        filter_layout.addWidget(QLabel("THEN результат:"), 2, 2)
        self.then_edit = QLineEdit()
        self.then_edit.setPlaceholderText("'Результат' или 123")
        filter_layout.addWidget(self.then_edit, 2, 3)
        
        add_btn = QPushButton("Добавить WHEN/THEN")
        add_btn.clicked.connect(self.add_when_then)
        filter_layout.addWidget(add_btn, 3, 0)
        
        filter_layout.addWidget(QLabel("ELSE результат:"), 4, 0)
        self.else_edit = QLineEdit()
        self.else_edit.setText("'Низкий'")
        self.else_edit.setPlaceholderText("'Низкий баланс'")
        filter_layout.addWidget(self.else_edit, 4, 1)

        # List of added WHEN/THENs
        self.when_list = QListWidget()
        filter_layout.addWidget(self.when_list, 5, 0, 1, 4)
        
        layout.addLayout(filter_layout)
        
        self.conditions_label = QLabel("Добавленные условия: нет")
        self.conditions_label.setStyleSheet("background-color: #f0f0f0; padding: 5px;")
        layout.addWidget(self.conditions_label)
        
        execute_btn = QPushButton("Выполнить CASE выражение")
        execute_btn.clicked.connect(self.execute_case)
        layout.addWidget(execute_btn)
        
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(0)
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.result_table.verticalHeader().setDefaultSectionSize(30)
        layout.addWidget(self.result_table)
        
        self.sql_label = QLabel("SQL:")
        self.sql_label.setStyleSheet("color: #666; font-size: 9pt;")
        layout.addWidget(self.sql_label)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("background-color: #6c757d;")
        buttons_layout.addWidget(close_btn)
        layout.addLayout(buttons_layout)
        
        # Установка таблицы по умолчанию
        self.table_combo.setCurrentText('transactions')
    
    def on_table_changed(self):
        table = self.table_combo.currentText()
        try:
            cols = self.db_manager.get_table_columns(table)
            col_names = [c['name'] for c in cols]
            self.when_col_combo.clear()
            self.when_col_combo.addItems(col_names)
        except Exception as e:
            self.logger.error(f"Error loading columns for CASE: {e}")
    
    def add_when_then(self):
        col = self.when_col_combo.currentText()
        op = self.when_op_combo.currentText()
        val = self.when_value_edit.text().strip()
        then = self.then_edit.text().strip()

        if not col or not op or val == '' or not then:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля WHEN и THEN")
            return

        # format value
        try:
            float(val)
            val_fmt = val
        except:
            val_fmt = f"'{val}'"

        when_expr = f"{col} {op} {val_fmt}"
        self.when_then_pairs.append((when_expr, then))
        self.when_list.addItem(f"WHEN {when_expr} THEN {then}")
        self.update_conditions_label()
        self.when_value_edit.clear()
        self.then_edit.clear()
    
    def update_conditions_label(self):
        if not self.when_then_pairs:
            self.conditions_label.setText("Добавленные условия: нет")
        else:
            text = "Добавленные условия:\n"
            for i, (when, then) in enumerate(self.when_then_pairs, 1):
                text += f"{i}. WHEN {when} THEN {then}\n"
            self.conditions_label.setText(text)
    
    def execute_case(self):
        try:
            if not self.when_then_pairs:
                QMessageBox.warning(self, "Ошибка", "Добавьте хотя бы одно условие WHEN/THEN")
                return
            
            table = self.table_combo.currentText()
            select_cols = self.select_edit.text().strip()
            else_result = self.else_edit.text().strip()
            
            case_expr = "CASE"
            for when, then in self.when_then_pairs:
                case_expr += f" WHEN {when} THEN {then}"
            case_expr += f" ELSE {else_result} END"
            
            results, column_names = self.db_manager.execute_case_expression(
                table, case_expr, select_cols
            )
            
            sql = f"SELECT {select_cols}, {case_expr} as case_result FROM bank_system.{table}"
            self.sql_label.setText(f"SQL: {sql}")
            
            self.result_table.setRowCount(len(results))
            self.result_table.setColumnCount(len(column_names))
            self.result_table.setHorizontalHeaderLabels(column_names)
            
            for row_idx, row_data in enumerate(results):
                for col_idx, value in enumerate(row_data):
                    self.result_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
            
            QMessageBox.information(self, "Успех", f"Найдено записей: {len(results)}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка выполнения CASE:\n{str(e)}")
            self.logger.error(f"CASE error: {e}")


class NullFunctionsDialog(QDialog):
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager
        self.logger = logging.getLogger('NullFunctionsDialog')
        
        self.setWindowTitle("COALESCE и NULLIF функции")
        self.setModal(True)
        self.resize(1200, 700)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.setStyleSheet("""
            QPushButton {
                background-color: #FF8C00;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #E67E00;
            }
        """)
        
        title = QLabel("COALESCE и NULLIF - работа с NULL значениями")
        title.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(title)
        
        filter_layout = QGridLayout()
        
        filter_layout.addWidget(QLabel("Таблица:"), 0, 0)
        self.table_combo = QComboBox()
        self.table_combo.addItems(['currencies', 'exchange_rates', 'clients', 'accounts', 'transactions'])
        self.table_combo.currentTextChanged.connect(self.on_table_changed)
        filter_layout.addWidget(self.table_combo, 0, 1)
        
        filter_layout.addWidget(QLabel("Функция:"), 0, 2)
        self.func_combo = QComboBox()
        self.func_combo.addItems(['COALESCE', 'NULLIF'])
        self.func_combo.currentTextChanged.connect(self.update_params)
        filter_layout.addWidget(self.func_combo, 0, 3)
        
        filter_layout.addWidget(QLabel("Колонка:"), 1, 0)
        self.column_combo = QComboBox()
        filter_layout.addWidget(self.column_combo, 1, 1)
        
        self.param_label = QLabel("Альтернативное значение:")
        filter_layout.addWidget(self.param_label, 1, 2)
        self.param_edit = QLineEdit()
        self.param_edit.setText("0")
        self.param_edit.setPlaceholderText("'default' или 0")
        filter_layout.addWidget(self.param_edit, 1, 3)
        
        filter_layout.addWidget(QLabel("SELECT столбцы:"), 2, 0)
        self.select_columns_list = QListWidget()
        self.select_columns_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        filter_layout.addWidget(self.select_columns_list, 2, 1, 1, 3)
        
        execute_btn = QPushButton("Выполнить")
        execute_btn.clicked.connect(self.execute_function)
        filter_layout.addWidget(execute_btn, 3, 3)
        
        layout.addLayout(filter_layout)
        
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(0)
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.result_table.verticalHeader().setDefaultSectionSize(30)
        layout.addWidget(self.result_table)
        
        self.sql_label = QLabel("SQL:")
        self.sql_label.setStyleSheet("color: #666; font-size: 9pt;")
        layout.addWidget(self.sql_label)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("background-color: #6c757d;")
        buttons_layout.addWidget(close_btn)
        layout.addLayout(buttons_layout)
        
        self.on_table_changed()
        self.table_combo.setCurrentText('transactions')
    
    def on_table_changed(self):
        table = self.table_combo.currentText()
        self.column_combo.clear()
        try:
            columns = self.db_manager.get_table_columns(table)
            self.column_combo.addItems([col['name'] for col in columns])
            # populate select columns list for NULL functions dialog
            self.select_columns_list.clear()
            for col in columns:
                self.select_columns_list.addItem(col['name'])
        except Exception as e:
            self.logger.error(f"Error loading columns: {e}")
    
    def update_params(self):
        func = self.func_combo.currentText()
        if func == "COALESCE":
            self.param_label.setText("Альтернативное значение:")
            self.param_edit.setPlaceholderText("'default' или 0")
        else:
            self.param_label.setText("Значение для замены на NULL:")
            self.param_edit.setPlaceholderText("Значение для NULLIF")
    
    def execute_function(self):
        try:
            table = self.table_combo.currentText()
            func_type = self.func_combo.currentText()
            column = self.column_combo.currentText()
            param = self.param_edit.text().strip()
            select_cols_items = [it.text() for it in self.select_columns_list.selectedItems()]
            select_cols = ', '.join(select_cols_items) if select_cols_items else '*'
            
            if func_type == "COALESCE":
                results, column_names = self.db_manager.execute_coalesce_nullif(
                    table, func_type, column, coalesce_values=[column, param], select_cols=select_cols
                )
                expr = f"COALESCE({column}, {param})"
            else:
                results, column_names = self.db_manager.execute_coalesce_nullif(
                    table, func_type, column, nullif_val1=param, select_cols=select_cols
                )
                expr = f"NULLIF({column}, {param})"
            
            sql = f"SELECT {select_cols}, {expr} as result FROM bank_system.{table}"
            self.sql_label.setText(f"SQL: {sql}")
            
            self.result_table.setRowCount(len(results))
            self.result_table.setColumnCount(len(column_names))
            self.result_table.setHorizontalHeaderLabels(column_names)
            
            for row_idx, row_data in enumerate(results):
                for col_idx, value in enumerate(row_data):
                    self.result_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
            
            QMessageBox.information(self, "Успех", f"Найдено записей: {len(results)}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка выполнения:\n{str(e)}")
            self.logger.error(f"NULL function error: {e}")
            self.logger.error(f"Aggregation error: {e}")


class AdvancedGroupingDialog(QDialog):
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager
        self.logger = logging.getLogger('AdvancedGroupingDialog')
        
        self.setWindowTitle("Расширенная группировка данных")
        self.setModal(True)
        self.resize(1400, 800)
        
        # Словарь таблиц и их колонок для группировки
        self.table_columns = {
            'currencies': ['currency_id', 'currency_code', 'is_active'],
            'exchange_rates': ['base_currency', 'target_currency', 'rate_date'],
            'clients': ['client_id', 'is_vip'],
            'accounts': ['client_id', 'currency_code', 'account_status'],
            'transactions': ['account_id', 'transaction_type', 'currency_code']
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.setStyleSheet("""
            QPushButton {
                background-color: #0066cc;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
        """)
        
        title = QLabel("Расширенная группировка (ROLLUP, CUBE, GROUPING SETS)")
        title.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(title)
        
        # Верхняя часть с выбором таблицы и типа группировки
        top_layout = QGridLayout()
        
        top_layout.addWidget(QLabel("Таблица:"), 0, 0)
        self.table_combo = QComboBox()
        self.table_combo.addItems(list(self.table_columns.keys()))
        self.table_combo.currentTextChanged.connect(self.on_table_changed)
        top_layout.addWidget(self.table_combo, 0, 1)
        
        top_layout.addWidget(QLabel("SELECT:"), 0, 2)
        # selectable columns for SELECT
        self.select_columns_box = QListWidget()
        self.select_columns_box.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        top_layout.addWidget(self.select_columns_box, 0, 3)
        
        top_layout.addWidget(QLabel("Тип группировки:"), 1, 0)
        self.group_type_combo = QComboBox()
        self.group_type_combo.addItems(['ROLLUP', 'CUBE', 'GROUPING_SETS'])
        top_layout.addWidget(self.group_type_combo, 1, 1)
        
        top_layout.addWidget(QLabel("WHERE условие (опционально):"), 1, 2)
        self.ag_where_col = QComboBox()
        top_layout.addWidget(self.ag_where_col, 1, 3)
        self.ag_where_op = QComboBox()
        self.ag_where_op.addItems(['=', '!=', '>', '<', '>=', '<=', 'LIKE', 'ILIKE', 'IN'])
        top_layout.addWidget(self.ag_where_op, 1, 4)
        self.ag_where_val = QLineEdit()
        self.ag_where_val.setPlaceholderText("Значение")
        top_layout.addWidget(self.ag_where_val, 1, 5)
        ag_add_filter_btn = QPushButton("Добавить фильтр")
        ag_add_filter_btn.clicked.connect(self.add_advanced_group_filter)
        top_layout.addWidget(ag_add_filter_btn, 1, 6)
        self.ag_where_list = QListWidget()
        self.ag_where_list.setMaximumHeight(60)
        top_layout.addWidget(self.ag_where_list, 2, 2, 1, 5)
        
        layout.addLayout(top_layout)
        
        # Средняя часть с выбором колонок для GROUP BY
        group_box = QGroupBox("Выберите колонки для GROUP BY")
        group_layout = QHBoxLayout()
        
        self.column_checkboxes = {}
        self.update_column_checkboxes()
        
        group_layout.addLayout(self.columns_layout)
        group_box.setLayout(group_layout)
        layout.addWidget(group_box)
        
        # WHERE и ORDER BY
        filter_layout = QGridLayout()
        
        filter_layout.addWidget(QLabel("ORDER BY:"), 0, 0)
        self.ag_order_col = QComboBox()
        filter_layout.addWidget(self.ag_order_col, 0, 1)
        self.ag_order_dir = QComboBox()
        self.ag_order_dir.addItems(['ASC', 'DESC'])
        filter_layout.addWidget(self.ag_order_dir, 0, 2)
        ag_clear_order_btn = QPushButton("Очистить")
        ag_clear_order_btn.clicked.connect(lambda: self.ag_order_col.setCurrentIndex(0))
        filter_layout.addWidget(ag_clear_order_btn, 0, 3)
        
        execute_btn = QPushButton("Выполнить группировку")
        execute_btn.clicked.connect(self.execute_grouping)
        filter_layout.addWidget(execute_btn, 1, 3)
        
        layout.addLayout(filter_layout)
        
        # Таблица результатов
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(0)
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.result_table.verticalHeader().setDefaultSectionSize(30)
        layout.addWidget(self.result_table)
        
        self.sql_label = QLabel("SQL:")
        self.sql_label.setStyleSheet("color: #666; font-size: 9pt; word-wrap: break-word;")
        self.sql_label.setWordWrap(True)
        layout.addWidget(self.sql_label)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("background-color: #6c757d;")
        buttons_layout.addWidget(close_btn)
        layout.addLayout(buttons_layout)
    
    def update_column_checkboxes(self):
        """Обновляем checkboxes для колонок выбранной таблицы"""
        table = self.table_combo.currentText()
        cols = self.table_columns.get(table, [])
        
        # Очищаем старые checkboxes
        if hasattr(self, 'columns_layout'):
            while self.columns_layout.count():
                child = self.columns_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        else:
            self.columns_layout = QVBoxLayout()
        
        self.column_checkboxes = {}
        
        # Создаем новые checkboxes
        for col in cols:
            cb = QCheckBox(col)
            cb.setChecked(False)
            self.column_checkboxes[col] = cb
            self.columns_layout.addWidget(cb)
        
        # Выбираем первую колонку по умолчанию
        if cols:
            first_cb = self.column_checkboxes.get(cols[0])
            if first_cb:
                first_cb.setChecked(True)
        # populate select columns list and where/order combos
        try:
            self.select_columns_box.clear()
            for col in cols:
                self.select_columns_box.addItem(col)
            self.ag_where_col.clear()
            self.ag_where_col.addItems(cols)
            self.ag_order_col.clear()
            self.ag_order_col.addItems([''] + cols)
        except Exception:
            pass
    
    def on_table_changed(self):
        """При смене таблицы обновляем checkboxes"""
        self.update_column_checkboxes()

    def add_advanced_group_filter(self):
        col = self.ag_where_col.currentText()
        op = self.ag_where_op.currentText()
        val = self.ag_where_val.text().strip()
        if not col or not op or val == '':
            QMessageBox.warning(self, "Ошибка", "Заполните фильтр")
            return
        try:
            float(val)
            vf = val
        except:
            vf = f"'{val}'"
        clause = f"{col} {op} {vf}"
        self.ag_where_list.addItem(clause)
        self.ag_where_val.clear()
    
    def execute_grouping(self):
        try:
            table = self.table_combo.currentText()
            group_type = self.group_type_combo.currentText()
            # collect select columns
            sel_items = [self.select_columns_box.item(i).text() for i in range(self.select_columns_box.count()) if self.select_columns_box.item(i).isSelected()]
            select_cols = ', '.join(sel_items) if sel_items else '*'
            # where clauses
            where_clauses = [self.ag_where_list.item(i).text() for i in range(self.ag_where_list.count())]
            where = ' AND '.join(where_clauses) if where_clauses else None
            # order
            order_col = self.ag_order_col.currentText()
            order_dir = self.ag_order_dir.currentText()
            order = f"{order_col} {order_dir}" if order_col else None

            # Получаем выбранные колонки для GROUP BY
            selected_cols = [col for col, cb in self.column_checkboxes.items() if cb.isChecked()]

            if not selected_cols:
                QMessageBox.warning(self, "Ошибка", "Выберите хотя бы одну колонку для GROUP BY")
                return

            group_cols_str = ", ".join(selected_cols)

            # При SELECT * с ROLLUP/CUBE/GROUPING_SETS нужно выбирать только GROUP BY колонки
            # или использовать агрегатные функции
            if select_cols == '*':
                select_cols = group_cols_str + ", COUNT(*) as count"

            results, column_names = self.db_manager.execute_advanced_grouping(
                table, select_cols, group_type, selected_cols, where, None, order
            )

            sql = f"SELECT {select_cols} FROM bank_system.{table}"
            if where:
                sql += f" WHERE {where}"
            sql += f" GROUP BY {group_type}({group_cols_str})"
            if order:
                sql += f" ORDER BY {order}"

            self.sql_label.setText(f"SQL: {sql}")

            self.result_table.setRowCount(len(results))
            self.result_table.setColumnCount(len(column_names))
            self.result_table.setHorizontalHeaderLabels(column_names)

            for row_idx, row_data in enumerate(results):
                for col_idx, value in enumerate(row_data):
                    self.result_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

            QMessageBox.information(self, "Успех", f"Найдено записей: {len(results)}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка группировки:\n{str(e)}")
            self.logger.error(f"Advanced grouping error: {e}")


class ViewManagementDialog(QDialog):
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager
        self.logger = logging.getLogger('ViewManagementDialog')
        
        self.setWindowTitle("Управление представлениями (VIEW)")
        self.setModal(True)
        self.resize(1400, 800)
        
        self.setup_ui()
        self.refresh_views()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.setStyleSheet("""
            QPushButton {
                background-color: #FF6B35;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #E55100;
            }
        """)
        
        title = QLabel("Управление представлениями (VIEW)")
        title.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(title)
        
        # Верхняя часть - список представлений
        top_layout = QHBoxLayout()
        
        top_layout.addWidget(QLabel("Существующие представления:"))
        self.views_combo = QComboBox()
        self.views_combo.currentTextChanged.connect(self.on_view_selected)
        top_layout.addWidget(self.views_combo)
        
        refresh_btn = QPushButton("Обновить список")
        refresh_btn.clicked.connect(self.refresh_views)
        refresh_btn.setMaximumWidth(150)
        top_layout.addWidget(refresh_btn)
        
        layout.addLayout(top_layout)
        
        # Средняя часть - определение представления
        def_group = QGroupBox("Определение представления")
        def_layout = QVBoxLayout()
        
        self.definition_text = QTextEdit()
        self.definition_text.setReadOnly(True)
        self.definition_text.setMaximumHeight(150)
        self.definition_text.setStyleSheet("background-color: #f8f9fa; border: 1px solid #ddd;")
        def_layout.addWidget(self.definition_text)
        
        def_group.setLayout(def_layout)
        layout.addWidget(def_group)
        
        # Кнопки для управления
        buttons_layout = QHBoxLayout()
        
        delete_btn = QPushButton("Удалить представление")
        delete_btn.clicked.connect(self.delete_view)
        delete_btn.setStyleSheet("background-color: #dc3545;")
        buttons_layout.addWidget(delete_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # Нижняя часть - создание нового представления
        create_group = QGroupBox("Создать новое представление")
        create_layout = QVBoxLayout()
        
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Имя представления:"))
        self.view_name_edit = QLineEdit()
        self.view_name_edit.setPlaceholderText("my_view")
        name_layout.addWidget(self.view_name_edit)
        create_layout.addLayout(name_layout)
        
        # GUI builder: choose table, columns and filters instead of free SQL
        table_sel_layout = QHBoxLayout()
        table_sel_layout.addWidget(QLabel("Таблица:"))
        self.view_table_combo = QComboBox()
        table_sel_layout.addWidget(self.view_table_combo)
        load_cols_btn = QPushButton("Загрузить колонки")
        load_cols_btn.clicked.connect(self.load_view_columns)
        table_sel_layout.addWidget(load_cols_btn)
        create_layout.addLayout(table_sel_layout)

        create_layout.addWidget(QLabel("Выберите колонки:"))
        self.view_columns_box = QScrollArea()
        self.view_columns_box.setWidgetResizable(True)
        vc_widget = QWidget()
        self.view_columns_layout = QVBoxLayout(vc_widget)
        self.view_columns_layout.addStretch()
        self.view_columns_box.setWidget(vc_widget)
        self.view_columns_box.setMaximumHeight(120)
        create_layout.addWidget(self.view_columns_box)

        create_layout.addWidget(QLabel("Фильтры (WHERE):"))
        v_where_grid = QGridLayout()
        self.view_where_col = QComboBox()
        v_where_grid.addWidget(self.view_where_col, 0, 0)
        self.view_where_op = QComboBox()
        self.view_where_op.addItems(['=', '!=', '>', '<', '>=', '<=', 'LIKE', 'ILIKE', 'IN'])
        v_where_grid.addWidget(self.view_where_op, 0, 1)
        self.view_where_val = QLineEdit()
        v_where_grid.addWidget(self.view_where_val, 0, 2)
        v_add_filter_btn = QPushButton("Добавить фильтр")
        v_add_filter_btn.clicked.connect(self.add_view_filter)
        v_where_grid.addWidget(v_add_filter_btn, 0, 3)
        self.view_where_list = QListWidget()
        v_where_grid.addWidget(self.view_where_list, 1, 0, 1, 4)
        create_layout.addLayout(v_where_grid)
        
        create_btn = QPushButton("Создать представление")
        create_btn.clicked.connect(self.create_view_from_builder)
        create_btn.setStyleSheet("background-color: #28a745;")
        create_layout.addWidget(create_btn)
        
        create_group.setLayout(create_layout)
        layout.addWidget(create_group)
        
        # Кнопка закрытия
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("background-color: #6c757d;")
        close_layout.addWidget(close_btn)
        layout.addLayout(close_layout)
    
    def refresh_views(self):
        """Обновить список представлений"""
        try:
            views = self.db_manager.get_views()
            self.views_combo.blockSignals(True)
            self.views_combo.clear()
            
            if views:
                self.views_combo.addItems(views)
                self.views_combo.blockSignals(False)
                self.views_combo.setCurrentIndex(0)
                self.on_view_selected(views[0])
            else:
                self.views_combo.blockSignals(False)
                self.definition_text.clear()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при получении списка представлений:\n{str(e)}")
            self.logger.error(f"Refresh views error: {e}")

    def load_view_columns(self):
        table = self.view_table_combo.currentText()
        if not table:
            return
        # clear existing
        while self.view_columns_layout.count() > 1:
            item = self.view_columns_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

        try:
            cols = self.db_manager.get_table_columns(table)
            col_names = [c['name'] for c in cols]
            for col in col_names:
                cb = QCheckBox(col)
                cb.setChecked(True)
                self.view_columns_layout.insertWidget(self.view_columns_layout.count() - 1, cb)
            # populate where column combo
            self.view_where_col.clear()
            self.view_where_col.addItems(col_names)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить колонки:\n{str(e)}")
            self.logger.error(f"Load view columns error: {e}")

    def add_view_filter(self):
        col = self.view_where_col.currentText()
        op = self.view_where_op.currentText()
        val = self.view_where_val.text().strip()
        if not col or not op or val == '':
            QMessageBox.warning(self, "Ошибка", "Заполните фильтр")
            return
        try:
            float(val)
            vf = val
        except:
            vf = f"'{val}'"
        clause = f"{col} {op} {vf}"
        self.view_where_list.addItem(clause)
        self.view_where_val.clear()

    def create_view_from_builder(self):
        view_name = self.view_name_edit.text().strip()
        table = self.view_table_combo.currentText()
        if not view_name:
            QMessageBox.warning(self, "Ошибка", "Укажите имя представления")
            return
        if not table:
            QMessageBox.warning(self, "Ошибка", "Выберите таблицу")
            return
        selected_columns = []
        for i in range(self.view_columns_layout.count()):
            item = self.view_columns_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), QCheckBox):
                w = item.widget()
                if w.isChecked():
                    selected_columns.append(w.text())
        if not selected_columns:
            QMessageBox.warning(self, "Ошибка", "Выберите хотя бы одну колонку")
            return
        columns_str = ", ".join(f"bank_system.{table}.{c}" for c in selected_columns)
        where_clauses = [self.view_where_list.item(i).text() for i in range(self.view_where_list.count())]
        sql_query = f"SELECT {columns_str} FROM bank_system.{table}"
        if where_clauses:
            sql_query += " WHERE " + " AND ".join(where_clauses)
        try:
            self.db_manager.create_view(view_name, sql_query)
            QMessageBox.information(self, "Успех", f"Представление '{view_name}' успешно создано")
            self.view_name_edit.clear()
            # clear filters
            self.view_where_list.clear()
            self.refresh_views()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка создания представления:\n{str(e)}")
            self.logger.error(f"Create view error: {e}")
    
    def on_view_selected(self, view_name: str):
        """Показать определение выбранного представления"""
        if not view_name:
            self.definition_text.clear()
            return
        
        try:
            definition = self.db_manager.get_view_definition(view_name)
            self.definition_text.setText(definition)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при получении определения представления:\n{str(e)}")
            self.logger.error(f"Get view definition error: {e}")
    
    def create_view(self):
        """Создать новое представление"""
        view_name = self.view_name_edit.text().strip()
        sql_query = self.sql_edit.toPlainText().strip()
        
        if not view_name:
            QMessageBox.warning(self, "Ошибка", "Укажите имя представления")
            return
        
        if not sql_query:
            QMessageBox.warning(self, "Ошибка", "Укажите SQL запрос")
            return
        
        try:
            self.db_manager.create_view(view_name, sql_query)
            QMessageBox.information(self, "Успех", f"Представление '{view_name}' успешно создано")
            self.view_name_edit.clear()
            self.sql_edit.clear()
            self.refresh_views()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка создания представления:\n{str(e)}")
    
    def delete_view(self):
        """Удалить представление"""
        view_name = self.views_combo.currentText()
        
        if not view_name:
            QMessageBox.warning(self, "Ошибка", "Выберите представление для удаления")
            return
        
        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить представление '{view_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db_manager.drop_view(view_name)
                QMessageBox.information(self, "Успех", f"Представление '{view_name}' успешно удалено")
                self.refresh_views()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка удаления представления:\n{str(e)}")
                self.logger.error(f"Delete view error: {e}")


class MaterializedViewManagementDialog(QDialog):
    """Диалог для управления материализованными представлениями"""
    
    def __init__(self, db_manager, logger, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.logger = logger
        self.setWindowTitle("Материализованные представления")
        self.setGeometry(100, 100, 800, 600)
        self.init_ui()
        self.refresh_views()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Верхняя часть - список существующих представлений
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Выберите представление:"))
        
        self.mviews_combo = QComboBox()
        self.mviews_combo.currentTextChanged.connect(self.on_view_selected)
        top_layout.addWidget(self.mviews_combo)
        
        self.refresh_btn = QPushButton("Обновить список")
        self.refresh_btn.clicked.connect(self.refresh_views)
        top_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(top_layout)
        
        # Определение представления
        layout.addWidget(QLabel("Определение представления:"))
        self.definition_text = QTextEdit()
        self.definition_text.setReadOnly(True)
        layout.addWidget(self.definition_text)
        
        # Кнопки управления
        control_layout = QHBoxLayout()
        
        self.refresh_mview_btn = QPushButton("Обновить данные")
        self.refresh_mview_btn.clicked.connect(self.refresh_mview_data)
        control_layout.addWidget(self.refresh_mview_btn)
        
        self.delete_mview_btn = QPushButton("Удалить")
        self.delete_mview_btn.clicked.connect(self.delete_view)
        control_layout.addWidget(self.delete_mview_btn)
        
        layout.addLayout(control_layout)
        
        # Создание нового представления
        layout.addWidget(QLabel("Создать новое материализованное представление:"))
        
        form_layout = QFormLayout()
        
        self.mview_name_edit = QLineEdit()
        form_layout.addRow("Имя представления:", self.mview_name_edit)
        
        self.table_combo = QComboBox()
        self.table_combo.currentTextChanged.connect(self.update_mview_columns)
        form_layout.addRow("Выберите таблицу:", self.table_combo)
        
        layout.addLayout(form_layout)
        
        # Выбор колонок
        layout.addWidget(QLabel("Выберите колонки:"))
        
        # Контейнер для чекбоксов с прокруткой
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.mview_columns = QVBoxLayout(scroll_widget)
        self.mview_columns.addStretch()
        scroll.setWidget(scroll_widget)
        scroll.setMaximumHeight(150)
        layout.addWidget(scroll)

        # WHERE filter builder for materialized view
        layout.addWidget(QLabel("Фильтры (WHERE, опционально):"))
        mv_where_grid = QGridLayout()
        self.mv_where_col = QComboBox()
        mv_where_grid.addWidget(self.mv_where_col, 0, 0)
        self.mv_where_op = QComboBox()
        self.mv_where_op.addItems(['=', '!=', '>', '<', '>=', '<=', 'LIKE', 'ILIKE', 'IN'])
        mv_where_grid.addWidget(self.mv_where_op, 0, 1)
        self.mv_where_val = QLineEdit()
        mv_where_grid.addWidget(self.mv_where_val, 0, 2)
        mv_add_filter_btn = QPushButton("Добавить фильтр")
        mv_add_filter_btn.clicked.connect(self.add_mview_filter)
        mv_where_grid.addWidget(mv_add_filter_btn, 0, 3)
        self.mv_where_list = QListWidget()
        mv_where_grid.addWidget(self.mv_where_list, 1, 0, 1, 4)
        layout.addLayout(mv_where_grid)
        
        # Кнопка создания
        create_btn = QPushButton("Создать представление")
        create_btn.clicked.connect(self.create_view)
        create_btn.setStyleSheet("background-color: #0066cc; color: white; font-weight: bold; padding: 5px;")
        layout.addWidget(create_btn)
        
        self.setLayout(layout)
        self.load_mview_tables()
    
    def refresh_views(self):
        """Обновить список материализованных представлений"""
        try:
            mviews = self.db_manager.get_materialized_views()
            self.mviews_combo.blockSignals(True)
            self.mviews_combo.clear()
            
            if mviews:
                self.mviews_combo.addItems(mviews)
                self.mviews_combo.blockSignals(False)
                self.mviews_combo.setCurrentIndex(0)
                self.on_view_selected(mviews[0])
            else:
                self.mviews_combo.blockSignals(False)
                self.definition_text.clear()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при получении списка материализованных представлений:\n{str(e)}")
            self.logger.error(f"Refresh materialized views error: {e}")
    
    def on_view_selected(self, view_name):
        """При выборе представления показать его определение"""
        if not view_name:
            self.definition_text.clear()
            return
        
        try:
            definition = self.db_manager.get_materialized_view_definition(view_name)
            self.definition_text.setText(definition)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при получении определения представления:\n{str(e)}")
            self.logger.error(f"Get materialized view definition error: {e}")
    
    def create_view(self):
        """Создать новое материализованное представление"""
        view_name = self.mview_name_edit.text().strip()
        table_name = self.table_combo.currentText()

        if not view_name:
            QMessageBox.warning(self, "Ошибка", "Укажите имя представления")
            return

        if not table_name:
            QMessageBox.warning(self, "Ошибка", "Выберите таблицу")
            return

        # Собрать выбранные колонки
        selected_columns = []
        for i in range(self.mview_columns.count()):
            item = self.mview_columns.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, QCheckBox) and widget.isChecked():
                    selected_columns.append(widget.text())

        if not selected_columns:
            QMessageBox.warning(self, "Ошибка", "Выберите хотя бы одну колонку")
            return

        # Собрать SQL запрос
        columns_str = ", ".join(f"bank_system.{table_name}.{col}" for col in selected_columns)
        sql_query = f"SELECT {columns_str} FROM bank_system.{table_name}"
        # add where filters if any
        where_clauses = [self.mv_where_list.item(i).text() for i in range(self.mv_where_list.count())]
        if where_clauses:
            sql_query += " WHERE " + " AND ".join(where_clauses)

        try:
            self.db_manager.create_materialized_view(view_name, sql_query)
            QMessageBox.information(self, "Успех", f"Материализованное представление '{view_name}' успешно создано")
            self.mview_name_edit.clear()
            self.mv_where_list.clear()
            self.refresh_views()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка создания представления:\n{str(e)}")
    
    def refresh_mview_data(self):
        """Обновить данные в материализованном представлении"""
        view_name = self.mviews_combo.currentText()
        if not view_name:
            QMessageBox.warning(self, "Ошибка", "Выберите представление")
            return
        
        try:
            self.db_manager.refresh_materialized_view(view_name)
            QMessageBox.information(self, "Успех", f"Материализованное представление '{view_name}' обновлено")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка обновления представления:\n{str(e)}")
    
    def delete_view(self):
        """Удалить материализованное представление"""
        view_name = self.mviews_combo.currentText()
        if not view_name:
            QMessageBox.warning(self, "Ошибка", "Выберите представление для удаления")
            return
        
        reply = QMessageBox.question(
            self, 
            "Подтверждение", 
            f"Вы уверены, что хотите удалить представление '{view_name}'?"
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db_manager.drop_materialized_view(view_name)
                QMessageBox.information(self, "Успех", f"Материализованное представление '{view_name}' успешно удалено")
                self.refresh_views()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка удаления представления:\n{str(e)}")

    def add_mview_filter(self):
        col = self.mv_where_col.currentText()
        op = self.mv_where_op.currentText()
        val = self.mv_where_val.text().strip()
        if not col or not op or val == '':
            QMessageBox.warning(self, "Ошибка", "Заполните фильтр")
            return
        try:
            float(val)
            vf = val
        except:
            vf = f"'{val}'"
        clause = f"{col} {op} {vf}"
        self.mv_where_list.addItem(clause)
        self.mv_where_val.clear()
    
    def load_mview_tables(self):
        """Загрузить список таблиц"""
        try:
            tables = self.db_manager.get_tables_list()
            self.table_combo.blockSignals(True)
            self.table_combo.clear()
            self.table_combo.addItems(tables)
            self.table_combo.blockSignals(False)
            if tables:
                self.update_mview_columns(tables[0])
        except Exception as e:
            self.logger.error(f"Load materialized view tables error: {e}")
    
    def update_mview_columns(self, table_name):
        """Обновить список колонок для выбранной таблицы"""
        if not table_name:
            return

        # Очистить предыдущие чекбоксы
        while self.mview_columns.count() > 0:
            item = self.mview_columns.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

        try:
            columns_info = self.db_manager.get_table_columns(table_name)
            for col_info in columns_info:
                col_name = col_info['name']
                checkbox = QCheckBox(col_name)
                checkbox.setChecked(True)
                self.mview_columns.insertWidget(self.mview_columns.count() - 1, checkbox)
            # populate where column combo
            self.mv_where_col.clear()
            self.mv_where_col.addItems([c['name'] for c in columns_info])
        except Exception as e:
            self.logger.error(f"Update materialized view columns error: {e}")


class CTEConstructorDialog(QDialog):
    """Конструктор для работы с Common Table Expressions (CTE)"""
    
    def __init__(self, db_manager, logger, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.logger = logger
        self.ctes = {}  # Словарь CTE: {имя: {таблица, колонки, условие}}
        
        self.setWindowTitle("Конструктор CTE (WITH запросы)")
        self.setGeometry(100, 100, 1000, 700)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Верхняя часть - добавление новой CTE
        layout.addWidget(QLabel("Создать новую временную выборку (CTE):"))
        
        form_layout = QFormLayout()
        
        self.cte_name_edit = QLineEdit()
        self.cte_name_edit.setPlaceholderText("Например: recent_transactions")
        form_layout.addRow("Имя CTE:", self.cte_name_edit)
        
        self.cte_table_combo = QComboBox()
        form_layout.addRow("Выберите таблицу:", self.cte_table_combo)
        
        layout.addLayout(form_layout)
        
        # Выбор колонок
        layout.addWidget(QLabel("Выберите колонки:"))
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.cte_columns = QVBoxLayout(scroll_widget)
        self.cte_columns.addStretch()
        scroll.setWidget(scroll_widget)
        scroll.setMaximumHeight(100)
        layout.addWidget(scroll)
        
        # WHERE условие
        layout.addWidget(QLabel("WHERE условие (опционально):"))
        # structured where builder for CTE
        where_grid = QGridLayout()
        self.cte_where_col = QComboBox()
        where_grid.addWidget(self.cte_where_col, 0, 0)
        self.cte_where_op = QComboBox()
        self.cte_where_op.addItems(['=', '!=', '>', '<', '>=', '<=', 'LIKE', 'ILIKE'])
        where_grid.addWidget(self.cte_where_op, 0, 1)
        self.cte_where_val = QLineEdit()
        where_grid.addWidget(self.cte_where_val, 0, 2)
        add_cte_filter_btn = QPushButton("Добавить фильтр")
        add_cte_filter_btn.clicked.connect(self.add_cte_filter)
        where_grid.addWidget(add_cte_filter_btn, 0, 3)
        self.cte_where_list = QListWidget()
        where_grid.addWidget(self.cte_where_list, 1, 0, 1, 4)
        layout.addLayout(where_grid)
        
        # Кнопка добавления CTE
        add_cte_btn = QPushButton("Добавить CTE")
        add_cte_btn.clicked.connect(self.add_cte)
        add_cte_btn.setStyleSheet("background-color: #0066cc; color: white; font-weight: bold; padding: 5px;")
        layout.addWidget(add_cte_btn)
        
        layout.addWidget(QLabel(""))
        
        # Список добавленных CTE
        layout.addWidget(QLabel("Добавленные временные выборки:"))
        
        self.ctes_list = QTableWidget()
        self.ctes_list.setColumnCount(3)
        self.ctes_list.setHorizontalHeaderLabels(["Имя CTE", "Таблица", "Действия"])
        self.ctes_list.horizontalHeader().setStretchLastSection(False)
        layout.addWidget(self.ctes_list)
        
        # Построение финального запроса
        layout.addWidget(QLabel("Основной запрос (SELECT из CTE):"))
        
        self.main_select_table_combo = QComboBox()
        self.main_select_table_combo.currentTextChanged.connect(self.update_main_columns)
        layout.addWidget(QLabel("Выберите источник данных:"))
        layout.addWidget(self.main_select_table_combo)
        
        layout.addWidget(QLabel("Выберите колонки для результата:"))
        scroll2 = QScrollArea()
        scroll2.setWidgetResizable(True)
        scroll_widget2 = QWidget()
        self.main_columns = QVBoxLayout(scroll_widget2)
        self.main_columns.addStretch()
        scroll2.setWidget(scroll_widget2)
        scroll2.setMaximumHeight(100)
        layout.addWidget(scroll2)
        
        # WHERE условие для основного запроса
        layout.addWidget(QLabel("WHERE условие для основного запроса (опционально):"))
        main_where_grid = QGridLayout()
        self.main_where_col = QComboBox()
        main_where_grid.addWidget(self.main_where_col, 0, 0)
        self.main_where_op = QComboBox()
        self.main_where_op.addItems(['=', '!=', '>', '<', '>=', '<=', 'LIKE', 'ILIKE', 'IN'])
        main_where_grid.addWidget(self.main_where_op, 0, 1)
        self.main_where_val = QLineEdit()
        main_where_grid.addWidget(self.main_where_val, 0, 2)
        add_main_filter_btn = QPushButton("Добавить фильтр")
        add_main_filter_btn.clicked.connect(self.add_main_filter)
        main_where_grid.addWidget(add_main_filter_btn, 0, 3)
        self.main_where_list = QListWidget()
        main_where_grid.addWidget(self.main_where_list, 1, 0, 1, 4)
        layout.addLayout(main_where_grid)
        
        # Кнопки действий
        buttons_layout = QHBoxLayout()
        
        execute_btn = QPushButton("Выполнить запрос")
        execute_btn.clicked.connect(self.execute_query)
        execute_btn.setStyleSheet("background-color: #27AE60; color: white; font-weight: bold; padding: 5px;")
        buttons_layout.addWidget(execute_btn)
        
        copy_btn = QPushButton("Скопировать SQL")
        copy_btn.clicked.connect(self.copy_sql)
        buttons_layout.addWidget(copy_btn)
        
        layout.addLayout(buttons_layout)
        
        # Предпросмотр SQL
        layout.addWidget(QLabel("Генерируемый SQL:"))
        self.sql_preview = QTextEdit()
        self.sql_preview.setReadOnly(True)
        self.sql_preview.setMaximumHeight(120)
        layout.addWidget(self.sql_preview)
        
        # Результаты запроса
        layout.addWidget(QLabel("Результаты:"))
        self.results_table = QTableWidget()
        layout.addWidget(self.results_table)
        
        self.setLayout(layout)
        self.load_tables()
        self.cte_table_combo.currentTextChanged.connect(self.update_cte_columns)
    
    def load_tables(self):
        """Загрузить список таблиц"""
        try:
            tables = self.db_manager.get_tables_list()
            self.cte_table_combo.blockSignals(True)
            self.main_select_table_combo.blockSignals(True)
            
            self.cte_table_combo.clear()
            self.main_select_table_combo.clear()
            
            self.cte_table_combo.addItems(tables)
            self.main_select_table_combo.addItems(tables)
            
            self.cte_table_combo.blockSignals(False)
            self.main_select_table_combo.blockSignals(False)
            
            if tables:
                self.update_cte_columns(tables[0])
                self.update_main_columns(tables[0])
        except Exception as e:
            self.logger.error(f"Load tables error: {e}")
    
    def update_cte_columns(self, table_name):
        """Обновить список колонок для CTE таблицы"""
        if not table_name:
            return
        
        while self.cte_columns.count() > 0:
            item = self.cte_columns.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
        
        try:
            columns_info = self.db_manager.get_table_columns(table_name)
            for col_info in columns_info:
                col_name = col_info['name']
                checkbox = QCheckBox(col_name)
                checkbox.setChecked(True)
                self.cte_columns.insertWidget(self.cte_columns.count() - 1, checkbox)
            # populate cte where column combo
            self.cte_where_col.clear()
            self.cte_where_col.addItems([c['name'] for c in columns_info])
            # populate main where / main columns combos
            self.main_where_col.clear()
            self.main_where_col.addItems([c['name'] for c in columns_info])
            # also update main_columns widgets set
            self.update_main_columns(table_name)
        except Exception as e:
            self.logger.error(f"Update CTE columns error: {e}")
    
    def update_main_columns(self, table_name):
        """Обновить список колонок для основного запроса"""
        if not table_name:
            return
        
        while self.main_columns.count() > 0:
            item = self.main_columns.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
        
        try:
            # Если выбрана CTE, показать её колонки
            if table_name in self.ctes:
                for col in self.ctes[table_name]['selected_columns']:
                    checkbox = QCheckBox(col)
                    checkbox.setChecked(True)
                    self.main_columns.insertWidget(self.main_columns.count() - 1, checkbox)
            else:
                # Иначе показать колонки таблицы
                columns_info = self.db_manager.get_table_columns(table_name)
                for col_info in columns_info:
                    col_name = col_info['name']
                    checkbox = QCheckBox(col_name)
                    checkbox.setChecked(True)
                    self.main_columns.insertWidget(self.main_columns.count() - 1, checkbox)
        except Exception as e:
            self.logger.error(f"Update main columns error: {e}")
    
    def add_cte(self):
        """Добавить новую CTE"""
        cte_name = self.cte_name_edit.text().strip()
        table_name = self.cte_table_combo.currentText()
        
        if not cte_name:
            QMessageBox.warning(self, "Ошибка", "Укажите имя CTE")
            return
        
        if not table_name:
            QMessageBox.warning(self, "Ошибка", "Выберите таблицу")
            return
        
        if cte_name in self.ctes:
            QMessageBox.warning(self, "Ошибка", f"CTE с именем '{cte_name}' уже существует")
            return
        
        # Собрать выбранные колонки
        selected_columns = []
        for i in range(self.cte_columns.count()):
            item = self.cte_columns.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, QCheckBox) and widget.isChecked():
                    selected_columns.append(widget.text())
        
        if not selected_columns:
            QMessageBox.warning(self, "Ошибка", "Выберите хотя бы одну колонку")
            return
        
        where_condition = self.cte_where_edit.toPlainText().strip()
        
        # Сохранить CTE
        self.ctes[cte_name] = {
            'table': table_name,
            'selected_columns': selected_columns,
            'where': where_condition
        }
        
        # Добавить в таблицу
        self.ctes_list.insertRow(self.ctes_list.rowCount())
        row = self.ctes_list.rowCount() - 1
        self.ctes_list.setItem(row, 0, QTableWidgetItem(cte_name))
        self.ctes_list.setItem(row, 1, QTableWidgetItem(table_name))
        
        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(lambda checked, name=cte_name: self.delete_cte(name))
        self.ctes_list.setCellWidget(row, 2, delete_btn)
        
        # Очистить форму
        self.cte_name_edit.clear()
        self.cte_where_edit.clear()
        
        # Обновить комбобокс источников
        cte_names = list(self.ctes.keys())
        all_sources = cte_names + self.db_manager.get_tables_list()
        self.main_select_table_combo.blockSignals(True)
        current_text = self.main_select_table_combo.currentText()
        self.main_select_table_combo.clear()
        self.main_select_table_combo.addItems(all_sources)
        if current_text in all_sources:
            self.main_select_table_combo.setCurrentText(current_text)
        self.main_select_table_combo.blockSignals(False)
        
        QMessageBox.information(self, "Успех", f"CTE '{cte_name}' добавлена")

    def add_cte_filter(self):
        col = self.cte_where_col.currentText()
        op = self.cte_where_op.currentText()
        val = self.cte_where_val.text().strip()
        if not col or not op or val == '':
            QMessageBox.warning(self, "Ошибка", "Заполните фильтр CTE")
            return
        try:
            float(val)
            vf = val
        except:
            vf = f"'{val}'"
        clause = f"{col} {op} {vf}"
        self.cte_where_list.addItem(clause)
        self.cte_where_val.clear()

    def add_main_filter(self):
        col = self.main_where_col.currentText()
        op = self.main_where_op.currentText()
        val = self.main_where_val.text().strip()
        if not col or not op or val == '':
            QMessageBox.warning(self, "Ошибка", "Заполните фильтр основного запроса")
            return
        try:
            float(val)
            vf = val
        except:
            vf = f"'{val}'"
        clause = f"{col} {op} {vf}"
        self.main_where_list.addItem(clause)
        self.main_where_val.clear()
    
    def delete_cte(self, cte_name):
        """Удалить CTE"""
        if cte_name in self.ctes:
            del self.ctes[cte_name]
            
            # Удалить из таблицы
            for row in range(self.ctes_list.rowCount()):
                if self.ctes_list.item(row, 0).text() == cte_name:
                    self.ctes_list.removeRow(row)
                    break
            
            # Обновить комбобокс
            cte_names = list(self.ctes.keys())
            all_sources = cte_names + self.db_manager.get_tables_list()
            self.main_select_table_combo.blockSignals(True)
            current_text = self.main_select_table_combo.currentText()
            self.main_select_table_combo.clear()
            self.main_select_table_combo.addItems(all_sources)
            if current_text in all_sources:
                self.main_select_table_combo.setCurrentText(current_text)
            self.main_select_table_combo.blockSignals(False)
    
    def build_sql(self):
        """Построить SQL запрос"""
        sql_parts = []
        
        # Построить WITH часть
        if self.ctes:
            cte_list = []
            for cte_name, cte_info in self.ctes.items():
                table = cte_info['table']
                columns = ", ".join(cte_info['selected_columns'])
                cte_sql = f"{cte_name} AS (SELECT {columns} FROM bank_system.{table}"
                
                if cte_info['where']:
                    cte_sql += f" WHERE {cte_info['where']}"
                
                cte_sql += ")"
                cte_list.append(cte_sql)
            
            sql_parts.append("WITH " + ",\n     ".join(cte_list))
        
        # Построить основной SELECT
        main_table = self.main_select_table_combo.currentText()
        if not main_table:
            return None
        
        # Собрать выбранные колонки
        selected_columns = []
        for i in range(self.main_columns.count()):
            item = self.main_columns.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, QCheckBox) and widget.isChecked():
                    selected_columns.append(widget.text())
        
        if not selected_columns:
            return None
        
        columns_str = ", ".join(selected_columns)
        
        # Определить, это CTE или таблица
        if main_table in self.ctes:
            main_sql = f"SELECT {columns_str} FROM {main_table}"
        else:
            main_sql = f"SELECT {columns_str} FROM bank_system.{main_table}"
        
        main_where = self.main_where_edit.toPlainText().strip()
        if main_where:
            main_sql += f" WHERE {main_where}"
        
        sql_parts.append(main_sql)
        
        return "\n".join(sql_parts)
    
    def execute_query(self):
        """Выполнить построенный запрос"""
        sql = self.build_sql()
        if not sql:
            QMessageBox.warning(self, "Ошибка", "Не удалось построить запрос")
            return
        
        self.sql_preview.setText(sql)
        
        try:
            results = self.db_manager.execute_query(sql)
            self.display_results(results)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка выполнения запроса:\n{str(e)}")
            self.logger.error(f"CTE execute error: {e}")
    
    def display_results(self, results):
        """Отобразить результаты запроса"""
        if not results:
            self.results_table.setRowCount(0)
            self.results_table.setColumnCount(0)
            return
        
        # Получить названия колонок
        first_row = results[0]
        columns = [str(i) for i in range(len(first_row))]
        
        self.results_table.setColumnCount(len(columns))
        self.results_table.setHorizontalHeaderLabels(columns)
        self.results_table.setRowCount(len(results))
        
        for row_idx, row_data in enumerate(results):
            for col_idx, value in enumerate(row_data):
                self.results_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
    
    def copy_sql(self):
        """Скопировать SQL в буфер обмена"""
        sql = self.build_sql()
        if sql:
            clipboard = QApplication.clipboard()
            clipboard.setText(sql)
            QMessageBox.information(self, "Успех", "SQL скопирован в буфер обмена")