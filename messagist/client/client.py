import sys

sys.path.append("../util/")
sys.path.append("../contract/target/")

import argparse
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from messagist.MessagIST import MessagIST


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="MessagIST", description="Secure messaging application."
    )
    parser.add_argument(
        "-H",
        "--host",
        default="localhost",
        help="MessagISTServer DMZ IP",
    )
    parser.add_argument(
        "-p",
        "--port",
        #default=5001,
        default=5002,
        help="MessagISTServer DMZ port",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        default=False,
        help="Show debug messages",
    )
    args = parser.parse_args()

    app = QGuiApplication()
    engine = QQmlApplicationEngine()
    messagist = MessagIST(args.debug, args.host, args.port)
    engine.rootContext().setContextProperty("messagist", messagist)
    engine.addImportPath(sys.path[0])
    engine.loadFromModule("ui", "Main")

    if not engine.rootObjects():
        sys.exit(-1)

    ex = app.exec()
    del engine
    messagist.logout()
    sys.exit(ex)
