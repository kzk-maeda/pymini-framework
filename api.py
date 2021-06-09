# api.py
import inspect
import os
from typing import Any, Callable, Dict, Tuple
from parse import parse
import requests
from webob import Request, Response
from requests import Session as RequestsSession
from wsgiadapter import WSGIAdapter as RequestsWSGIAdapter
from jinja2 import Environment, FileSystemLoader

from util import print_info


class API:
  @print_info
  def __init__(self, templates_dir='templates') -> None:
    self.routes = {}
    self.templates_env = Environment(
      loader=FileSystemLoader(os.path.abspath(templates_dir))
    )
    self.exception_handler = None


  @print_info
  def __call__(self, environ: Dict, start_response: Callable) -> Response:
    request = Request(environ)
    response = self.handle_request(request)

    return response(environ, start_response)


  #################################
  ## Routes
  #################################
  @print_info
  def add_route(self, path: str, handler: Callable) -> None:
    '''
    Common method and Django like route
    Usage:
      in app class or method, define route as function such like

      def func(req, res):
        do something
      
      app.add_route(path, func)
    '''
    assert path not in self.routes, f'Such route already exists: {path}'

    self.routes[path] = handler


  @print_info
  def route(self, path: str) -> Callable:
    '''
    Flask like route
    Usage:
      in app class or method, define route as decorator such like

      @app.route('/path')
      def func(req, res):
        do something
    '''
    def wrapper(handler):
      self.add_route(path, handler)
      return handler
    
    return wrapper


  #################################
  ## Request Handler
  #################################
  @print_info
  def handle_request(self, request: Request) -> Response:
    user_agent = request.environ.get("HTTP_USER_AGENT", "No User Agent Found")

    response = Response()
    handler, kwargs = self._find_handler(request_path=request.path)

    try:
      if handler is not None:
        if inspect.isclass(handler):
          handler = getattr(handler(), request.method.lower(), None)
          if handler is None:
            raise AttributeError("Method not allowed", request.method)
        
        handler(request, response, **kwargs)
      else:
        self._default_response(response)
      
    except Exception as e:
      if self.exception_handler is None:
        raise e
      else:
        self.exception_handler(request, response, e)
  
    return response


  @print_info
  def template(self, template_name: str, context: Dict = None) -> str:
    if context is None:
      context = {}
    
    return self.templates_env.get_template(template_name).render(**context)


  #################################
  ## Exception Handler
  #################################
  @print_info
  def add_exception_handler(self, exception_handler: Any) -> Any:
    self.exception_handler = exception_handler


  #################################
  ## Private Methods
  #################################
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