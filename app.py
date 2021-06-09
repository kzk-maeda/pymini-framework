# app.py
from webob import Request, Response
from api import API
from util import print_info

app = API()


@print_info
@app.route('/home')
def home(request: Request, response: Response) -> None:
  response.text = 'Hello from the Home page'


@print_info
@app.route('/about')
def about(request: Request, response: Response) -> None:
  response.text = 'Hello from the About page'


@print_info
@app.route('/hello/{name}')
def greeting(request: Request, response: Response, name: str) -> None:
  response.text = f'Hello , {name}'


@app.route("/sum/{num_1:d}/{num_2:d}")
def sum(request: Request, response: Response, num_1: int, num_2: int) -> None:
    total = int(num_1) + int(num_2)
    response.text = f"{num_1} + {num_2} = {total}"