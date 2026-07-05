import threading
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer

# === Simulated Open Ports ===
GUIDED_FAKE_FLAGS = {
    8032: "CCRI-UTOH-7108",  # ✅ REAL FLAG
    8069: "MLSQ-6694-WFAN",
    8004: "TZUF-QFQY-3965",
    8098: "WHBE-5909-BYCI",
    8072: "YHWY-3825-KGHG",
}
GUIDED_JUNK_RESPONSES = {
    8006: "DEBUG: Connection established successfully.",
    8010: "503 Service Unavailable\nTry again later.",
    8018: "Welcome to Experimental IoT Server (beta build).",
    8025: "💡 Tip: Scan only the ports you really need.",
    8043: "💻 Dev API v0.1 — POST requests only.",
    8052: "503 Service Unavailable\nTry again later.",
    8065: "<html><body><h1>It works!</h1><p>Apache2 default page.</p></body></html>",
    8088: "🔒 Unauthorized: API key required.",
    8092: "Hello World!\nTest endpoint active.",
    8094: "403 Forbidden: You don’t have permission to access this resource."
}
GUIDED_SERVICE_NAMES = {
    8000: "epsilon-sync",
    8003: "beta-hub",
    8012: "update-agent",
    8016: "auth-service",
    8017: "theta-daemon",
    8018: "delta-proxy",
    8023: "configd",
    8026: "alpha-core",
    8030: "metricsd",
    8044: "lambda-api",
    8051: "zeta-cache",
    8053: "sysmon-api",
    8056: "delta-sync",
    8069: "kappa-node",
    8084: "gamma-relay",
    8085: "beta-hub",
    8092: "omega-stream"
}
SOLO_FAKE_FLAGS = {
    9068: "CCRI-SPQE-6486",  # ✅ REAL FLAG
    9010: "YKGY-0651-NBTC",
    9094: "CHWR-ATUG-6537",
    9084: "BDDN-MGJJ-4367",
    9077: "GDLR-9819-RTYU",
}
SOLO_JUNK_RESPONSES = {
    9006: "403 Forbidden: You don’t have permission to access this resource.",
    9025: "ERROR 400: Bad request syntax.",
    9038: "Hello World!\nTest endpoint active.",
    9045: "Welcome to Dev HTTP Server v1.3\nPlease login to continue.",
    9049: "<html><body><h1>It works!</h1><p>Apache2 default page.</p></body></html>",
    9055: "Welcome to Dev HTTP Server v1.3\nPlease login to continue.",
    9059: "Welcome to Dev HTTP Server v1.3\nPlease login to continue.",
    9088: "Hello World!\nTest endpoint active.",
    9089: "403 Forbidden: You don’t have permission to access this resource.",
    9099: "503 Service Unavailable\nTry again later."
}
SOLO_SERVICE_NAMES = {
    9015: "metricsd",
    9016: "delta-sync",
    9024: "lambda-api",
    9025: "theta-daemon",
    9034: "configd",
    9035: "sysmon-api",
    9040: "alpha-core",
    9047: "kappa-node",
    9075: "zeta-cache",
    9076: "update-agent",
    9081: "auth-service",
    9085: "omega-stream",
    9094: "gamma-relay"
}

GUIDED_ALL_PORTS = {**GUIDED_JUNK_RESPONSES, **GUIDED_FAKE_FLAGS}
SOLO_ALL_PORTS = {**SOLO_JUNK_RESPONSES, **SOLO_FAKE_FLAGS}

# 🛡️ SO_REUSEADDR ENFORCED INTERFACE POOL
# Subclassing standard HTTPServer allows us to hardcode option flags on the socket
# layer BEFORE bind operations execute, entirely mitigating TIME_WAIT resource locks.
class RapidReuseHTTPServer(HTTPServer):
    allow_reuse_address = True

# === Dynamic HTTP Handler Factory ===
def PortHandlerFactory(response_map, service_map):
    class CustomPortHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            response = response_map.get(self.server.server_port, "Connection refused")
            service_name = service_map.get(self.server.server_port, "http")
            banner = f"👋 Welcome to {service_name} Service\n\n"
            self.send_response(200)
            self.send_header("Content-type", "text/plain; charset=utf-8")
            self.send_header("Server", service_name)
            self.send_header("X-Service-Name", service_name)
            self.end_headers()
            try:
                self.wfile.write((banner + response).encode("utf-8"))
            except (BrokenPipeError, ConnectionResetError):
                # Captured ConnectionResetError to absorb sudden, aggressive scans from Nmap
                pass

        def log_message(self, format, *args):
            # Suppress default request-by-request terminal logging output
            return
    return CustomPortHandler

def start_fake_service(port, response_map, service_map) -> bool:
    try:
        # Utilize the custom socket reuse wrapper class
        server = RapidReuseHTTPServer(('0.0.0.0', port), PortHandlerFactory(response_map, service_map))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        return True
    except OSError as e:
        logging.warning(f"❌ Could not bind port {port}: {e}")
        return False

def start_all_services(available_modes):
    """Starts fake services based on which modes are available."""
    launched_ports = []

    if "regular" in available_modes:
        for port in GUIDED_ALL_PORTS.keys():
            if start_fake_service(port, GUIDED_ALL_PORTS, GUIDED_SERVICE_NAMES):
                launched_ports.append(port)

    if "solo" in available_modes:
        for port in SOLO_ALL_PORTS.keys():
            if start_fake_service(port, SOLO_ALL_PORTS, SOLO_SERVICE_NAMES):
                launched_ports.append(port)

    # Output a concise, clean summary block instead of terminal spam
    if launched_ports:
        launched_ports.sort()
        ports_str = ", ".join(map(str, launched_ports))
        print(f"🚁 Successfully deployed {len(launched_ports)} mock service listeners across ports:")
        print(f"   [{ports_str}]")