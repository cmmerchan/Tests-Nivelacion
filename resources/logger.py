import logging
from threading import Lock
from colorlog import ColoredFormatter

class LoggerConfigurator:
    _is_configured = False
    _lock = Lock()

    @staticmethod
    def configure(log_file="errores.log"):
        with LoggerConfigurator._lock:
            if LoggerConfigurator._is_configured:
                return

            # Crea el logger raíz
            logger = logging.getLogger()
            logger.setLevel(logging.DEBUG)  # Acepta todos, los handlers filtran

            # 🎨 Consola con colores
            color_formatter = ColoredFormatter(
                fmt='%(log_color)s%(asctime)s %(levelname)s [%(threadName)s][%(user)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                log_colors={
                    'DEBUG':    'cyan',
                    'INFO':     'green',
                    'WARNING':  'yellow',
                    'ERROR':    'red',
                    'CRITICAL': 'bold_red',
                }
            )

            # 🔹 Handler para consola: muestra INFO en adelante
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(color_formatter)

            console_handler.addFilter(DefaultAttributeFilter({'user': '-'})) # Asegura que el atributo 'user' esté presente en los registros

            # 🔸 Handler para archivo: guarda solo errores
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.ERROR)
            file_format = logging.Formatter('%(asctime)s %(levelname)s [%(threadName)s][%(user)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s')
            file_handler.setFormatter(file_format)

            # Agrega ambos handlers al logger
            logger.addHandler(console_handler)
            logger.addHandler(file_handler)

            LoggerConfigurator._is_configured = True


class DefaultAttributeFilter(logging.Filter):
    def __init__(self, defaults):
        super().__init__()
        self.defaults = defaults

    def filter(self, record):
        for key, value in self.defaults.items():
            if not hasattr(record, key):
                setattr(record, key, value)
        return True  # siempre permite el registro