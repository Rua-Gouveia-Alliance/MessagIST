import argparse
import sys
import logging
import os
from concurrent import futures

from KeyServerServiceImpl import KeyServerServiceImpl
from database.DatabaseClass import DatabaseClass

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(1, "../contract/target/")
import grpc
import KeyServer_pb2_grpc as pb2_grpc


def parse_args():
    parser = argparse.ArgumentParser(
        prog="KeyServer",
        description="Server for managing MessagIST client's public keys and chat salts.",
    )
    parser.add_argument(
        "-p",
        "--port",
        required=True,
        help="port where the server listens",
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
    port = args.port
    # Provavelmente passar o path das cenas no comando
    config_log(args.debug)
    try:
        # Initialize DB
        DB = DatabaseClass(dbname="test", user="postgres", password="sirs")

        DB.connect()
        DB.execute_script("../database/keyserverschema.sql")

        # TODO: Aumentar thread pool para 10, depois de locks nos managers.
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
        pb2_grpc.add_KeyServerServicer_to_server(KeyServerServiceImpl(DB), server)

        # GRPS WITH TLS
        server_key_path = "keys/server.key"
        server_cert_path = "keys/server.crt"

        server_cert = open(server_cert_path, "rb").read()
        server_key = open(server_key_path, "rb").read()
        server_credentials = grpc.ssl_server_credentials([(server_key, server_cert)])

        server.add_secure_port("localhost:" + str(port), server_credentials)
        logging.debug("Listening on port " + str(port))

        # start server and wait for termination
        server.start()
        server.wait_for_termination()

    except KeyboardInterrupt:
        print("Stopping server.")
        exit(0)

    finally:
        DB.close()


if __name__ == "__main__":
    main()
