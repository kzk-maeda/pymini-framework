# api.py
from typing import Callable, Dict
from webob import Request, Response

class API:
  def __init__(self) -> None:
      self.routes = {}


  def __call__(self, environ: Dict, start_response: Callable) -> Response:
    request = Request(environ)
    response = self.handle_request(request)

    return response(environ, start_response)


  def route(self, path: str) -> Callable:
    def wrapper(handler):
      self.routes[path] = handler
      return handler
    
    return wrapper


  def handle_request(self, request: Request) -> Response:
    user_agent = request.environ.get("HTTP_USER_AGENT", "No User Agent Found")

    response = Response()
    for path, handler in self.routes.items():
      if path == request.path:
        handler(request, response)
        return response

    return response