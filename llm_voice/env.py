import os
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME: str = os.environ["MODEL_NAME"]
OPENAI_API_KEY: str | None = os.environ.get("OPENAI_API_KEY")
