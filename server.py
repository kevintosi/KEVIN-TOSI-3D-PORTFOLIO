import http.server
import socketserver

PORT = 8000

class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        '.bin': 'application/octet-stream',
        '.gltf': 'model/gltf+json',
        '.glb': 'model/gltf-binary',
        '.hdr': 'application/octet-stream',
        '.webm': 'video/webm',
        '.wav': 'audio/wav',
    }

    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"🚀 Server is live at http://localhost:{PORT}")
    print("Keep this window open. Press Ctrl+C to stop.")
    httpd.serve_forever()
