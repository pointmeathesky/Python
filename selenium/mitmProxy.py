from mitmproxy import http

url = ""
file_name = "packets.txt"


def start(flow):
    global url
    url = flow.server.config.get("url")
    # overwrite the file so that the only input is from this instance of the program running
    with open(file_name, "w") as file:
        pass


def request(flow: http.HTTPFlow) -> None:
    global url
    # global inputs
    # Check if the request is going to the target website
    # if flow.request.content and inputs.encode() in flow.request.content:
    if url in flow.request.pretty_host:
        print(flow.request.content)
        with open(file_name, "a") as file:
            file.write(flow.request.content.decode(errors="ignore"))
            file.write("\n\n")


def response(flow: http.HTTPFlow) -> None:
    global url
    if url in flow.request.pretty_host:
        print(flow.response.content)
        with open(file_name, "a") as file:
            file.write(flow.response.content.decode(errors="ignore"))
            file.write("\n\n")


