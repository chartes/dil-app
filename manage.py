#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Launcher for the Flask application."""

from flask import Flask

app = Flask(__name__)


@app.route('/')
def main():
    return 'start!'


if __name__ == '__main__':
    app.run()
