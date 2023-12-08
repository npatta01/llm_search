from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk
import pandas as pd
import tqdm.auto
import requests
import rich

class SearchClient:
    def __init__(self):
        ELASTIC_HOST="localhost"
        ELASTIC_PORT=9200

        self.url =f"http://{ELASTIC_HOST}:{ELASTIC_PORT}"
        
        self.client = Elasticsearch(
                [self.url]
        )
        
        self.index= "products"
        self.default_analyzer = "stop"
        
        
    def create_index(self, num_shards=1):
        """Creates an index in Elasticsearch. Delete old index."""

        if self.client.indices.exists(index=self.index):
            self.client.indices.delete(index=self.index)

        self.client.indices.create(
            index=self.index
            , body = { "settings" : {"number_of_shards": num_shards}
                        ,"mappings":  {
                            "properties": {
                                        "product_title": {"type": "text", "analyzer": self.default_analyzer }
                                        ,"url_image": {"type": "text" ,"index":False}
                                        ,"url_product": {"type": "text" ,"index":False}
                                        ,"product_id": {"type": "keyword" ,"index":False}

                                   }
                            }
                     }
            )

    def generate_docs(self,df:pd.DataFrame):
        """
        Given a datframe containing product data, yields a generator of dicitionary 
        """

        df = df[['product_id','product_title','url_product','url_image']]

        # iterate over dataframe contains posts with metadata
        for index, row in df.iterrows():
            doc = row.to_dict()

            # use PostId as document id
            doc['_id'] = doc["product_id"]

            for k in list(doc.keys()):
                # don't insert nan fields
                if doc[k] ==None:
                    del doc[k]

            yield doc

        
    def index_documents(self, df:pd.DataFrame):
        self.create_index()
        with tqdm.auto.tqdm(total=len(df) , unit="docs" ) as pbar:
            successes = 0


            for ok, action in streaming_bulk(
                    client=self.client, index=self.index, actions=self.generate_docs(df) ,
                ):
                pbar.update(1)
                successes += ok
        
        
    def analyze(self, query:str, analyzer=None):
        
        analyzer = analyzer or self.default_analyzer
        r =requests.post(self.url+"/_analyze", 
                  json =
                        {
                          "analyzer": analyzer ,
                          "text": query
                        }
            )

        return r.json() 

    
    def fetch_results(self, query:str,  num_hits=10, fields = ["product_title"], analyzer =None):
        """
        With the passed elastic search client, return documents that contain the passed `query` in the fields specified by `fields`

        If the fields is empty, it will search all text fields

        We are using mult-match, which by default uses `or`
        https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-match-query.html
        """


        analyzer = analyzer or self.default_analyzer

        resp = self.client.search(
            body={"query": {
                "multi_match" : {
                  "query":    query, 
                  "fields": [ "product_title" ] ,
                    "analyzer": analyzer
                }
              }
            }
            ,size = num_hits
        )

        return resp
    
