import sys
import subprocess
import requests
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import *


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl('https://google.com'))
        self.setCentralWidget(self.browser)
        self.showMaximized()

        # navbar
        navbar = QToolBar()
        self.addToolBar(navbar)

        back_btn = QAction('Back', self)
        back_btn.triggered.connect(self.browser.back)
        navbar.addAction(back_btn)

        forward_btn = QAction('Forward', self)
        forward_btn.triggered.connect(self.browser.forward)
        navbar.addAction(forward_btn)

        reload_btn = QAction('Reload', self)
        reload_btn.triggered.connect(self.browser.reload)
        navbar.addAction(reload_btn)

        home_btn = QAction('Home', self)
        home_btn.triggered.connect(self.nav_home)
        navbar.addAction(home_btn)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.nav_to_url)
        navbar.addWidget(self.url_bar)

        self.browser.urlChanged.connect(self.update_url)

        settings_btn = QAction('Settings', self)
        navbar.addAction(settings_btn)

        # Create a menu and add actions to it
        settings_menu = QMenu(self)
        info_btn = QAction('Info', self)
        check_updates_btn = QAction('Check For Updates', self)
        close_btn = QAction('Close', self)

        # Add actions to the Settings menu
        settings_menu.addAction(info_btn)
        settings_menu.addAction(check_updates_btn)
        settings_menu.addAction(close_btn)

        # Show the Settings menu when the button is clicked
        settings_btn.triggered.connect(lambda: self.show_settings_menu(navbar, settings_menu, settings_btn))

        # Connect actions to functions
        info_btn.triggered.connect(self.show_info)
        check_updates_btn.triggered.connect(self.check_updates)
        close_btn.triggered.connect(self.close)

    def show_settings_menu(self, navbar, settings_menu, settings_btn):
        # Get the widget associated with the Settings button
        button_widget = navbar.widgetForAction(settings_btn)

        if button_widget:
            # Get the position of the button widget relative to the toolbar
            button_pos = navbar.mapToGlobal(button_widget.geometry().bottomLeft())
            # Show the menu, aligned with the bottom of the button
            settings_menu.exec_(button_pos)

    def get_current_version(self):
        try:
            # Run the Git command to get the latest tag (version)
            result = subprocess.run(['git', 'describe', '--tags'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.stdout.decode('utf-8').strip()  # Get the tag from Git
        except Exception as e:
            print(f"Error getting Git version: {e}")
            return "Unknown"  # Return "Unknown" if Git tag can't be determined

    def get_latest_version_from_github(self):
        try:
            # Fetch the latest release version from your GitHub repository
            url = 'https://api.github.com/repos/AmmoDev0/DevSearch/releases/latest'  # Update with your repo URL
            response = requests.get(url)
            response.raise_for_status()  # Check if the request was successful
            data = response.json()
            return data['tag_name']  # 'tag_name' contains the latest release tag
        except requests.exceptions.RequestException as e:
            print(f"Error fetching latest version: {e}")
            return "Unknown"  # Return "Unknown" if there's an error with the API request

    def check_updates(self):
        current_version = self.get_current_version()
        latest_version = self.get_latest_version_from_github()

        if current_version < latest_version:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText(f"New update available! (v{latest_version})\n\n"
                        "Please visit the official GitHub page to download the latest version.")
            msg.setWindowTitle("Update Available")
            msg.exec_()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText(f"You are using the latest version ({current_version}) of DevSearch.")
            msg.setWindowTitle("No Updates")
            msg.exec_()
    
    def show_info(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(
        "DevSearch v0.2\n\n"
        "What's New:\n"
        "- Improved user interface for better navigation and ease of use\n"
        "- Enhanced browser functionality with faster loading times\n\n"
        "Bug Fixes:\n"
        "- Fixed minor UI glitches on the homepage\n"
        "- Resolved issues with URL bar input lag"
    )
        msg.setWindowTitle("Info")
        msg.exec_()  

    def get_current_version(self):
        # Read the current version from the version.txt file
        try:
            with open('version.txt', 'r') as f:
                return f.read().strip()  # Strip to remove any extra whitespace
        except FileNotFoundError:
            return "Unknown"  # Return "Unknown" if the file is not found

    def check_updates(self):
        current_version = self.get_current_version()
        latest_version = "0.2"

        if current_version < latest_version:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText(f"New update available! (v{latest_version})\n\n"
                        "Please visit the official website to download the latest version.")
            msg.setWindowTitle("Update Available")
            msg.exec_()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText(f"You are using the latest version ({current_version}) of DevSearch.")
            msg.setWindowTitle("No Updates")
            msg.exec_()

    def nav_home(self):
        self.browser.setUrl(QUrl('https://google.com'))

    def nav_to_url(self):
        url = self.url_bar.text()
        self.browser.setUrl(QUrl(url))

    def update_url(self, q):
        self.url_bar.setText(q.toString())


app = QApplication(sys.argv)
QApplication.setApplicationName('DevSearch')
window = MainWindow()
app.exec_()