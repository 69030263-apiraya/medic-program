import customtkinter as ctk

from .api_client import api_request
from .app_admin import AdminView
from .app_auth import AuthView
from .app_me import ProfileView
from .app_my_medicines import MyMedicinesView
from .settings import load_saved_theme
from .theme import COLORS


class AppService(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ระบบจัดการคลินิก")
        self.geometry("460x560")
        self.resizable(False, False)
        self.current_theme = load_saved_theme()
        ctk.set_appearance_mode(
            "Dark" if self.current_theme == "dark" else "Light"
        )
        self.configure(fg_color=COLORS["background"])
        self.current_view = None
        self.show_auth()

    def show_auth(self):
        self.geometry("460x560")
        self._show_view(AuthView(self, api_request, self.show_authenticated))

    def show_profile(self, user):
        self._show_view(ProfileView(self, user, api_request, self.show_auth))

    def show_my_medicines(self, user):
        self.geometry("900x700")
        self._show_view(
            MyMedicinesView(
                self, user, api_request, self.show_auth, self.set_theme
            )
        )

    def show_admin(self, user):
        self.geometry("900x700")
        self._show_view(AdminView(self, user, api_request, self.show_auth))

    def show_authenticated(self, user):
        if user.get("userRole") == "admin":
            self.show_admin(user)
        else:
            self.show_my_medicines(user)

    def set_theme(self, theme_name):
        if theme_name not in ("light", "dark"):
            raise ValueError(f"Unsupported theme: {theme_name}")
        self.current_theme = theme_name
        ctk.set_appearance_mode("Dark" if theme_name == "dark" else "Light")

    def _show_view(self, view):
        if self.current_view is not None:
            self.current_view.destroy()
        self.current_view = view
        view.pack(fill="both", expand=True)


def main():
    ctk.set_appearance_mode(
        "Dark" if load_saved_theme() == "dark" else "Light"
    )
    ctk.set_default_color_theme("blue")
    AppService().mainloop()


if __name__ == "__main__":
    main()