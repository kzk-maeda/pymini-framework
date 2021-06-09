import pytest
from webob import Request, Response
from api import API


@pytest.fixture
def api():
  return API()


def test_basic_route_adding(api):
  @api.route('/home')
  def home(req: Request, res: Response) -> None:
    res.text = 'YOLO'


def test_route_overlap_throws_exception(api):
  @api.route('/home')
  def home(req: Request, res: Response) -> None:
    res.text = 'YOLO'
  
  with pytest.raises(AssertionError):
    @api.route('/home')
    def home2(req: Request, res: Response) -> None:
      res.text = 'YOLO'