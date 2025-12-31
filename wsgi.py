from dotenv import load_dotenv
# Load environement variables
load_dotenv()

from app.__init__ import create_app

app = create_app()
