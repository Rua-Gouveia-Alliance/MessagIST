package pt.tecnico.sirs.a61;

import pt.tecnico.sirs.a61.MessagISTServerService;
import pt.tecnico.sirs.a61.MessagISTServerServiceGrpc;
import io.grpc.stub.StreamObserver;
import java.util.Vector;

public class MessagISTServerServiceImpl
        extends MessageISTServerServiceGrpc.MessageISTServerServiceImplBase {
    private Vector<String> _chat;

    @Override
    public void send(MessagISTServerService.SendRequest request,
            StreamObserver<MessagISTServerService.SendResponse> responseObserver) {

        String message = request.getMessage();
        _chat.add(message);
        Integer timestamp = _chat.size() - 1;

        MessagISTServerService.SendResponse response =
                MessageISTServerService.SendResponse.newBuilder().setTimestamp(timestamp).build();

        responseObserver.onNext(response);
        responseObserver.onCompleted();
    }

    @Override
    public void receive(MessagISTServerService.ReceiveRequest request,
            StreamObserver<MessagISTServerService.ReceiveResponse> responseObserver) {

        Integer timestamp = request.getTimestamp();
        String message = timestamp < _chat.size() ? _chat.elementAt(timestamp) : "";

        MessagISTServerService.SendResponse response =
                MessageISTServerService.SendResponse.newBuilder().setResponse(message).build();

        responseObserver.onNext(response);
        responseObserver.onCompleted();
    }
}
