#!/usr/bin/env python3
import json
import time
from http import server, HTTPStatus
from urllib.parse import urlparse, parse_qs
from os.path import join


class handler(server.BaseHTTPRequestHandler):
    counter = 0

    def stream_handler(self):
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        queries = parse_qs(urlparse(self.path).query)
        delay_time = queries.get("sleep")

        with open(join("data", "streaming.txt"), "r") as file:
            # Stream the file contents
            for line in file:
                data = {"message": line.strip()}
                json_data = json.dumps(data)
                self.wfile.write(json_data.encode())
                self.wfile.write(b"\n")
                self.wfile.flush()
                # Simulate a delay
                if delay_time:
                    delay_time = delay_time[0]
                    print("DEBUG: Delaying response by = {} seconds".format(delay_time))
                    time.sleep(float(delay_time))
                else:
                    time.sleep(0.1)
        self.wfile.write(b"data: End of stream\n\n")
        self.wfile.flush()
        self.wfile.close()

    def do_GET(self):
        self.stream_handler()

    def do_OPTIONS(self):
        self.send_response(HTTPStatus.OK)
        requested_headers = self.headers.get("Access-Control-Request-Headers")
        requested_methods = self.headers.get("Access-Control-Request-Method")
        requested_origin = self.headers.get("Origin")
        print(
            "*** CORS Info: requested_origin = {}\n requested_methods = {}\n requested_headers = {}".format(
                requested_origin, requested_methods, requested_headers
            )
        )
        self.send_header("Access-Control-Allow-Origin", requested_origin)
        # Pseudo code
        # If requested_origin in allowed origin(s) or in configuration:
        #   Add domain to Access-Control-Allow-Origin response header
        self.send_header("Access-Control-Allow-Headers", requested_headers)
        self.send_header("Access-Control-Allow-Methods", requested_methods)
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header("Access-Control-Max-Age", 86400)
        # Pseudo code
        # If requested_headers in safelisted-request-headers #https://fetch.spec.whatwg.org/#cors-safelisted-request-header
        # Append header to Access-Control-Allow-Headers header value
        self.send_header("Content-length", 0)
        self.end_headers()
        request_headers = {}
        for header in self.headers._headers:
            request_headers[header[0]] = header[1]
        print(request_headers)
        close_chunk = "0\r\n\r\n"
        self.wfile.write(close_chunk.encode(encoding="utf-8"))

def main():
    """
    Run as a standalone server if needed
    """
    handler.run()


if __name__ == "__main__":
    main()
