# -*- coding: utf-8 -*-

"""Запуск документации"""
from docs.app import start_app
from loguru import logger

logger.info("Запуск документации")

if __name__ == "__main__":
    start_app()
