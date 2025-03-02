import os
os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"
from PyQt5.QtCore import QCoreApplication, Qt
QCoreApplication.setAttribute(Qt.AA_UseSoftwareOpenGL)
from PyQt5.QtCore import QCoreApplication, Qt, QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QToolBar, QAction, QLineEdit, QMessageBox, QMenu
from PyQt5.QtWebEngineWidgets import QWebEngineView
import sys
import subprocess
import requests

QCoreApplication.setAttribute(Qt.AA_UseSoftwareOpenGL)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)
        self.showMaximized()
        self.add_new_tab('https://yandex.com')

        # Navbar
        navbar = QToolBar()
        self.addToolBar(navbar)

        back_btn = QAction('Back', self)
        back_btn.triggered.connect(lambda: self.current_browser().back())
        navbar.addAction(back_btn)

        forward_btn = QAction('Forward', self)
        forward_btn.triggered.connect(lambda: self.current_browser().forward())
        navbar.addAction(forward_btn)

        reload_btn = QAction('Reload', self)
        reload_btn.triggered.connect(lambda: self.current_browser().reload())
        navbar.addAction(reload_btn)

        home_btn = QAction('Home', self)
        home_btn.triggered.connect(self.nav_home)
        navbar.addAction(home_btn)

        new_tab_btn = QAction('New Tab', self)
        new_tab_btn.triggered.connect(lambda: self.add_new_tab('https://yandex.com'))
        navbar.addAction(new_tab_btn)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.nav_to_url)
        navbar.addWidget(self.url_bar)

        self.tabs.currentChanged.connect(self.update_url)

        options_menu = QAction('Options', self)
        navbar.addAction(options_menu)

        # Settings menu
        dropdown_menu_options = QMenu(self)
        new_tab_sbtn = QAction('New Tab', self)
        info_btn = QAction('Info', self)
        settings_menu_btn = QAction('Settings', self)
        check_updates_btn = QAction('Check For Updates', self)

        close_btn = QAction('Close', self)
        dropdown_menu_options.addAction(new_tab_sbtn)
        dropdown_menu_options.addAction(info_btn)
        dropdown_menu_options.addAction(check_updates_btn)
        dropdown_menu_options.addAction(settings_menu_btn)
        dropdown_menu_options.addAction(close_btn)
        options_menu.triggered.connect(lambda: self.show_settings_menu(navbar, dropdown_menu_options, options_menu))
        new_tab_sbtn.triggered.connect(lambda: self.add_new_tab('https://yandex.com/'))
        info_btn.triggered.connect(self.show_info)
        check_updates_btn.triggered.connect(self.check_updates)
        settings_menu_btn.triggered.connect(lambda: self.handle_custom_urls('devsearch://settings'))
        close_btn.triggered.connect(self.close)
        self.current_browser().urlChanged.connect(self.handle_custom_urls)

    def handle_custom_urls(self, url):
        if url == "devsearch://settings":
            # Get the absolute path of the directory where the current script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))  
            settings_file = os.path.join(script_dir, 'pages', 'settings.html')
        
            # Check if the file exists before trying to load it
            if os.path.exists(settings_file):
                # Load the settings page using a file URL
                self.add_new_tab(f'file:///{settings_file.replace("\\", "/")}')
            else:
                print(f"Settings file not found at: {settings_file}")

    def add_new_tab(self, url):
        browser = QWebEngineView()
        browser.setUrl(QUrl(url))
        browser.urlChanged.connect(lambda q, browser=browser: self.update_url(q))
        browser.titleChanged.connect(lambda title, browser=browser: self.update_tab_title(browser, title))
        browser.iconChanged.connect(lambda icon, browser=browser: self.update_tab_icon(browser, icon))
        i = self.tabs.addTab(browser, url)
        self.tabs.setCurrentIndex(i)

    def current_browser(self):
        return self.tabs.currentWidget()

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def update_tab_title(self, browser, title):
        index = self.tabs.indexOf(browser)
        if index != -1:
            self.tabs.setTabText(index, title)

    def update_tab_icon(self, browser, icon):
        index = self.tabs.indexOf(browser)
        if index != -1:
            self.tabs.setTabIcon(index, icon)

    def show_settings_menu(self, navbar, dropdown_menu_options, options_menu):
        button_widget = navbar.widgetForAction(options_menu)
        if button_widget:
            button_pos = navbar.mapToGlobal(button_widget.geometry().bottomLeft())
            dropdown_menu_options.exec_(button_pos)

    def get_current_version(self):
        try:
            result = subprocess.run(['git', 'describe', '--tags'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.stdout.decode('utf-8').strip()
        except Exception as e:
            print(f"Error getting Git version: {e}")
            return "Unknown"

    def get_latest_version_from_github(self):
        try:
            url = 'https://api.github.com/repos/AmmoDev0/DevSearch/releases/latest'
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data['tag_name']
        except requests.exceptions.RequestException as e:
            print(f"Error fetching latest version: {e}")
            return "Unknown"

    def check_updates(self):
        current_version = self.get_current_version()
        latest_version = self.get_latest_version_from_github()
        if current_version < latest_version:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText(f"New update available! ({latest_version})\n\nPlease visit the official GitHub page to download it.")
            msg.setWindowTitle("Update Available")
            msg.exec_()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText(f"You are using the latest version ({current_version}).")
            msg.setWindowTitle("No Updates")
            msg.exec_()

    def show_info(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(
            "DevSearch v0.3\n\n"
            "What's New:\n"
            "- Improved UI for better navigation\n"
            "- Enhanced browser functionality\n\n"
            "Bug Fixes:\n"
            "- Fixed minor UI glitches\n"
            "- Resolved URL bar input lag"
        )
        msg.setWindowTitle("Info")
        msg.exec_()

    def nav_home(self):
        self.current_browser().setUrl(QUrl('https://yandex.com'))

    def nav_to_url(self):
        url = self.url_bar.text()
        self.current_browser().setUrl(QUrl(url))

    def update_url(self, index):
        browser = self.current_browser()
        if browser:
            url = browser.url()
            self.url_bar.setText(url.toString())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    QApplication.setApplicationName('DevSearch')
    window = MainWindow()
    app.exec_()
