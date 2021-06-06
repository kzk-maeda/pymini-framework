# api.py
from typing import Callable, Dict
from webob import Request, Response, request

class API:
  def __init__(self) -> None:
      self.routes = {}


  def __call__(self, environ: Dict, start_response: Callable) -> Response:
    request = Request(environ)
    response = self.handle_request(request)

    return response(environ, start_response)


  # Decorator
  def route(self, path: str) -> Callable:
    def wrapper(handler):
      self.routes[path] = handler
      return handler
    
    return wrapper


  def handle_request(self, request: Request) -> Response:
    user_agent = request.environ.get("HTTP_USER_AGENT", "No User Agent Found")

    response = Response()
    handler = self._find_handler(request_path=request.path)

    if handler is not None:
      handler(request, response)
    else:
      self._default_response(response)
    
    return response


  def _default_response(self, response: Response) -> None:
    response.status_code = 404
    response.text = 'Not Found'
  

  def _find_handler(self, request_path: str) -> Callable:
    for path, handler in self.routes.items():
      if path == request_path:
        return handler