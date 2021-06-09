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


@print_info
@app.route("/sum/{num_1:d}/{num_2:d}")
def sum(request: Request, response: Response, num_1: int, num_2: int) -> None:
    total = int(num_1) + int(num_2)
    response.text = f"{num_1} + {num_2} = {total}"


@print_info
@app.route('/book')
class BooksResource:
  def get(self, req: Request, res: Response) -> None:
    res.text = "Books Page"
  
  def post(self, req: Request, res: Response) -> None:
    res.text = "Endpoint to create a book"


def handler(request: Request, response: Response) -> None:
  response.text = 'Sample'


app.add_route('/sample', handler)


@app.route("/template")
def template_handler(req, res):
    res.body = app.template(
        "index.html", context={"name": "Bumbo", "title": "Best Framework"}).encode()