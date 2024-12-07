package pt.tecnico.sirs.a61;

import io.grpc.Server;
import io.grpc.ServerBuilder;
import io.grpc.BindableService;
import java.io.IOException;
import java.lang.InterruptedException;

/**
 * MessageIST server.
 */
public class MessagISTServer {
    // static final Logger logger = new Logger();

    public static void main(String[] args) throws IOException, InterruptedException {
        if (args.length != 1 && args.length != 2) {
            System.err.println("Wrong number of arguments.");
            System.err.println("Usage: mvn exec:java -Dexec.args=<port> [-debug]");
            return;
        }

        // logger.setDebug(args.length == 2 && args[1].equals("-debug"));

        // receive and print arguments
        // logger.debugMessage("Received %d arguments", args.length);
        for (int i = 0; i < args.length; i++) {
            // logger.debugMessage("arg[%d] = %s", i, args[i]);
        }

        final Integer port = Integer.parseInt(args[0]);
        startServer(port);
    }

    private static void startServer(int port) throws IOException, InterruptedException {
        final BindableService impl = new MessagISTServerServiceImpl();

        // create new server
        Server server = ServerBuilder.forPort(port).addService(impl).build();
        // loger.debugMessage("Successful bind to port " + port);

        // start the server
        try {
            server.start();
        } catch (IOException e) {
            System.err.println(e.toString());
            System.err.println("Port already in use!");
            System.out.println("Exiting...");
            System.exit(0);
        }

        // logger.log("Server started");

        // wait until server is terminated
        // logger.debugMessage("Waiting...");
        server.awaitTermination();
    }
}
