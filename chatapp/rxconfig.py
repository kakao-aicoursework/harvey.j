import reflex as rx

class ChatappConfig(rx.Config):
    pass

config = ChatappConfig(
    app_name="chatapp",
    db_url="sqlite:///reflex.db",
    env=rx.Env.DEV,
)