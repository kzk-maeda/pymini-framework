from webob import Request, Response, request, response
# from api import API


class Middleware:
  def __init__(self, app) -> None:
    self.app = app

  
  def __call__(self, environ, start_response) -> Response:
    request = Request(environ)
    response = self.app.handle_request(request)
    return response(environ, start_response)    


  def add(self, middleware_cls) -> None:
    self.app = middleware_cls(self.app)


  def process_request(self, req: Request) -> None:
    pass


  def process_response(self, req: Request, res: Response) -> None:
    pass


  def handle_request(self, request: Request) -> Response:
    self.process_request(request)
    response = self.app.handle_request(request)
    self.process_response(request, response)

    return response