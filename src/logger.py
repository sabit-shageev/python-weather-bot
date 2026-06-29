import logging
import sys

def setup_logger(name: str = "weather_bot") -> logging.Logger:
    """Настраивает и возвращает логгер с указанным именем"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Обработчик для вывода в консоль (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    # Формат логов: время | уровень | имя | сообщение
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)

    # Добавляем обработчик к логгеру
    logger.addHandler(console_handler)

    return logger

# Глобальный логгер для всего приложения (можно использовать по умолчанию)
default_logger = setup_logger()