from typing import Dict, List, Sequence
from whoosh import index
from whoosh.index import create_in, EmptyIndexError
from whoosh.fields import *
from whoosh.qparser import MultifieldParser
from whoosh.filedb.filestore import RamStorage, FileStorage, copy_to_ram
from whoosh.analysis import StemmingAnalyzer

import json

import os
import sys
import sqlite3
import pandas as pd

data_path = "data/sp23_courses.db"
index_path = "data/index/"
load_classes_query = "SELECT subject,number,name,credit_hours,label,description,gpa,yearterm,degree_attributes FROM classes "


# code adapted from https://github.com/darenr/python-whoosh-simple-example/blob/master/example.py
class SearchEngine:
    def __init__(self, schema, docs=None):
        self.schema = schema
        schema.add("raw", TEXT(stored=True))
        # Load index from file storage
        # try loading index. If unsuccessful, load index into Ram storage.
        try:
            storage = copy_to_ram(FileStorage("data/index"))
            self.ix = storage.open_index()

        except EmptyIndexError:
            with sqlite3.connect(data_path) as conn:
                # Use sql query to load docs into pandas dataframe.
                docs = (
                    pd.read_sql(load_classes_query, conn)
                    .drop_duplicates(subset=["label"])
                    .to_dict(orient="records")
                )
                self.index_documents(docs)

                storage = copy_to_ram(FileStorage("data/index"))
                self.ix = storage.open_index()

    def index_documents(self, docs: Sequence):
        """
        Loads `docs` into this object's index.
        Not currently used since I'm using the index that is already stored inside the data/index folder.
        """

        if docs is None:
            return None

        if not os.path.exists(index_path):
            os.makedirs(index_path)

        self.ix = index.create_in(index_path, self.schema)
        writer = self.ix.writer()

        for doc in docs:
            d = {k: v for k, v in doc.items() if k in self.schema.stored_names()}
            d["raw"] = json.dumps(doc)  # raw version of all of doc
            writer.add_document(**d)
        writer.commit(optimize=True)

    def get_index_size(self) -> int:
        return self.storage_ix.doc_count_all()

    def query(self, q: str, fields: Sequence, highlight: bool = True) -> List[Dict]:
        search_results = []
        with self.ix.searcher() as searcher:
            results = searcher.search(
                MultifieldParser(fields, schema=self.schema).parse(q)
            )
            for r in results:
                d = json.loads(r["raw"])
                d["raw"] = json.loads(r["raw"])
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
    GPA=TEXT(stored=True),
)

engine = SearchEngine(schema)
