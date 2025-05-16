from http.server import HTTPServer, SimpleHTTPRequestHandler
import os


class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")

        if self.path.endswith(".pbf"):
            self.send_header("Content-Type", "application/x-protobuf")
            self.send_header("Content-Encoding", "gzip")

        super().end_headers()


if __name__ == "__main__":
    port = 8000
    print(f"Serving on http://localhost:{port}")
    httpd = HTTPServer(("localhost", port), CORSRequestHandler)
    httpd.serve_forever()
