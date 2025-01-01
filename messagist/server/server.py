import argparse
import sys
import logging
import os
import grpc
from concurrent import futures
from MessagISTServerServiceImpl import MessagISTServerServiceImpl

sys.path.append("../database/")
sys.path.append("../contract/target/")
import MessagISTServer_pb2_grpc as pb2_grpc
from DatabaseClass import DatabaseClass


def parse_args():
    parser = argparse.ArgumentParser(
        prog="MessagISTServer", description="Secure messaging service."
    )
    parser.add_argument(
        "-p",
        "--port",
        default=5001,
        help="port where the server listens",
    )
    parser.add_argument(
        "-i",
        "--dbip",
        #default="192.168.2.2",
        default = "localhost",
        help="ip of the PostgreSQL DB Server",
    )
    parser.add_argument(
        "-d",
        "--dbport",
        default=5432,
        help="port of the PostgreSQL DB Server",
    )
    parser.add_argument(
        "-u",
        "--dbuser",
        required=True,
        help="username of PostgreSQL user",
    )
    parser.add_argument(
        "-P",
        "--dbpassword",
        required=True,
        help="password of PostgreSQL user",
    )
    parser.add_argument(
        "-n",
        "--dbname",
        default="messagist",
        help="database name of PostgreSQL db",
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
    # Provavelmente passar o path das cenas no comando
    config_log(args.debug)

    # connect to DB
    DB = DatabaseClass(
        dbname=args.dbname,
        user=args.dbuser,
        password=args.dbpassword,
        host=args.dbip,
        port=args.dbport,
    )
    DB.connect()

    try:
        # TODO: Aumentar thread pool para 10.
        # Preciso trocar a maneira como a base de dados funciona.
        # Cada thread tem que ter a sua propria db e a classe da base de dados
        # talvez tenha que ser trocada para ser seguro fazer operacoes concorrentes.

        # initialize DB
        DB.execute_script("../database/serverschema.sql")

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

        server.add_secure_port("localhost:" + str(args.port), server_credentials)
        logging.debug("Listening on port " + str(args.port))

        server.start()
        server.wait_for_termination()

    except KeyboardInterrupt:
        print("Stopping server.")
        exit(0)

    finally:
        DB.close()


if __name__ == "__main__":
    main()
