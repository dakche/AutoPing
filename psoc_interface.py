import serial
import serial.tools.list_ports
import sys
import discord
import threading, asyncio

from PyQt5.QtCore import QSize, Qt, pyqtSignal, QObject, QTimer
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

# TOKEN = "YOUR TOKEN HERE"
# ID = "YOUR CHANNEL ID HERE"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

employees = []
message_queue = asyncio.Queue()

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

        self.show_connect()
        
    def _update_port_list(self, ):
        """Query OS for serial ports and refresh the list when it changes."""
        self.ports = [x.name for x in serial.tools.list_ports.comports()]

        # Only touch UI when there is a change (avoids flicker)
        if self.ports != self._current_ports:
            self._current_ports = self.ports
            self.selection.clear()
            self.selection.addItems(self._current_ports)

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

    def connect(self):
        comport = self.selection.currentText()
        if (comport != ''):
            self.s = serial.Serial(comport)
            self.main_app()
        else:
            self.error.setText("Please select a valid port")

    def main_app(self):
        self._clear_layout()

        self.colorbox = QWidget()
        self.colorbox_layout = QVBoxLayout()
        self.colorbox_layout.setAlignment(Qt.AlignHCenter)
        self.colorbox.setStyleSheet("background-color:#00ff00;")
        self.colorbox.setLayout(self.colorbox_layout)

        self.label = QLabel("Ready")
        self.label.setAlignment(Qt.AlignHCenter)
        font = self.label.font()
        font.setPointSize(40)
        font.setBold(True)
        self.label.setFont(font)

        self.abort_button = QPushButton("Abort")
        self.abort_button.clicked.connect(lambda: self.sendmsg("Go to work!"))
        self.abort_button.setFixedHeight(150)
        self.abort_button.setFont(QFont('Arial', 30))
        #self.abort_button.setEnabled(False)

        disconnect = QPushButton("Close Connection")
        disconnect.clicked.connect(self.closeconnection)

        self._layout.addWidget(self.colorbox)
        self._layout.addWidget(self.label)
        self._layout.addWidget(self.abort_button)
        self._layout.addWidget(disconnect)

    def closeconnection(self):
        self.s.close()
        self.show_connect()

    def sendmsg(self, msg):
        global message_queue
        asyncio.run_coroutine_threadsafe(message_queue.put(msg), client.loop)

    # Helper functions
    def _clear_layout(self):
        """Remove all widgets from the current layout."""
        while self._layout.count():
            item = self._layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()

@client.event
async def on_ready():
    print('Logged on as {0}!'.format(client.user))
    asyncio.create_task(msg_worker())

@client.event
async def on_message(message):
    # if (message.author != client.user): 
    print('Message from {0.author}: {0.content}'.format(message))

async def send_msg(usr, msg):
    global ID
    user = discord.utils.get(client.users, name=usr)
    channel = client.get_channel(ID)
    await channel.send(f'{user.mention}: {msg}')

async def msg_worker():
    global message_queue
    while True:
        message = await message_queue.get()
        await send_msg("hackedgnu", message)

def msgbot():
    client.run(TOKEN)

def run():
    threading.Thread(target=msgbot, daemon=True).start()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

if __name__ == "__main__":
    run()
    