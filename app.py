# app.py
from webob import Request, Response
from api import API

app = API()


@app.route('/home')
def home(request: Request, response: Response) -> None:
  response.text = 'Hello from the Home page'


@app.route('/about')
def about(request: Request, response: Response) -> None:
  response.text = 'Hello from the About page'