import pytest
from webob import Request, Response
from requests import Session
from api import API


@pytest.fixture
def api():
  return API()


@pytest.fixture
def client(api):
  return api.test_session()


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