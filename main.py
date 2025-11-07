import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QLabel, QTextEdit,
                               QGroupBox, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import logging
from logger_config import setup_logger
from db_manager import DatabaseManager
from gui_windows import (ConnectionDialog, AddDataDialog, ViewDataDialog,
                         AlterTableDialog, AdvancedSelectDialog, TextSearchDialog,
                         StringFunctionsDialog, JoinWizardDialog, SubqueryFilterDialog,
                         CustomTypesDialog, SimilarToDialog, AggregationDialog)


class BankSystemApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = setup_logger()
        self.db_manager = None
        self.is_connected = False

        self.setWindowTitle("Банковская система - Работа с валютными операциями")
        self.setGeometry(100, 100, 900, 700)

        self.setup_ui()
        self.show_connection_dialog()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        title_label = QLabel("Банковская система\nУправление валютными операциями")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Arial", 16, QFont.Weight.Bold)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)

        status_group = QGroupBox("Статус подключения")
        status_layout = QVBoxLayout()
        self.status_label = QLabel("⚠ Не подключено к базе данных")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(self.status_label)
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)

        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(10)

        button_style = """
            QPushButton {
                background-color: #2E86AB;
                color: white;
                font-weight: bold;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1B5B7E;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #666666;
            }
        """

        self.btn_create_schema = QPushButton("Создать схему и таблицы")
        self.btn_create_schema.setMinimumHeight(40)
        self.btn_create_schema.setEnabled(False)
        self.btn_create_schema.setStyleSheet(button_style)
        self.btn_create_schema.clicked.connect(self.create_schema)
        buttons_layout.addWidget(self.btn_create_schema)

        self.btn_drop_schema = QPushButton("Удалить схему bank_system")
        self.btn_drop_schema.setMinimumHeight(40)
        self.btn_drop_schema.setEnabled(False)
        self.btn_drop_schema.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
                font-weight: bold;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #666666;
            }
        """)
        self.btn_drop_schema.clicked.connect(self.drop_schema)
        buttons_layout.addWidget(self.btn_drop_schema)

        self.btn_insert_data = QPushButton("Внести данные")
        self.btn_insert_data.setMinimumHeight(40)
        self.btn_insert_data.setEnabled(False)
        self.btn_insert_data.setStyleSheet(button_style)
        self.btn_insert_data.clicked.connect(self.show_insert_dialog)
        buttons_layout.addWidget(self.btn_insert_data)

        self.btn_view_data = QPushButton("Показать данные")
        self.btn_view_data.setMinimumHeight(40)
        self.btn_view_data.setEnabled(False)
        self.btn_view_data.setStyleSheet(button_style)
        self.btn_view_data.clicked.connect(self.show_view_dialog)
        buttons_layout.addWidget(self.btn_view_data)

        advanced_style = """
            QPushButton {
                background-color: #6610f2;
                color: white;
                font-weight: bold;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #520dc2;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #666666;
            }
        """

        advanced_style_3 = """
            QPushButton {
                background-color: #FF8C00;
                color: white;
                font-weight: bold;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #E67E00;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #666666;
            }
        """

        self.btn_alter_table = QPushButton("ALTER TABLE - Изменить структуру БД")
        self.btn_alter_table.setMinimumHeight(40)
        self.btn_alter_table.setEnabled(False)
        self.btn_alter_table.setStyleSheet(advanced_style)
        self.btn_alter_table.clicked.connect(self.show_alter_table_dialog)
        buttons_layout.addWidget(self.btn_alter_table)

        self.btn_advanced_select = QPushButton("Расширенный SELECT")
        self.btn_advanced_select.setMinimumHeight(40)
        self.btn_advanced_select.setEnabled(False)
        self.btn_advanced_select.setStyleSheet(advanced_style)
        self.btn_advanced_select.clicked.connect(self.show_advanced_select_dialog)
        buttons_layout.addWidget(self.btn_advanced_select)

        self.btn_text_search = QPushButton("Поиск по тексту (LIKE / REGEX)")
        self.btn_text_search.setMinimumHeight(40)
        self.btn_text_search.setEnabled(False)
        self.btn_text_search.setStyleSheet(advanced_style)
        self.btn_text_search.clicked.connect(self.show_text_search_dialog)
        buttons_layout.addWidget(self.btn_text_search)

        self.btn_string_functions = QPushButton("Функции работы со строками")
        self.btn_string_functions.setMinimumHeight(40)
        self.btn_string_functions.setEnabled(False)
        self.btn_string_functions.setStyleSheet(advanced_style)
        self.btn_string_functions.clicked.connect(self.show_string_functions_dialog)
        buttons_layout.addWidget(self.btn_string_functions)

        self.btn_join_wizard = QPushButton("Мастер соединений (JOIN)")
        self.btn_join_wizard.setMinimumHeight(40)
        self.btn_join_wizard.setEnabled(False)
        self.btn_join_wizard.setStyleSheet(advanced_style)
        self.btn_join_wizard.clicked.connect(self.show_join_wizard_dialog)
        buttons_layout.addWidget(self.btn_join_wizard)

        self.btn_subquery_filter = QPushButton("Фильтры на основе подзапросов")
        self.btn_subquery_filter.setMinimumHeight(40)
        self.btn_subquery_filter.setEnabled(False)
        self.btn_subquery_filter.setStyleSheet(advanced_style_3)
        self.btn_subquery_filter.clicked.connect(self.show_subquery_filter_dialog)
        buttons_layout.addWidget(self.btn_subquery_filter)

        self.btn_custom_types = QPushButton("Пользовательские типы данных")
        self.btn_custom_types.setMinimumHeight(40)
        self.btn_custom_types.setEnabled(False)
        self.btn_custom_types.setStyleSheet(advanced_style_3)
        self.btn_custom_types.clicked.connect(self.show_custom_types_dialog)
        buttons_layout.addWidget(self.btn_custom_types)

        self.btn_similar_to = QPushButton("Поиск SIMILAR TO")
        self.btn_similar_to.setMinimumHeight(40)
        self.btn_similar_to.setEnabled(False)
        self.btn_similar_to.setStyleSheet(advanced_style_3)
        self.btn_similar_to.clicked.connect(self.show_similar_to_dialog)
        buttons_layout.addWidget(self.btn_similar_to)

        self.btn_aggregation = QPushButton("Агрегирование и группировка")
        self.btn_aggregation.setMinimumHeight(40)
        self.btn_aggregation.setEnabled(False)
        self.btn_aggregation.setStyleSheet(advanced_style_3)
        self.btn_aggregation.clicked.connect(self.show_aggregation_dialog)
        buttons_layout.addWidget(self.btn_aggregation)

        self.btn_reconnect = QPushButton("Переподключиться к БД")
        self.btn_reconnect.setMinimumHeight(40)
        self.btn_reconnect.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                font-weight: bold;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        self.btn_reconnect.clicked.connect(self.show_connection_dialog)
        buttons_layout.addWidget(self.btn_reconnect)

        main_layout.addLayout(buttons_layout)

        log_group = QGroupBox("Последние действия")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #F8F9FA;
                border: 1px solid #DDD;
                border-radius: 3px;
                padding: 5px;
                font-family: Consolas, monospace;
            }
        """)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)

        group_style = """
            QGroupBox {
                font-weight: bold;
                border: 2px solid #CCCCCC;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """
        status_group.setStyleSheet(group_style)
        log_group.setStyleSheet(group_style)

    def show_connection_dialog(self):
        dialog = ConnectionDialog(self)
        if dialog.exec():
            params = dialog.get_connection_params()
            if params:
                self.connect_to_database(params)

    def connect_to_database(self, params):
        try:
            if self.db_manager:
                self.db_manager.disconnect()

            self.db_manager = DatabaseManager(
                host=params['host'],
                port=int(params['port']),
                database=params['database'],
                user=params['user'],
                password=params['password']
            )

            self.db_manager.connect()
            self.is_connected = True

            self.status_label.setText(f"✓ Подключено к {params['database']} на {params['host']}")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")

            self.btn_create_schema.setEnabled(True)
            self.btn_insert_data.setEnabled(True)
            self.btn_view_data.setEnabled(True)
            self.btn_drop_schema.setEnabled(True)
            self.btn_alter_table.setEnabled(True)
            self.btn_advanced_select.setEnabled(True)
            self.btn_text_search.setEnabled(True)
            self.btn_similar_to.setEnabled(True)
            self.btn_string_functions.setEnabled(True)
            self.btn_join_wizard.setEnabled(True)
            self.btn_subquery_filter.setEnabled(True)
            self.btn_custom_types.setEnabled(True)
            self.btn_aggregation.setEnabled(True)

            self.add_log("Успешное подключение к базе данных")
            QMessageBox.information(self, "Успех", "Подключение к базе данных установлено")

        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            QMessageBox.critical(self, "Ошибка подключения", str(e))
            self.add_log(f"Ошибка подключения: {e}")

    def create_schema(self):
        if not self.is_connected:
            QMessageBox.warning(self, "Предупреждение", "Нет подключения к базе данных")
            return

        try:
            with open('database_schema.sql', 'r', encoding='utf-8') as f:
                sql_script = f.read()

            self.db_manager.execute_script(sql_script)

            QMessageBox.information(
                self,
                "Успех",
                "Схема базы данных успешно создана!\n\n"
                "Созданы:\n"
                "- Схема bank_system\n"
                "- Типы ENUM (transaction_type, account_status)\n"
                "- 5 таблиц с ограничениями\n"
                "- Индексы для оптимизации\n"
                "- Тестовые данные (валюты, курсы, клиенты, счета, транзакции)"
            )
            self.add_log("Схема БД создана с тестовыми данными")

        except FileNotFoundError:
            QMessageBox.critical(self, "Ошибка", "Файл database_schema.sql не найден")
            self.add_log("Ошибка: файл схемы не найден")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать схему:\n{str(e)}")
            self.add_log(f"Ошибка создания схемы: {e}")

    def drop_schema(self):
        reply = QMessageBox.question(
            self,
            "Подтверждение удаления схемы",
            "Вы уверены, что хотите удалить схему bank_system?\n\n"
            "Это действие:\n"
            "• Удалит ВСЕ таблицы и данные в схеме bank_system\n"
            "• Удалит пользовательские типы (ENUM)\n"
            "• Не может быть отменено!\n\n"
            "Продолжить?",
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
                        "Для создания новой схемы нажмите 'Создать схему и таблицы'."
                    )
                    self.add_log("Схема bank_system удалена")
                else:
                    QMessageBox.warning(
                        self,
                        "Предупреждение",
                        "Не удалось удалить схему bank_system"
                    )
                    self.add_log("Предупреждение: не удалось удалить схему")
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Ошибка",
                    f"Не удалось удалить схему:\n{str(e)}"
                )
                self.add_log(f"Ошибка удаления схемы: {e}")

    def show_insert_dialog(self):
        if not self.is_connected:
            QMessageBox.warning(self, "Предупреждение", "Нет подключения к базе данных")
            return

        dialog = AddDataDialog(self, self.db_manager, self.add_log)
        dialog.exec()

    def show_view_dialog(self):
        if not self.is_connected:
            QMessageBox.warning(self, "Предупреждение", "Нет подключения к базе данных")
            return

        dialog = ViewDataDialog(self, self.db_manager)
        dialog.exec()

    def show_alter_table_dialog(self):
        if not self.is_connected:
            QMessageBox.warning(self, "Предупреждение", "Нет подключения к базе данных")
            return

        dialog = AlterTableDialog(self, self.db_manager)
        dialog.exec()
        self.add_log("Открыто окно изменения структуры таблиц")

    def show_advanced_select_dialog(self):
        if not self.is_connected:
            QMessageBox.warning(self, "Предупреждение", "Нет подключения к базе данных")
            return

        dialog = AdvancedSelectDialog(self, self.db_manager)
        dialog.exec()
        self.add_log("Открыто окно расширенного SELECT")

    def show_text_search_dialog(self):
        if not self.is_connected:
            QMessageBox.warning(self, "Предупреждение", "Нет подключения к базе данных")
            return

        dialog = TextSearchDialog(self, self.db_manager)
        dialog.exec()
        self.add_log("Открыто окно поиска по тексту")

    def show_similar_to_dialog(self):
        if not self.is_connected:
            QMessageBox.warning(self, "Предупреждение", "Нет подключения к базе данных")
            return

        dialog = SimilarToDialog(self, self.db_manager)
        dialog.exec()
        self.add_log("Открыто окно поиска SIMILAR TO")

    def show_aggregation_dialog(self):
        if not self.is_connected:
            QMessageBox.warning(self, "Предупреждение", "Нет подключения к базе данных")
            return

        dialog = AggregationDialog(self, self.db_manager)
        dialog.exec()
        self.add_log("Открыто окно агрегирования")

    def show_string_functions_dialog(self):
        if not self.is_connected:
            QMessageBox.warning(self, "Предупреждение", "Нет подключения к базе данных")
            return

        dialog = StringFunctionsDialog(self, self.db_manager)
        dialog.exec()
        self.add_log("Открыто окно функций работы со строками")

    def show_join_wizard_dialog(self):
        if not self.is_connected:
            QMessageBox.warning(self, "Предупреждение", "Нет подключения к базе данных")
            return

        dialog = JoinWizardDialog(self, self.db_manager)
        dialog.exec()
        self.add_log("Открыт мастер соединений таблиц")

    def show_subquery_filter_dialog(self):
        if not self.is_connected:
            QMessageBox.warning(self, "Предупреждение", "Нет подключения к базе данных")
            return

        dialog = SubqueryFilterDialog(self, self.db_manager)
        dialog.exec()
        self.add_log("Открыто окно фильтров подзапросов")

    def show_custom_types_dialog(self):
        if not self.is_connected:
            QMessageBox.warning(self, "Предупреждение", "Нет подключения к базе данных")
            return

        dialog = CustomTypesDialog(self, self.db_manager)
        dialog.exec()
        self.add_log("Открыто окно управления типами данных")

    def add_log(self, message: str):
        self.log_text.append(f"• {message}")

    def closeEvent(self, event):
        if self.db_manager:
            self.db_manager.disconnect()
        self.logger.info("Application closed")
        event.accept()


def main():
    app = QApplication(sys.argv)

    app.setStyleSheet("""
        QMainWindow {
            background-color: #F5F5F5;
        }
        QLabel {
            color: #333333;
        }
    """)

    window = BankSystemApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()