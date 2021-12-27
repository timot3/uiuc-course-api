import flask
# import pandas as pd
from flask import request, jsonify
import sqlite3
from utils.SearchEngine import engine
from functools import lru_cache
import asyncio

from utils.functions import course_cache, dict_factory, cache_classes, fields_to_search, descriptions_to_markdown

loop = asyncio.get_event_loop()

app = flask.Flask(__name__)
# app.config["DEBUG"] = True

data_path = 'data/sp22_courses.db'

@app.errorhandler(404)
def page_not_found(e):
    return "The resource could not be found.", 404


@app.route('/', methods=['GET'])
def home():
    return """API is alive and well :) \n
    Visit https://github.com/timot3/uiuc-course-api for documentation."""


@app.route('/api/classes/all', methods=['GET'])
def api_all():
    conn = sqlite3.connect(data_path)
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all_classes = cur.execute('SELECT subject,number,name,credit_hours,label,description,gpa,degree_attributes,yearterm FROM classes;').fetchall()
    return jsonify(all_classes)

@lru_cache  
@app.route('/api/classes/', methods=['GET'])
def api_get_course():
    # class_id = f"{name.upper()} {str(number)}"
    subj, num = None, None
    if 'subject' in request.args:
        subj = request.args['subject']
    if 'number' in request.args:
        num = request.args['number']

    search_query = 'SELECT subject,number,name,credit_hours,label,description,gpa,degree_attributes,yearterm FROM classes '
    if subj is not None and num is not None:
        # check to see if the course is cached or not
        label = f'{subj.upper()} {num}'
        if label in course_cache:
            return course_cache[label], 200
        
        search_query += f"WHERE subject='{subj.upper()}' AND number='{num}'"
        print(search_query)
    else:
        if subj is not None:
            search_query += f"WHERE subject='{subj.upper()}'"
        elif num is not None:
            search_query += f"WHERE number='{num}'"
        else:
            return 'No query provided!', 404
    
    print(search_query)
    conn = sqlite3.connect(data_path)
    conn.row_factory = dict_factory
    cur = conn.cursor()
    to_filter = []

    results = cur.execute(search_query, to_filter).fetchall()

    if len(results) == 0:
        return 'No courses found!', 404

    return jsonify(results), 200

@app.route('/api/classes/search/', methods=['GET']) # GET api/classes/search/?query=Digital+Signal+Processing
def api_search_course():
    search_query = ''
    if 'query' in request.args:
        search_query = request.args['query']
    else:
        return 'No query provided!', 404
    
    res = engine.query(search_query, fields_to_search, highlight=True)

    # I expect courses that were requested by a search to be requested 
    # immediately after with a query for more information
    loop.create_task(cache_classes(res))

    return jsonify(descriptions_to_markdown(res)), 200

if __name__ == '__main__':
# def main():
    print("Starting app....")
    app.run(host='0.0.0.0', debug=True)
