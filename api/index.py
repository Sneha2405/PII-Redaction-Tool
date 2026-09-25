import os
import sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.engine import PIIRedactor

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "status": "success",
            "service": "Enterprise PII Redaction API",
            "version": "1.0.0",
            "usage": "POST text content to /api to redact PII entities"
        }
        self.wfile.write(str(response).encode('utf-8'))
        return

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        redactor = PIIRedactor(seed=42)
        redacted_text, entities = redactor.redact(post_data)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        import json
        res_data = json.dumps({
            "redacted_text": redacted_text,
            "entities_detected": len(entities),
            "details": entities
        })
        self.wfile.write(res_data.encode('utf-8'))
        return
