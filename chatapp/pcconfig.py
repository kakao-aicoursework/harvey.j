import pynecone as pc

class ChatappConfig(pc.Config):
    pass

config = ChatappConfig(
    app_name="chatapp",
    db_url="sqlite:///pynecone.db",
    env=pc.Env.DEV,
)