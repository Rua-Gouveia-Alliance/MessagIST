import argparse
import sys
import logging
from concurrent import futures

from MessagISTServerServiceImpl import MessagISTServerServiceImpl

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
    logger.handlers = []  # delete default handler

    # configure new handler with custom message format
    logger_handler = logging.StreamHandler()
    logger_handler.setFormatter(logging.Formatter("[%(levelname)s]: %(message)s"))
    logger.addHandler(logger_handler)


def main():
    print("Starting server.")
    args = parse_args()
    port = args.port
    config_log(args.debug)
    try:
        # set up server
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
        pb2_grpc.add_MessagISTServerServicer_to_server(
            MessagISTServerServiceImpl(), server
        )
        server.add_insecure_port("localhost:" + str(port))
        logging.debug("Listening on port " + str(port))

        # start server and wait for termination
        server.start()
        server.wait_for_termination()

    except KeyboardInterrupt:
        print("Stopping server.")
        exit(0)


if __name__ == "__main__":
    main()
