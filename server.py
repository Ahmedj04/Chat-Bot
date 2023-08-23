from concurrent import futures

import grpc
import time

import proto.chat_pb2 as chat
import proto.chat_pb2_grpc as rpc

class ChatServer(rpc.ChatServerServicer):  # inheriting here from the protobuf rpc file which is generated

    def __init__(self):
        # List with all the chat history
        self.chats = []

    # The stream which will be used to send new messages to clients
    def ChatStream(self, request_iterator, context):
        """
        This is a response-stream type call. This means the server can keep sending messages
        Every client opens this connection and waits for server to send new messages

        :param request_iterator:
        :param context:
        :return:
        """
        lastindex = 0
        # For every client a infinite loop starts (in gRPC's own managed thread)
        while True:
            # Check if there are any new messages
            while len(self.chats) > lastindex:
                n = self.chats[lastindex]
                lastindex += 1
                yield n
    
    # def SendNote(self, request: chat.Note, context):
        print("[{}] {}".format(request.name, request.message))
        
        client_message = request.message  # Get the client's message
        
        response_message = f"Hi, {request.name}! You said: {client_message}"
        response_note = chat.Note(name="Server", message=response_message)  # Create a Note message
        self.chats.append(request)  # Add the client's message to the chat history
        self.chats.append(response_note)  # Add the response to the chat history
        
        return response_note  # Respond with the combined message
    
    def SendNote(self, request: chat.Note, context):
        client_message = request.message.lower()  # Get the client's message in lowercase
        
        if "hi" in client_message:
            response_message = f"Hello, {request.name}!"
        elif "how is the weather" in client_message:
            response_message = "The weather is good!"
        else:
            response_message = "I'm sorry, I don't understand."
        
        response_note = chat.Note(name="Server", message=response_message)  # Create a Note message
        self.chats.append(request)  # Add the client's message to the chat history
        self.chats.append(response_note)  # Add the response to the chat history
        
        return response_note  # Respond with the appropriate message


if __name__ == '__main__':
    port = 11912  # a random port for the server to run on
    # the workers is like the amount of threads that can be opened at the same time, when there are 10 clients connected
    # then no more clients able to connect to the server.
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))  # create a gRPC server
    rpc.add_ChatServerServicer_to_server(ChatServer(), server)  # register the server to gRPC
    # gRPC basically manages all the threading and server responding logic, which is perfect!
    print('Starting server. Listening...')
    server.add_insecure_port('[::]:' + str(port))
    server.start()
    # Server starts in background (in another thread) so keep waiting
    # if we don't wait here the ma  in thread will end, which will end all the child threads, and thus the threads
    # from the server won't continue to work and stop the server
    while True:
        time.sleep(64 * 64 * 100)
