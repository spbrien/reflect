from livereload import Server, shell

from app import app

server = Server(app)
server.serve(port=5000, host='localhost', open_url_delay=True)
