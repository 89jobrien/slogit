import logging
from concurrent.futures import ThreadPoolExecutor

# TODO: Write tests for this


class AsyncHandler(logging.Handler):
    def __init__(self, handler):
        super().__init__()
        self.handler = handler
        self.executor = ThreadPoolExecutor(max_workers=5)

    def emit(self, record):
        self.executor.submit(self.handler.emit, record)

    def close(self):
        self.executor.shutdown(wait=True)
        super().close()
