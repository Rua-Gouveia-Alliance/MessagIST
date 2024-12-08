import argparse
from ChatManager import ChatManager
from SessionManager import SessionManager
from MessagISTContext import MessagISTContext


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
        "-debug",
        action="store_true",
        default=False,
        help="print debug messages",
    )
    return parser.parse_args()


def main():
    print("Starting client.")
    args = parse_args()
    ctx = MessagISTContext(args.debug, args.port)

    print("1 - Sign Up")
    print("2 - Login")
    opt = input()
    while opt != "1" and opt != "2":
        opt = input()

    sessionManager = SessionManager(ctx)
    username = input("Username: ")
    password = input("Password: ")
    if opt == "1":
        while not sessionManager.signup(username, password):
            print("Signup failed.")
            username = input("Username: ")
            password = input("Password: ")

    while not sessionManager.login(username, password):
        print("Login failed.")
        username = input("Username: ")
        password = input("Password: ")

    chatManager = ChatManager(ctx)
    while True:
        print("1 - Send Message")
        print("2 - Read Chat")
        opt = input()
        while opt != "1" and opt != "2":
            opt = input()

        partner = input("Partner username: ")
        if opt == "1":
            msg = input("Message: ")
            chatManager.sendMessage(msg, partner)
        elif partner in chatManager.chats:
            print(chatManager.chats[partner])


if __name__ == "__main__":
    main()
