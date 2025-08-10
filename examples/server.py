# import socket
# from json import dumps

# def run_server():
#     sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
#     sock.bind(("localhost", 8000))
#     sock.listen(1)
#     print("Server is running on http://localhost:8080")

#     while True:
#         conn, addr = sock.accept()
#         request = conn.recv(1024).decode("utf-8")
#         print(f"request: {request}")

#         if "GET" not in request:
#             body = "Method Not Allowed"
#             response = (
#                 "HTTP/1.1 405 Not Allowed\r\n"
#                 "Content-Type: text/plain\r\n"
#                 f"Content-Length: {len(body)}\r\n"
#                 "Connection: close\r\n"
#                 "\r\n"
#                 f"{body}"
#             )
#             conn.sendall(response.encode())
#             conn.close()

#         if "GET /hello" in request:
#             body = "Hello!"
#             response = (
#                 "HTTP/1.1 200 OK\r\n"
#                 "Content-Type: text/plain\r\n"
#                 f"Content-Length: {len(body)}\r\n"
#                 "Connection: close\r\n"
#                 "\r\n"
#                 f"{body}"
#             )
#         elif "GET /bye" in request:
#             body = "Bye!"
#             response = (
#                 "HTTP/1.1 200 OK\r\n"
#                 "Content-Type: text/plain\r\n"
#                 f"Content-Length: {len(body)}\r\n"
#                 "Connection: close\r\n"
#                 "\r\n"
#                 f"{body}"
#             )
#         elif "GET /json" in request:
#             body = dumps({"status": "ok"})
#             response = (
#                 "HTTP/1.1 200 OK\r\n"
#                 "Content-Type: text/plain\r\n"
#                 f"Content-Length: {len(body)}\r\n"
#                 "Connection: close\r\n"
#                 "\r\n"
#                 f"{body}"
#             )
#         else:
#             body = "Not Found"
#             response = (
#                 "HTTP/1.1 404 Not Found\r\n"
#                 "Content-Type: text/plain\r\n"
#                 f"Content-Length: {len(body)}\r\n"
#                 "Connection: close\r\n"
#                 "\r\n"
#                 f"{body}"
#             )
#         conn.sendall(response.encode())
#         conn.close()

# if __name__ == "__main__":
#     run_server()


################################################################################
import json
from http.server import BaseHTTPRequestHandler, HTTPServer


class RequestsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/hello":
            self.respond(200, "Hello!", "text/plain")
        elif self.path == "/bye":
            self.respond(200, "Bye!", "text/plain")
        elif self.path == "/json":
            data = {"status": "ok"}
            self.respond(200, json.dumps(data), "application/json")
        else:
            self.respond(404, "Not Found", "text/plain")

    def respond(self, code, body, content_type):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body.encode())))
        self.end_headers()
        self.wfile.write(body.encode())


server = HTTPServer(("localhost", 8000), RequestsHandler)
server.serve_forever()