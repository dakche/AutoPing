import serial
import serial.tools.list_ports
import sys
import discord
import threading, asyncio
from time import sleep

from PyQt5.QtCore import QSize, Qt, pyqtSignal, QObject, QTimer, QThread
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtWidgets import (
    QApplication,
    QPushButton,
    QLabel,
    QMainWindow,
    QGridLayout,
    QWidget,
    QComboBox,
    QVBoxLayout,
    QHBoxLayout,
    QToolButton,
)

# Discord Bot token and channel ID
TOKEN = "YOUR TOKEN HERE"
ID = "YOUR CHANNEL ID HERE"

# Start discord
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

# Place employee discord usernames here
employees = ["hackedgnu", "hackdun"]

# Discord client loop
discord_loop = None

# GUI function (thread #1)
class MainWindow(QMainWindow):
    def __init__(self, refresh_interval_ms = 1000):
        super().__init__()
        self.ports = []
        self.setWindowTitle("AutoPing Companion")
        self._central = QWidget()
        self.setCentralWidget(self._central)
        self._layout = QVBoxLayout(self._central)
        self.setWindowIcon(QIcon("psocmemes.png"))
        self._central.setContentsMargins(200, 200, 200, 200)
        self._current_ports = []

        self._timer = QTimer(self)
        self._timer.setInterval(refresh_interval_ms)  # 1 second by default
        self._timer.timeout.connect(self._update_port_list)
        self._timer.start()

        self.countdown_count = 3
        self.countdown_timer = QTimer(self)
        self.countdown_timer.setInterval(refresh_interval_ms)
        self.countdown_timer.timeout.connect(self.drawNumbers)
        self.countdown_timer.stop()

        self.show_connect()

    # PSoC response handler
    def process(self, msg):
        if (msg == "Call"):
            self.colorbox.setStyleSheet("background-color:#ff0000;")
            self.countdown_timer.start()
            self.drawNumbers()
            self.repaint()
            self.abort_button.setEnabled(True)
        else:
            self.colorbox.setStyleSheet("background-color:#00ff00;")
            self.label.setText("Ready")
            self.abort_button.setEnabled(False)
            self.repaint()
    
    # Draw the countdown timer
    def drawNumbers(self):
        if (self.countdown_count == 0):
            self.label.setText("Calling")
            self.countdown_timer.stop()
            self.countdown_count = 3
            send(employees[1], "Go to work!")
        else:
            self.label.setText(str(self.countdown_count))
            self.countdown_count -= 1
        
    # Scan the connected USB devices
    def _update_port_list(self, ):
        self.ports = [x.name for x in serial.tools.list_ports.comports()]

        # Only touch UI when there is a change (avoids flicker)
        if self.ports != self._current_ports:
            self._current_ports = self.ports
            self.selection.clear()
            self.selection.addItems(self._current_ports)

    # Splash screen
    def show_connect(self):
        self._clear_layout()

        logo = QLabel()
        pixmap = QPixmap("psocmemes.png").scaled(512, 512)
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignHCenter)

        title = QLabel("Connect to AutoPing!")
        title.setAlignment(Qt.AlignHCenter)
        font = title.font()
        font.setPointSize(20)
        font.setBold(True)
        title.setFont(font)

        tools = QWidget()
        tools_layout = QHBoxLayout()
        tools.setLayout(tools_layout)

        spec = QLabel("Select Port:")
        spec.setMaximumWidth(135)
        tools_layout.addWidget(spec)        

        self.selection = QComboBox()
        self.selection.clearEditText()
        self.selection.addItems(self.ports)
        self.selection.setFixedHeight(55)
        tools_layout.addWidget(self.selection)

        nextButton = QPushButton("Next ->")
        nextButton.clicked.connect(self.connect)
        nextButton.setMaximumWidth(200)
        tools_layout.addWidget(nextButton)

        self.error = QLabel()
        self.error.setAlignment(Qt.AlignHCenter)
    
        self._layout.addWidget(logo)
        self._layout.addWidget(title)
        self._layout.addWidget(tools)
        self._layout.addWidget(self.error)

    # Handles the COM port form on the splash screen
    def connect(self):
        ser = self.selection.currentText()
        if (ser != ''):
            self.thread = SerialReaderThread(ser)
            self.thread.data_received.connect(self.process)
            self.thread.start()
            self.main_app()
        else:
            self.error.setText("Please select a valid port")

    # Main application with the color indicator
    def main_app(self):
        self._clear_layout()

        self.colorbox = QWidget()
        self.colorbox_layout = QVBoxLayout()
        self.colorbox_layout.setAlignment(Qt.AlignHCenter)
        self.colorbox.setMinimumHeight(300)
        self.colorbox.setStyleSheet("background-color:#00ff00;")
        self.colorbox.setLayout(self.colorbox_layout)

        self.label = QLabel("Ready")
        self.label.setAlignment(Qt.AlignHCenter)
        font = self.label.font()
        font.setPointSize(40)
        font.setBold(True)
        self.label.setFont(font)

        self.abort_button = QPushButton("Abort")
        self.abort_button.clicked.connect(self.cancel)
        self.abort_button.setFixedHeight(150)
        self.abort_button.setFont(QFont('Arial', 30))
        self.abort_button.setEnabled(False)

        disconnect = QPushButton("Close Connection")
        disconnect.clicked.connect(self.closeconnection)

        self._layout.addWidget(self.colorbox)
        self._layout.addWidget(self.label)
        self._layout.addWidget(self.abort_button)
        self._layout.addWidget(disconnect)

    # Abort handler
    def cancel(self):
        self.countdown_timer.stop()
        self.countdown_count = 3
        self.colorbox.setStyleSheet("background-color:#00ff00;")
        self.label.setText("Ready")
        self.abort_button.setEnabled(False)
        self.repaint()

    # Close serial connection
    def closeconnection(self):
        self.thread.close()
        self.show_connect()

    # Helper function, clear layout before new screen is drawn
    def _clear_layout(self):
        """Remove all widgets from the current layout."""
        while self._layout.count():
            item = self._layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()

# Reads from the PSoC (thread #2)
class SerialReaderThread(QThread):
    data_received = pyqtSignal(str)

    def __init__(self, portname):
        super().__init__()
        self.port_name = portname
        self.running = True

    # Monitors the serial connection
    def run(self):
        self.s = serial.Serial(self.port_name, baudrate=115200)
        while(self.running):
            if self.s.in_waiting:
                line = self.s.readline().decode(errors="ignore").strip()
                if line:
                    self.data_received.emit(line)
    
    # Handles closing the serial connection
    def close(self):
        self.running = False
        self.s.close()

# Display a message in terminal when connected to Discord
@client.event
async def on_ready():
    print('Logged on as {0}!'.format(client.user))

# Handles message receipt
@client.event
async def on_message(message):
    # if (message.author != client.user): 
    print('Message from {0.author}: {0.content}'.format(message))

# Async function to send the message to Discord
async def send_msg(usr, msg):
    global ID
    user = discord.utils.get(client.users, name=usr)
    channel = client.get_channel(ID)
    await channel.send(f'{user.mention}: {msg}')

# Helper function to safely send message
def send(usr, msg):
    asyncio.run_coroutine_threadsafe(send_msg(usr, msg), discord_loop)

# Initializes Discord Bot
def msgbot():
    global discord_loop
    discord_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(discord_loop)
    discord_loop.create_task(client.start(TOKEN))
    discord_loop.run_forever()

# Handles the splitting of the threads
def run():
    threading.Thread(target=msgbot, daemon=True).start()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

if __name__ == "__main__":
    run()
    