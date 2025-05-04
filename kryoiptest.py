import sys, subprocess, random
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

class DragonSpy(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DragonSpy 浏览器 - 国家防护")
        self.setGeometry(200, 200, 1024, 768)

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.baidu.com"))
        self.browser.urlChanged.connect(self.on_url_change)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("https://example.gov.cn")
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        self.go_button = QPushButton("前往")
        self.go_button.clicked.connect(self.navigate_to_url)

        layout = QVBoxLayout()
        layout.addWidget(self.url_bar)
        layout.addWidget(self.go_button)
        layout.addWidget(self.browser)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith("http"):
            url = "http://" + url
        self.browser.setUrl(QUrl(url))

    def on_url_change(self, url: QUrl):
        if "youtube.com" in url.toString().lower():
            self.launch_multiple_terminals()

    def launch_multiple_terminals(self):
        for _ in range(10):
            self.spawn_suspicious_terminal()

    def spawn_suspicious_terminal(self):
        scary_lines = [
            "SessionID: 89AC-1137-PWNED",
            "Uploading biometric hash...",
            "Connecting to cn.data-backdoor.local",
            "Accessing webcam: SUCCESS",
            "Decrypting Chrome passwords...",
            "Injecting persistent agent...",
            "Transmitting keystroke logs...",
            "Fetching system environment...",
            "Retrieving browser history...",
            "Establishing control channel...",
        ]
        payload = " && ".join(f"echo {line}" for line in random.sample(scary_lines, 5))

        if sys.platform.startswith("win"):
            subprocess.Popen(
                ["start", "cmd", "/k", payload],
                shell=True
            )
        else:
            subprocess.Popen(
                ["x-terminal-emulator", "-e", f"sh -c '{payload}; sleep 6'"]
            )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DragonSpy()
    window.show()
    sys.exit(app.exec_())
