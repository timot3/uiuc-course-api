import flask
import pandas as pd
from flask import request, jsonify
import sqlite3
from SearchEngine import engine
from markdownify import markdownify

fields_to_search = ["name", "label", "description"]


app = flask.Flask(__name__)
app.config["DEBUG"] = True

data_path = 'data/class_data.db'


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@app.route('/', methods=['GET'])
def home():
    return "API is alive and well"


@app.route('/api/classes/all', methods=['GET'])
def api_all():
    conn = sqlite3.connect(data_path)
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all_classes = cur.execute('SELECT * FROM classes;').fetchall()

    return jsonify(all_classes)



@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

      
# @app.route('/api/classes/<string:name>/', methods=['GET'])
# def api_get_subject(name):
#     query = f"SELECT * FROM classes WHERE subject='{name.upper()}'"
#     to_filter = []

#     conn = sqlite3.connect(data_path)
#     conn.row_factory = dict_factory
#     cur = conn.cursor()
#     results = cur.execute(query, to_filter).fetchall()

#     return jsonify(results), 200


@app.route('/api/classes/', methods=['GET'])
def api_get_course():
    # class_id = f"{name.upper()} {str(number)}"
    # query = f"SELECT * FROM classes WHERE name='{class_id}'"
    to_filter = []

    search_query = 'SELECT * FROM classes '
    if 'subject' in request.args and 'number' in request.args:
        search_query += f"WHERE subject='{request.args['subject']}' AND number='{request.args['number']}'"
    else:
        if 'subject' in request.args:
            search_query += f"WHERE subject='{request.args['subject']}'"
        elif 'number' in request.args:
            search_query += f"WHERE number='{request.args['number']}'"
        else:
            return 'No query provided!', 404
    print(search_query)
    conn = sqlite3.connect(data_path)
    conn.row_factory = dict_factory
    cur = conn.cursor()
    results = cur.execute(search_query, to_filter).fetchall()

    return jsonify(results), 200


def descriptions_to_markdown(dict_res):
    for itm in dict_res:
        for field in fields_to_search:
            itm[field] = markdownify(itm[field])

    return dict_res

@app.route('/api/classes/search/', methods=['GET']) # GET api/classes/search/?query=Digital+Signal+Processing

def api_search_course():
    search_query = ''
    if 'query' in request.args:
        search_query = request.args['query']
    else:
        return 'No query provided!', 404
    
    res = engine.query(search_query, fields_to_search, highlight=True)
    return jsonify(descriptions_to_markdown(res)), 200



# def get_class_from_course_explorer(course):
#     href = ''
#     try:
#         href = urlopen('https://courses.illinois.edu/cisapp/explorer/catalog/2021/fall/' + course[0].upper() + '/'
#                        + course[1] + '.xml')

#     except urllib.error.HTTPError:
#         return None

#     class_tree = ET.parse(href).getroot()

#     class_id = class_tree.attrib['id']  # AAS 100
#     # department_code, course_num = course.__get_class(class_id)  # AAS, 100
#     label = class_tree.find('label').text  # Intro Asian American Studies
#     description = class_tree.find('description').text  # Provided description of the class
#     crh = class_tree.find('creditHours').text  # 3 hours.
#     deg_attr = ',\n'.join(
#         x.text for x in class_tree.iter('genEdAttribute'))  # whatever geneds the class satisfies
#     class_link = class_tree.find('termsOffered').find('course')
#     most_recent_url = 'https://courses.illinois.edu/schedule/2021/fall/'
#     if class_link is None:
#         year_term = 'None'
#     else:
#         year_term = class_link.text
#         most_recent_url = get_class_url(class_link.attrib['href'])
#         if year_term == 'Spring 2022':
#             year_term = 'Offered in ' + year_term + '. :white_check_mark:'
#         else:
#             year_term = 'Most recently offered in ' + year_term + '.'

#     gpa = get_recent_average_gpa(class_id.upper().replace(' ', ''))
#     #  return __get_dict(year_term, class_id, department_code, course_num, label, description, crh, deg_attr)

#     online_status = get_online_status(most_recent_url)

#     return Course(class_id, label, crh, gpa, year_term, deg_attr, description, most_recent_url, online_status)


# def get_online_status(most_recent_url):
#     try:
#         # get total num of sections & num online
#         r = requests.get(most_recent_url)
#         soup = BeautifulSoup(r.content, 'html.parser')
#         script = str(soup.find_all("script")[4])
#         script = script.replace('\"', '')
#         script = script.replace('\\a', 'A')
#         # print(script)
#         online_sections = script.count('type:<div class=App-meeting\>Online')
#         total_sections = script.count("crn")
#         # decide which emoji to use based on % of sections online

#         status_emoji = ":computer:" if int(online_sections) / int(total_sections) >= 0.5 else ":books:"
#         # create string/desc of status
#         online_status = f"{online_sections} of {total_sections} sections online. {status_emoji}"
#     except Exception:
#         print(traceback.format_exc())
#         online_status = "N/A"

#     return online_status

app.run()