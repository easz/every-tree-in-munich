from http.server import HTTPServer, SimpleHTTPRequestHandler
import argparse


class CORSRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, compressed_pbf=True, **kwargs):
        self.compressed_pbf = compressed_pbf
        super().__init__(*args, **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")

        # Set content type and encoding for .pbf files
        if self.path.endswith(".pbf"):
            self.send_header("Content-Type", "application/x-protobuf")
            if self.compressed_pbf:
                self.send_header("Content-Encoding", "gzip")

        super().end_headers()


def run_server(port=8000, compressed_pbf=True):
    def handler(*args, **kwargs):
        CORSRequestHandler(*args, compressed_pbf=compressed_pbf, **kwargs)

    httpd = HTTPServer(("localhost", port), handler)
    print(f"Serving on http://localhost:{port} (compressed_pbf={compressed_pbf})")
    httpd.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Simple HTTP server with CORS and .pbf handling."
    )
    parser.add_argument(
        "-p", "--port", type=int, default=8000, help="Port to serve on (default: 8000)"
    )
    parser.add_argument(
        "-X",
        "--uncompressed",
        action="store_true",
        help="Serve .pbf files as uncompressed (default: compressed)",
    )

    args = parser.parse_args()

    run_server(port=args.port, compressed_pbf=not args.uncompressed)
