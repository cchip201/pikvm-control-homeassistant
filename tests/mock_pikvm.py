"""Mock PiKVM HTTP API Server for offline testing."""
import base64
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import parse_qs, urlparse

HOST = "127.0.0.1"
PORT = 8080
EXPECTED_AUTH = "Basic " + base64.b64encode(b"admin:password").decode("utf-8")

# In-memory mock states
mock_state = {
    "busy": False,
    "enabled": True,
    "leds": {
        "power": True,
        "hdd": False
    }
}

class MockPiKVMHandler(BaseHTTPRequestHandler):
    """Handler for PiKVM mock endpoints."""

    def _check_auth(self) -> bool:
        """Verify Basic Authentication headers."""
        auth_header = self.headers.get("Authorization")
        if auth_header == EXPECTED_AUTH:
            return True
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="PiKVM"')
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"ok": False, "error": "Unauthorized"}).encode("utf-8"))
        return False

    def do_GET(self) -> None:
        """Handle GET requests."""
        if not self._check_auth():
            return

        parsed_path = urlparse(self.path)
        if parsed_path.path == "/api/atx":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"ok": True, "result": mock_state}
            self.wfile.write(json.dumps(response).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self) -> None:
        """Handle POST requests."""
        if not self._check_auth():
            return

        parsed_path = urlparse(self.path)
        query = parse_qs(parsed_path.query)

        if parsed_path.path == "/api/atx/click":
            button = query.get("button", [None])[0]
            if button in ("power", "reset"):
                # Simulate toggling power LED state upon clicking power
                if button == "power":
                    mock_state["leds"]["power"] = not mock_state["leds"]["power"]

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": True, "result": f"{button} clicked successfully"}).encode("utf-8"))
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": "Invalid button"}).encode("utf-8"))

        elif parsed_path.path == "/api/atx/power":
            action = query.get("action", [None])[0]
            if action in ("on", "off", "off_hard", "reset_hard"):
                if action == "off_hard":
                    mock_state["leds"]["power"] = False

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": True, "result": f"power action {action} triggered"}).encode("utf-8"))
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": "Invalid action"}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

def run() -> None:
    """Run mock server."""
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, MockPiKVMHandler)
    print(f"Mock PiKVM Server running at http://{HOST}:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Mock PiKVM Server...")
        httpd.server_close()

if __name__ == "__main__":
    run()
