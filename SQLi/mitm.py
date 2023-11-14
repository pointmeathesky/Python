from mitmproxy import http
import zmq
import threading
url = ""
payload = ""
signaled = False

context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.bind("tcp://127.0.0.1:5555")
modified_packets = set()


def start(flow):
    global url
    url = flow.server.config.get("url")


def request(flow: http.HTTPFlow) -> None:
    global url, payload, signaled
    query = flow.request.query
    # check that the other script has signalled to begin altering packets
    if signaled and url in flow.request.pretty_host:
        for key, value in query.items(multi=True):
            # replace the packet value with a SQL payload
            query[key] = payload
        # store the id of modified packet so that it's status code can be sent
        modified_packets.add(flow.id)


def response(flow: http.HTTPFlow) -> None:
    global url, signaled
    query = flow.request.query
    # send the status code of the modified packet back to the other script
    if flow.id in modified_packets:
        status_code = flow.response.status_code
        status_code = str(status_code)
        socket.send_string(status_code)


def receive_payload_from_socket():
    global payload, signaled
    while True:
        msg = socket.recv_string()
        if msg == "stop":
            signaled = False
        else:
            payload = msg
            signaled = True


# Start the socket listening thread
socket_thread = threading.Thread(target=receive_payload_from_socket)
socket_thread.start()
