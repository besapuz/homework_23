import os

from flask import Flask, request
from werkzeug.exceptions import BadRequest

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


def build_query(data, cmd, value):
    res = map(lambda v: v.strip(), data)
    if cmd == "filter":
        res = filter(lambda v: value in v, res)
    if cmd == "sort":
        revers = value == 'desc'
        res = sorted(res, reverse=revers)
    if cmd == "unique":
        res = set(res)
    if cmd == "limit":
        value = int(value)
        res = list(res)[:value]
    if cmd == "map":
        value = int(value)
        res = map(lambda v: v.split(' ')[value], res)
    return list(res)


@app.route("/perform_query", methods=["POST"])
def perform_query():
    try:
        data = request.json
    except KeyError:
        return BadRequest, 400

    file_name = data["filename"]
    path_file = os.path.join(DATA_DIR, file_name)
    if not os.path.exists(path_file):
        raise BadRequest

    with open(path_file) as f:
        res = build_query(f, data["cmd1"], data["value1"])
        if "cmd2" in data and "value2" in data:
            res = build_query(res, data["cmd2"], data["value2"])
        res = '\n'.join(res)

    return app.response_class(res, content_type="text/plain")
