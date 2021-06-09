# api.py
import inspect
from typing import Callable, Dict, Tuple
from parse import parse
from webob import Request, Response
from requests import Session as RequestsSession
from wsgiadapter import WSGIAdapter as RequestsWSGIAdapter
from util import print_info

class API:
  def __init__(self) -> None:
    self.routes = {}


  @print_info
  def __call__(self, environ: Dict, start_response: Callable) -> Response:
    request = Request(environ)
    response = self.handle_request(request)

    return response(environ, start_response)


  # Decorator
  @print_info
  def route(self, path: str) -> Callable:
    assert path not in self.routes, f'Such route already exists: {path}'

    def wrapper(handler):
      self.routes[path] = handler
      return handler
    
    return wrapper


  @print_info
  def handle_request(self, request: Request) -> Response:
    user_agent = request.environ.get("HTTP_USER_AGENT", "No User Agent Found")

    response = Response()
    handler, kwargs = self._find_handler(request_path=request.path)

    if handler is not None:
      if inspect.isclass(handler):
        handler = getattr(handler(), request.method.lower(), None)
        if handler is None:
          raise AttributeError("Method not allowed", request.method)
      
      handler(request, response, **kwargs)
    else:
      self._default_response(response)
    
    return response


  @print_info
  def _default_response(self, response: Response) -> None:
    response.status_code = 404
    response.text = 'Not Found.'
  

  @print_info
  def _find_handler(self, request_path: str) -> Tuple[Callable, Dict]:
    for path, handler in self.routes.items():
      parse_result = parse(path, request_path)
      if parse_result is not None:
        return handler, parse_result.named
    
    return None, None
  

  @print_info
  def test_session(self, base_url: str='http://testserver') -> RequestsSession:
    session = RequestsSession()
    session.mount(prefix=base_url, adapter=RequestsWSGIAdapter(self))
    return session