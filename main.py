import json
import socket
import threading
import datetime
import os
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from pymongo import MongoClient

HTTP_HOST = "0.0.0.0"
HTTP_PORT = 3000
SOCKET_HOST = "0.0.0.0"
SOCKET_PORT = 5000

mongo_host = os.getenv("MONGO_HOST", "mongodb")
client = MongoClient(mongo_host, 27017)
db = client["chat_db"]
collection = db["messages"]

class CustomHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/message":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length).decode("utf-8")

            try:
                data = json.loads(post_data)
            except json.JSONDecodeError:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Invalid JSON")
                return

            username = data.get("username")
            message = data.get("message")

            if username and message:
                msg_data = {
                    "date": datetime.datetime.now().isoformat(),
                    "username": username,
                    "message": message,
                }
                collection.insert_one(msg_data)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok"}).encode())
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Invalid data")
            return

        self.send_response(404)
        self.end_headers()

    def do_GET(self):
        if self.path == "/messages":
            messages = list(collection.find({}, {"_id": 0}))
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(messages).encode())
            return

        if self.path == "/":
            self.path = "/static/index.html"
        elif self.path == "/message.html":
            self.path = "/static/message.html"

        try:
            with open("." + self.path, "rb") as f:
                self.send_response(200)
                if self.path.endswith(".css"):
                    self.send_header("Content-Type", "text/css")
                elif self.path.endswith(".png"):
                    self.send_header("Content-Type", "image/png")
                elif self.path.endswith(".html"):
                    self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(f.read())
            return
        except FileNotFoundError:
            self.send_response(404)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            with open("./static/error.html", "rb") as f:
                self.wfile.write(f.read())

def udp_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((SOCKET_HOST, SOCKET_PORT))
    print(f"The UDP server is running on {SOCKET_HOST}:{SOCKET_PORT}")

    while True:
        data, _ = sock.recvfrom(1024)
        message = json.loads(data.decode())

        if "username" in message and "message" in message:
            message["date"] = datetime.datetime.now().isoformat()
            collection.insert_one(message)
            print(f"Saved UDP message: {message}")

if __name__ == "__main__":
    threading.Thread(target=udp_server, daemon=True).start()

    httpd = HTTPServer((HTTP_HOST, HTTP_PORT), CustomHandler)
    print(f"HTTP server running on {HTTP_HOST}:{HTTP_PORT}")
    httpd.serve_forever()
