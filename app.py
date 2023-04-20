from typing import List, Tuple
import flask

# import pandas as pd
from flask import request, jsonify, render_template
from flask_cors import CORS
import sqlite3
from utils.SearchEngine import engine
from functools import lru_cache
import asyncio

from utils.functions import (
    course_cache,
    dict_factory,
    cache_classes,
    fields_to_search,
    descriptions_to_markdown,
)

loop = asyncio.get_event_loop()

app = flask.Flask(__name__)
CORS(app)

data_path = "data/fa23_courses.db"


@app.errorhandler(404)
def page_not_found(e):
    return "The resource could not be found.", 404


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@lru_cache
def exec_query(search_query: str, to_filter: Tuple[str] = []):
    print(search_query)
    with sqlite3.connect(data_path) as conn:
        conn.row_factory = dict_factory
        cur = conn.cursor()

        placeholders = tuple(to_filter)
        results = cur.execute(search_query, placeholders).fetchall()

    if len(results) == 0:
        return "No courses found!", 404

    return jsonify(results), 200


@app.route("/api/classes/all", methods=["GET"])
def api_all():
    search_query = "SELECT * from classes;"
    return exec_query(search_query)


@app.route("/api/classes/", methods=["GET"])
def api_get_course():
    subj, num, section = None, None, None
    if "subject" in request.args:
        subj = request.args["subject"]
    if "number" in request.args:
        num = request.args["number"]
    if "section" in request.args:
        section = request.args["section"]

    search_query = "SELECT * FROM classes "
    to_filter = []
    if subj is not None and num is not None:
        # check to see if the course is cached or not
        label = f"{subj.upper()} {num}"
        if label in course_cache:
            return course_cache[label], 200
        
        to_filter.append(subj.upper())
        to_filter.append(num)

        if section is not None:
            search_query += f"WHERE subject=? AND number=? AND section=?"
            to_filter.append(section)
        else:
            search_query += f"WHERE subject=? AND number=?"
        
        print(search_query)
    else:
        if subj is not None:
            search_query += f"WHERE subject=?"
            to_filter.append(subj.upper())
        elif num is not None:
            search_query += f"WHERE number=?"
            to_filter.append(num)
        elif section is not None:
            search_query += f"WHERE section=?"
            to_filter.append(section)
        else:
            return "No query provided!", 404

    print(to_filter)
    placeholder_tuple = tuple(to_filter)
    return exec_query(search_query, to_filter=placeholder_tuple)


@lru_cache
@app.route("/api/classes/crn/", methods=["GET"])
def api_get_crn():
    crn = None
    if "crn" in request.args:
        crn = request.args["crn"]
    else:
        return "No query provided!", 404
    search_query = f"SELECT * FROM classes WHERE crn={int(crn)} limit 1"

    return exec_query(search_query)


# GET api/classes/search/?query=Digital+Signal+Processing
@app.route("/api/classes/search/", methods=["GET"])
def api_search_course():
    if "query" in request.args:
        search_query = request.args["query"]
    else:
        return "No query provided!", 404

    res = engine.query(search_query, fields_to_search, highlight=True)

    # I expect courses that were requested by a search to be requested
    # immediately after with a query for more information
    loop.create_task(cache_classes(res))

    return jsonify(descriptions_to_markdown(res)), 200


if __name__ == "__main__":
    print("Starting app....")
    app.run(host="0.0.0.0", debug=True)
