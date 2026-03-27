"""Root launcher that delegates execution to the app package entrypoint."""

from app.main import run

if __name__ == "__main__":
    run()
