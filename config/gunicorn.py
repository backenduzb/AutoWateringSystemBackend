# import multiprocessing
from core.settings.base import DEBUG

bind = "0.0.0.0:8000"
workers = 2 if not DEBUG else 2 
worker_class = "gthread"  
threads = 2    
timeout = 120
keepalive = 5

accesslog = "-"
errorlog = "-"
loglevel = "info"