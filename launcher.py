import os
import threading
import tkinter as tk
from tkinter import messagebox

from waitress import create_server

from api.service import app as api_app


API_HOST = "127.0.0.1"
API_PORT = 5010


def main():
    os.environ["MEDIC_API_URL"] = f"http://{API_HOST}:{API_PORT}"

    try:
        server = create_server(api_app, host=API_HOST, port=API_PORT)
    except OSError as error:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "เปิดโปรแกรมไม่ได้",
            f"ไม่สามารถเปิด API ที่พอร์ต {API_PORT} ได้\n{error}",
            parent=root,
        )
        root.destroy()
        return

    server_thread = threading.Thread(
        target=server.run,
        name="medic-api",
        daemon=True,
    )
    server_thread.start()

    try:
        from app.service import main as run_app

        run_app()
    finally:
        server.close()


if __name__ == "__main__":
    main()
