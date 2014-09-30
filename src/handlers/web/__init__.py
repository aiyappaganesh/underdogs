from .web_request_handler import WebRequestHandler
from django import template

template.add_to_builtins('handlers.web.filters')