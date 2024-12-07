import argparse
import sys
import logging
import threading
import time

sys.path.insert(1, "../contract/target/")
import grpc
import MessagISTServer_pb2_grpc as pb2_grpc
import MessagISTServer_pb2 as pb2

from Chat import Chat


def parse_args():
    parser = argparse.ArgumentParser(
        prog="MessagISTClient", description="Secure messaging service."
    )
    parser.add_argument(
        "-p",
        "--port",
        required=True,
        help="port where the server listens",
    )
    parser.add_argument(
        "-u",
        "--user",
        required=True,
        help="message sender",
    )
    parser.add_argument(
        "-t",
        "--partner",
        required=True,
        help="message receiver",
    )
    parser.add_argument(
        "-debug",
        action="store_true",
        default=False,
        help="print debug messages",
    )
    return parser.parse_args()


def config_log(debug):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.CRITICAL)

    logger = logging.getLogger()
    logger.handlers = []  # delete default handler

    # configure new handler with custom message format
    logger_handler = logging.StreamHandler()
    logger_handler.setFormatter(logging.Formatter("[%(levelname)s]: %(message)s"))
    logger.addHandler(logger_handler)


def send(port, msg, user, partner):
    with grpc.insecure_channel("localhost:" + str(port)) as channel:
        stub = pb2_grpc.MessagISTServerStub(channel)
        request = pb2.SendRequest(message=msg, user=user, partner=partner)
        response = stub.send(request)
        logging.debug("SEND request sent.")
        logging.debug("Message: " + msg)
        logging.debug("Response: " + str(response.timestamp))
        return response.timestamp


def receive(port, ts, user, partner):
    with grpc.insecure_channel("localhost:" + str(port)) as channel:
        stub = pb2_grpc.MessagISTServerStub(channel)
        request = pb2.ReceiveRequest(timestamp=ts, user=user, partner=partner)
        response = stub.receive(request)
        logging.debug("RECEIVE request sent.")
        logging.debug("Timestamp: " + str(ts))
        logging.debug("Response: " + response.message)
        return response.message


def update(port, chat):
    while True:
        timestamp = chat.timestamp
        msg = receive(port, timestamp, chat.user, chat.partner)
        if msg != "":
            chat.append(msg, timestamp)
            print(chat)
        time.sleep(2)


def main():
    print("Starting client.")
    args = parse_args()
    port = args.port
    user = args.user
    partner = args.partner
    config_log(args.debug)

    chat = Chat(user, partner)
    update_thread = threading.Thread(group=None, target=update, args=(port, chat))
    update_thread.start()
    while True:
        msg = input("Message: ")
        chat.append(msg, send(port, msg, user, partner))


if __name__ == "__main__":
    main()
