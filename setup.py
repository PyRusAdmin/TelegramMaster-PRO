# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

# Считываем зависимости из requirements.txt
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = f.read().splitlines()

# Основная конфигурация
setup(
    name='TelegramMaster-PRO',
    version='2.8.5',
    description='Программа для инвайтинга, парсинга, отправки сообщений в Telegram. Помощь администраторам, для ведения групп и каналов. A program for inviting, parsing, and sending messages to Telegram. Help administrators to manage groups and channels.',
    long_description=open('README.md', 'r', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='PyRusAdmin',
    author_email='zh.vitaliy92@yandex.com',
    url='https://github.com/PyRusAdmin/TelegramMaster-PRO',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'telegrammaster=main:main',
        ],
    },
)
