import argparse
import sys
import logging
import os
from concurrent import futures

from MessagISTServerServiceImpl import MessagISTServerServiceImpl

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.DatabaseClass import DatabaseClass

sys.path.insert(1, "../contract/target/")
import grpc
import MessagISTServer_pb2_grpc as pb2_grpc


def parse_args():
    parser = argparse.ArgumentParser(
        prog="MessagISTServer", description="Secure messaging service."
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
        # TODO: Aumentar thread pool para 10.
        # So nao meto ja porque seria preciso meter locks no ChatManager e
        # UserManager, que vao ser implementados de novo quando tivermos a DB
        # ptt nao faz mto sentido perder temepo com isso agora.

        ##Initialize DB
        DB = DatabaseClass(dbname="test", user="postgres", password="sirs")

        DB.connect()

        DB.execute_script("../database/database.sql")

        server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
        pb2_grpc.add_MessagISTServerServicer_to_server(
            MessagISTServerServiceImpl(DB), server
        )

        # GRPS WITH TLS
        server_key_path = "keys/server.key"
        server_cert_path = "keys/server.crt"

        server_cert = open(server_cert_path, "rb").read()
        server_key = open(server_key_path, "rb").read()
        server_credentials = grpc.ssl_server_credentials([(server_key, server_cert)])

        server.add_secure_port("localhost:" + str(port), server_credentials)

        # server.add_insecure_port(":" + str(port))
        # server.add_insecure_port("localhost:5001")

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
