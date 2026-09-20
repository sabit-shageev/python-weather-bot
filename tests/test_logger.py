import logging
from src.logger import setup_logger


def test_setup_logger_returns_logger():
    """Проверяем, что функция setup_logger возвращает объект logging.Logger"""
    logger = setup_logger("test_logger")
    assert isinstance(logger, logging.Logger)


def test_setup_logger_sets_correct_name():
    """Проверяем, что логгеру присваивается правильное имя"""
    logger = setup_logger("test_module")
    assert logger.name == "test_module"


def test_setup_logger_default_name():
    """Проверяем, что функция использует имя по умолчанию, если оно не передано"""
    logger = setup_logger()
    assert logger.name == "weather_bot"