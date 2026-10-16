import sys
import sqlite3
import urllib.parse
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLineEdit, QPushButton, QTabWidget, QMessageBox)
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
from PyQt6.QtWebEngineWidgets import QWebEngineView

DB_PATH = "browser_history.db"

def init_history_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def log_url_history(url_str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO history (url) VALUES (?)", (url_str,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[-] History failure: {e}")

class PhishingDetector:
    def __init__(self):
        self.flagged_terms = ["verify", "login", "secure", "update", "banking", "signin"]

    def evaluate(self, url_str: str) -> tuple[bool, str]:
        try:
            parsed = urllib.parse.urlparse(url_str)
            domain = parsed.netloc.lower()
            if not domain:
                return False, "Safe"
            segments = domain.split('.')
            if len(segments) > 4:
                return True, f"Deceptive Domain: Too many segments ({len(segments)} subdomains)."
            for word in self.flagged_terms:
                if word in segments[:-2]:
                    return True, f"Security Warning: Keyword '{word}' found in domain routing."
            return False, "Safe"
        except Exception as e:
            return True, f"URL Parsing Error: {str(e)}"

class ActiveSecureBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Apex Core Workstation (Cloudflare Privacy Locked)")
        self.resize(1280, 800)

        self.detector = PhishingDetector()
        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies)

        browser_layout = QVBoxLayout()
        navigation_bar = QHBoxLayout()

        self.btn_back = QPushButton("◀")
        self.btn_back.clicked.connect(self.go_back)
        self.btn_forward = QPushButton("▶")
        self.btn_forward.clicked.connect(self.go_forward)
        self.btn_reload = QPushButton("⟳")
        self.btn_reload.clicked.connect(self.reload_page)
        
        self.address_bar = QLineEdit()
        self.address_bar.setStyleSheet("padding: 5px; font-family: monospace; font-size: 13px;")
        self.address_bar.returnPressed.connect(self.navigate_input)
        
        self.btn_new_tab = QPushButton("＋ New Tab")
        self.btn_new_tab.clicked.connect(lambda: self.add_browser_tab("https://duckduckgo.com"))

        navigation_bar.addWidget(self.btn_back)
        navigation_bar.addWidget(self.btn_forward)
        navigation_bar.addWidget(self.btn_reload)
        navigation_bar.addWidget(self.address_bar)
        navigation_bar.addWidget(self.btn_new_tab)
        browser_layout.addLayout(navigation_bar)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_browser_tab)
        self.tabs.currentChanged.connect(self.update_address_bar_display)
        browser_layout.addWidget(self.tabs)

        container = QWidget()
        container.setLayout(browser_layout)
        self.setCentralWidget(container)

        self.add_browser_tab("https://duckduckgo.com")

    def add_browser_tab(self, url_str: str):
        web_view = QWebEngineView()
        web_page = QWebEnginePage(self.profile, web_view)
        web_view.setPage(web_page)
        
        web_page.urlChanged.connect(self.process_url_change)
        web_page.titleChanged.connect(lambda title: self.update_tab_title(web_view, title))
        
        index = self.tabs.addTab(web_view, "Loading...")
        self.tabs.setCurrentIndex(index)
        web_view.load(QUrl(url_str))

    def close_browser_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            self.close()

    def update_tab_title(self, view, title):
        index = self.tabs.indexOf(view)
        if index != -1:
            self.tabs.setTabText(index, title[:15] + "..." if len(title) > 15 else title)

    def navigate_input(self):
        target = self.address_bar.text().strip()
        if not target: return
        if not (target.startswith("http://") or target.startswith("https://")):
            target = "https://" + target
            
        current_view = self.tabs.currentWidget()
        if current_view:
            is_bad, message = self.detector.evaluate(target)
            if is_bad:
                self.trigger_alert(target, message)
            else:
                current_view.load(QUrl(target))

    def process_url_change(self, qurl: QUrl):
        url_str = qurl.toString()
        current_view = self.tabs.currentWidget()
        
        is_bad, message = self.detector.evaluate(url_str)
        if is_bad:
            if current_view: current_view.stop()
            self.trigger_alert(url_str, message)
            return

        if "duckduckgo.com" not in url_str:
            log_url_history(url_str)
        self.update_address_bar_display()

    def update_address_bar_display(self):
        current_view = self.tabs.currentWidget()
        if current_view:
            self.address_bar.setText(current_view.url().toString())

    def trigger_alert(self, url, info):
        QMessageBox.critical(self, "Threat Blocked", f"Heuristic Threat Intercepted!\n\nReason: {info}\nTarget: {url}")
        current_view = self.tabs.currentWidget()
        if current_view:
            current_view.load(QUrl("https://duckduckgo.com"))

    def go_back(self):
        cv = self.tabs.currentWidget()
        if cv: cv.back()
    def go_forward(self):
        cv = self.tabs.currentWidget()
        if cv: cv.forward()
    def reload_page(self):
        cv = self.tabs.currentWidget()
        if cv: cv.reload()

if __name__ == "__main__":
    init_history_db()
    
    # FORCES CLOUDFLARE DNS IN CORES
    sys.argv.append("--built-in-dns-lookup-enabled")
    sys.argv.append("--dns-server=1.1.1.1,1.0.0.1")
    
    app = QApplication(sys.argv)
    browser = ActiveSecureBrowser()
    browser.show()
    sys.exit(app.exec())
