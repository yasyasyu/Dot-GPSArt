ESCAPE_LINK = "\033[3m \033[36m"
ESCAPE_RESET = "\033[0m"

import dash
from wsgiref import simple_server

app = dash.Dash(
    __name__, title="Dot-GPSArtRoute", use_pages=True, suppress_callback_exceptions=True
)

if __name__ == "__main__":
    host = ""
    port = 8080
    server = simple_server.make_server(host, port, app.server)
    print()
    print(f"server start")
    print(f"click to access!!")
    print(f"here !  ->  {ESCAPE_LINK} http://localhost:{port} {ESCAPE_RESET}")
    server.serve_forever()
