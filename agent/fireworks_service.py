from langchain_fireworks import Fireworks

# os.environ["FIREWORKS_API_KEY"] = "<KEY>"


class FireworksService:
    def __init__(self):
        self.agent = Fireworks(api_key="<KEY>")
