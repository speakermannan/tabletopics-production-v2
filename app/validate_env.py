from dotenv import load_dotenv
import os

load_dotenv()

print("KEY LOADED:", bool(os.getenv("OPENAI_API_KEY")))

