# -*- coding: utf-8 -*-
import yaml


def load_translations():
    """
    Загружает переводы из YAML-файла.

    :return: Словарь с переводами
    """
    with open("src/locales/translations.yaml", "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


translations = load_translations()
