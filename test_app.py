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