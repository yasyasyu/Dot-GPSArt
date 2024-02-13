import dash

app = dash.Dash(
    __name__, title="Dot-GPSArtRoute", use_pages=True, suppress_callback_exceptions=True
)

if __name__ == "__main__":
    app.run(use_reloader=True)
