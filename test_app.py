from typing import Any, Callable
import pytest
from webob import Request, Response
from requests import Session
from api import API
from middleware import Middleware


############
## fixtures

@pytest.fixture
def api():
  return API()


@pytest.fixture
def client(api):
  return api.test_session()


############
## helpers

FILE_DIR = 'css'
FILE_NAME = 'main.css'
FILE_CONTENTS = 'body {background-color: red}'

def _create_static(static_dir: str) -> Any:
  asset = static_dir.mkdir(FILE_DIR).join(FILE_NAME)
  asset.write(FILE_CONTENTS)

  return asset


############
## tests

def test_basic_route_adding(api: API):
  @api.route('/home')
  def home(req: Request, res: Response) -> None:
    res.text = 'YOLO'


def test_route_overlap_throws_exception(api: API):
  @api.route('/home')
  def home(req: Request, res: Response) -> None:
    res.text = 'YOLO'
  
  with pytest.raises(AssertionError):
    @api.route('/home')
    def home2(req: Request, res: Response) -> None:
      res.text = 'YOLO'


def test_app_test_client_can_send_requests(api: API, client: Session):
  RESPONSE_TEXT = 'This is COOL'

  @api.route('/hey')
  def cool(req, res):
    res.text = RESPONSE_TEXT
  
  assert client.get('http://testserver/hey').text == RESPONSE_TEXT


def test_parameterized_route(api, client):
    @api.route("/{name}")
    def hello(req, resp, name):
        resp.text = f"hey {name}"

    assert client.get("http://testserver/matthew").text == "hey matthew"
    assert client.get("http://testserver/ashley").text == "hey ashley"


def test_default_404_response(client):
    response = client.get("http://testserver/doesnotexist")

    assert response.status_code == 404
    assert response.text == "Not Found."


def test_class_based_handler_get(api, client):
    response_text = "this is a get request"

    @api.route("/book")
    class BookResource:
        def get(self, req, resp):
            resp.text = response_text

    assert client.get("http://testserver/book").text == response_text


def test_class_based_handler_post(api, client):
    response_text = "this is a post request"

    @api.route("/book")
    class BookResource:
        def post(self, req, resp):
            resp.text = response_text

    assert client.post("http://testserver/book").text == response_text


def test_class_based_handler_not_allowed_method(api, client):
    @api.route("/book")
    class BookResource:
        def post(self, req, resp):
            resp.text = "yolo"

    with pytest.raises(AttributeError):
        client.get("http://testserver/book")


def test_alternative_route(api: API, client: Session):
  response_text = 'Alternative way to add a route'

  def home(req, res):
    res.text = response_text
  
  api.add_route('/alternative', home)

  assert client.get('http://testserver/alternative').text == response_text


def test_template(api: API, client: Session):
  @api.route('/html')
  def html_handler(req, res):
    res.body = api.template('index.html', context={'title': 'Some title', 'name': 'Some Name'}).encode()

  response = client.get('http://testserver/html')

  assert 'text/html' in response.headers['Content-Type']
  assert 'Some title' in response.text
  assert 'Some Name' in response.text


def test_custom_exception_handler(api: API, client: Session):
  def on_exception(req, res, exc):
    res.text = 'AttributeErrroHappened'
  
  api.add_exception_handler(on_exception)

  @api.route('/')
  def index(req, res):
    raise AttributeError()
  
  response = client.get('http://testserver/')

  assert response.text == 'AttributeErrroHappened'


def test_404_is_returned_for_nonexistent_static_file(client: Session):
  assert client.get(f'http://testserver/static/hoge.css').status_code == 404


def test_assets_are_served(tmpdir_factory):
  static_dir = tmpdir_factory.mktemp('static')
  _create_static(static_dir)
  api = API(static_dir=str(static_dir))
  client = api.test_session()

  response = client.get(f'http://testserver/static/{FILE_DIR}/{FILE_NAME}')

  assert response.status_code == 200
  assert response.text == FILE_CONTENTS


def test_middleware_methods_are_calles(api: API, client: Callable):
  process_request_called = False
  process_response_called = False

  class CallMiddlewareMethod(Middleware):
    def __init__(self, app) -> None:
      super().__init__(app)
    
    def process_request(self, req):
      nonlocal process_request_called
      process_request_called = True

    def process_response(self, req, res):
      nonlocal process_response_called
      process_response_called = True
  
  api.add_middleware(CallMiddlewareMethod)

  @api.route('/')
  def index(req, res):
    res.text = "YOLO"

  client.get('http://testserver/')

  assert process_request_called is True
  assert process_response_called is True