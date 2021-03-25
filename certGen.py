#!/usr/bin/python3
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from subprocess import Popen, check_output, call
from urllib.parse import parse_qs, urlparse
import os

# curl "http://mariusmotea.go.ro:9002/gencert?mac=$mac" > /opt/hue-emulator/cert.pem

class S(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/gencert"):
            get_parameters = parse_qs(urlparse(self.path).query)
            if get_parameters:
                if "mac" in get_parameters:
                    self.send_response(200)

                    mac = get_parameters["mac"][0].replace(":","").lower()
                    dec_serial= str(int(mac, 16))
                    response = ""
                    Popen(["openssl", "req", "-new", "-days", "3650", "-config", "openssl.conf", "-nodes", "-x509", "-newkey", "ec", "-pkeyopt", "ec_paramgen_curve:P-256", "-pkeyopt", "ec_param_enc:named_curve", "-subj", "/C=NL/O=Philips Hue/CN=" + mac, "-keyout", "/tmp/private.key", "-out", "/tmp/public.crt", "-set_serial", dec_serial])
                    with open('/tmp/private.key', 'r') as file:
                        response = file.read()
                    with open('/tmp/public.crt', 'r') as file:
                        response += file.read()
                    os.remove("/tmp/private.key")
                    os.remove("/tmp/public.crt")
                    self.wfile.write(bytes(response,"utf8"))


        else:
           self.send_response(404)
           self.end_headers()


class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass


if __name__ == "__main__":
    server_class=ThreadingSimpleServer
    handler_class=S
    server_address = ("0.0.0.0", 9002)
    httpd = server_class(server_address, handler_class)
    print('Starting ssl httpd...')
    httpd.serve_forever()
    httpd.server_close()
