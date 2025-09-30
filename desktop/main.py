import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget, QFileDialog, QLabel, QHBoxLayout, QTableWidget, QTableWidgetItem, QSplitter, QLineEdit, QHeaderView, QToolBar, QAction, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import requests
import pandas as pd
import io

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Reader Desktop")
        self.setGeometry(100, 100, 1300, 750)

        # Toolbar
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        export_action = QAction(QIcon(), "Export to Excel", self)
        export_action.triggered.connect(self.export_to_excel)
        toolbar.addAction(export_action)

        # Main layout
        main_layout = QHBoxLayout()
        splitter = QSplitter(Qt.Horizontal)

        # Left: File upload and Data Table
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        title = QLabel("<h2 style='margin-bottom:10px'>AI Reader - Data Table</h2>")
        left_layout.addWidget(title)
        self.label = QLabel("Upload a PDF or Word file:")
        left_layout.addWidget(self.label)
        self.upload_btn = QPushButton("Select File")
        self.upload_btn.clicked.connect(self.open_file_dialog)
        left_layout.addWidget(self.upload_btn)
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("QTableWidget {gridline-color: #b0b0b0; font-size: 13px;} QHeaderView::section {background-color: #e0e0e0; font-weight: bold;}")
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectItems)
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)
        self.table.setSortingEnabled(True)
        left_layout.addWidget(self.table)
        left_widget.setLayout(left_layout)

        # Right: Chat box
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("<h2>AI Chat</h2>"))
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        right_layout.addWidget(self.chat_display)
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Ask a question about the data...")
        self.chat_input.returnPressed.connect(self.send_chat)
        right_layout.addWidget(self.chat_input)
        right_widget.setLayout(right_layout)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        main_layout.addWidget(splitter)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.data_text = ""
        self.df = None

        # Modern stylesheet
        self.setStyleSheet("""
            QMainWindow { background: #f7f7f7; }
            QPushButton { padding: 6px 16px; font-size: 13px; }
            QLabel { font-size: 13px; }
            QLineEdit { font-size: 13px; padding: 4px; }
            QToolBar { background: #e0e0e0; border-bottom: 1px solid #b0b0b0; }
        """)
    def export_to_excel(self):
        if self.df is not None and not self.df.empty:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Excel File", "", "Excel Files (*.xlsx)")
            if file_path:
                try:
                    self.df.to_excel(file_path, index=False)
                    QMessageBox.information(self, "Export Successful", f"Data exported to {file_path}")
                except Exception as e:
                    QMessageBox.critical(self, "Export Failed", str(e))
        else:
            QMessageBox.warning(self, "No Data", "No data to export.")

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "PDF Files (*.pdf);;Word Files (*.docx)")
        if file_path:
            self.label.setText(f"Selected: {file_path}")
            self.upload_and_extract(file_path)

    def upload_and_extract(self, file_path):
        url = "http://127.0.0.1:8000/extract"
        with open(file_path, "rb") as f:
            # Use os.path.basename for cross-platform compatibility
            filename = os.path.basename(file_path)
            files = {"file": (filename, f)}
            try:
                resp = requests.post(url, files=files)
                if resp.status_code == 200:
                    data = resp.json()
                    self.data_text = data.get("text", "No text extracted.")
                    self.display_table_from_text(self.data_text)
                else:
                    self.table.setRowCount(0)
                    self.table.setColumnCount(1)
                    self.table.setHorizontalHeaderLabels(["Error"])
                    self.table.setItem(0, 0, QTableWidgetItem(resp.text))
            except Exception as e:
                self.table.setRowCount(0)
                self.table.setColumnCount(1)
                self.table.setHorizontalHeaderLabels(["Error"])
                self.table.setItem(0, 0, QTableWidgetItem(str(e)))

    def display_table_from_text(self, text):
        lines = [l for l in text.splitlines() if l.strip()]
        if not lines:
            self.table.setRowCount(0)
            self.table.setColumnCount(1)
            self.table.setHorizontalHeaderLabels(["No Data"])
            self.df = None
            return
        # Try to parse as table with header
        try:
            header = lines[0].split()
            data = [l.split() for l in lines[1:]]
            # Check if all rows have the same number of columns as header
            if all(len(row) == len(header) for row in data):
                self.df = pd.DataFrame(data, columns=header)
                self.table.setColumnCount(len(header))
                self.table.setHorizontalHeaderLabels(header)
                self.table.setRowCount(len(data))
                for row_idx, row in enumerate(data):
                    for col_idx, value in enumerate(row):
                        self.table.setItem(row_idx, col_idx, QTableWidgetItem(value))
                return
        except Exception:
            pass
        # Fallback: show as single column
        self.df = pd.DataFrame({'Extracted Data': lines})
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(["Extracted Data"])
        self.table.setRowCount(len(lines))
        for row_idx, value in enumerate(lines):
            self.table.setItem(row_idx, 0, QTableWidgetItem(value))

    def send_chat(self):
        question = self.chat_input.text().strip()
        if not question:
            return
        self.chat_display.append(f"You: {question}")
        if self.data_text:
            try:
                url = "http://127.0.0.1:8000/chat"
                payload = {"text": self.data_text, "question": question}
                resp = requests.post(url, json=payload)
                if resp.status_code == 200:
                    answer = resp.json().get("answer", "No answer from AI.")
                else:
                    answer = f"Error: {resp.text}"
            except Exception as e:
                answer = f"Request failed: {e}"
        else:
            answer = "No data loaded. Please upload a file first."
        self.chat_display.append(f"AI: {answer}\n")
        self.chat_input.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
