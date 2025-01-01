import argparse
import sys
import logging
import os
from concurrent import futures


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DmzMainClass import DmzMainClass

sys.path.insert(1, "../contract/target/")
import grpc
import MessagISTServer_pb2_grpc as pb2_grpc


def parse_args():
    parser = argparse.ArgumentParser(
        prog="MessagISTServer", description="Secure messaging service."
    )
    parser.add_argument(
        "-i",
        "--serverip",
        default="localhost",
        #default="192.168.1.1",
        help="ip of the MessagISTServer",
    )
    parser.add_argument(
        "-s",
        "--serverport",
        default=5001,
        help="port of the MessagISTServer",
    )
    parser.add_argument(
        "-p",
        "--port",
        #default=5001,
        default=5002,
        help="port where the DMZ listens",
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
    logger.handlers = []

    logger_handler = logging.StreamHandler()
    logger_handler.setFormatter(logging.Formatter("[%(levelname)s]: %(message)s"))
    logger.addHandler(logger_handler)


def main():
    print("Starting server.")
    args = parse_args()
    config_log(args.debug)

    try:
        # TODO: Aumentar thread pool para 10.
        # Preciso trocar a maneira como a base de dados funciona.
        # Cada thread tem que ter a sua propria db e a classe da base de dados
        # talvez tenha que ser trocada para ser seguro fazer operacoes concorrentes.

        server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
        pb2_grpc.add_MessagISTServerServicer_to_server(
            DmzMainClass(args.serverip, args.serverport), server
        )

        # GRPS WITH TLS
        server_key_path = "keys/server.key"
        server_cert_path = "keys/server.crt"

        server_cert = open(server_cert_path, "rb").read()
        server_key = open(server_key_path, "rb").read()
        server_credentials = grpc.ssl_server_credentials([(server_key, server_cert)])

        server.add_secure_port("localhost:" + str(args.port), server_credentials)

        logging.debug("Listening on port " + str(args.port))

        # start server and wait for termination
        server.start()

        server.wait_for_termination()

    except KeyboardInterrupt:
        print("Stopping server.")
        exit(0)


if __name__ == "__main__":
    main()
