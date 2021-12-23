from typing import Dict, List, Sequence

from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import MultifieldParser
from whoosh.filedb.filestore import RamStorage
from whoosh.analysis import StemmingAnalyzer

import json

import pandas as pd
import sys
import sqlite3

data_path = 'data/sp22_courses.db'
# data_path = 'data/class_data.db'

# code from https://github.com/darenr/python-whoosh-simple-example/blob/master/example.py
class SearchEngine:

    def __init__(self, schema, docs):
        self.schema = schema
        schema.add('raw', TEXT(stored=True))
        self.ix = RamStorage().create_index(self.schema)
        self.docs = docs
        self.index_documents(self.docs)

    def index_documents(self, docs: Sequence):
        writer = self.ix.writer()
        for doc in docs:
            d = {k: v for k,v in doc.items() if k in self.schema.stored_names()}
            d['raw'] = json.dumps(doc) # raw version of all of doc
            writer.add_document(**d)
        writer.commit(optimize=True)

    def get_index_size(self) -> int:
        return self.ix.doc_count_all()

    def query(self, q: str, fields: Sequence, highlight: bool=True) -> List[Dict]:
        search_results = []
        with self.ix.searcher() as searcher:
            results = searcher.search(MultifieldParser(fields, schema=self.schema).parse(q))
            for r in results:
                d = json.loads(r['raw'])
                d['raw'] = json.loads(r['raw'])
                if highlight:
                    for f in fields:
                        if r[f] and isinstance(r[f], str):
                            d[f] = r.highlights(f) or r[f]

                search_results.append(d)

        return search_results

    def get_size_idx(self):
        return sys.getsizeof(self.ix)


schema = Schema(
    name=TEXT(stored=True),
    label=TEXT(stored=True, analyzer=StemmingAnalyzer()),
    description=TEXT(stored=True, analyzer=StemmingAnalyzer()),
    GPA=TEXT(stored=True)
)

# load_classes_query = 'SELECT Subject,Number,Name,`Credit Hours`,Label,Description,GPA,`Degree Attributes`,YearTerm FROM classes '
load_classes_query = 'SELECT subject,number,name,credit_hours,label,description,gpa,yearterm FROM classes '

docs = pd.DataFrame()
with sqlite3.connect(data_path) as conn:
    docs = pd.read_sql(load_classes_query, conn).dropna().to_dict(orient='records')

engine = SearchEngine(schema, docs)