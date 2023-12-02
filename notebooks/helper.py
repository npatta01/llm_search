import pandas as pd
from IPython.display import Image, JSON
from IPython.core.display import HTML
import ipyplot
import helper_es



def find_results_old(query:str, df:pd.DataFrame, k =5):
    
    df_subset = df[df['query'] == query]
    
    relevance_dict = {'Exact': 0, 'Substitute': 1, 'Complement': 2, 'Irrelevant': 3} 

    # sort by values
    df_subset = df_subset.sort_values(by=['relevance_label'], key=lambda x: x.map(relevance_dict))
    

    data = df_subset.iloc[0].to_dict()
    display(HTML(f"""
    <h2>Query: {query} </h2> (query type: {data['query_type']} )
    
    """))
    
    
    for relevance in relevance_dict:
        images = []
        labels = []
       
        
        df_tmp = df_subset[df_subset['relevance_label']==relevance]
        records = df_tmp.to_dict(orient ="records")
        
        if len(records) == 0:
            continue
            
        display(HTML(f"<h3>Relevance: {relevance} </h3>"))
    
        for idx, data in enumerate( records):
            product_id = data['product_id']

            images.append(data["url_image"])
            #print(data["url_image"])
            labels.append (f"""
                           <a href="{data["url_product"]}">{data["product_title"]} </a> <br/>
                         """)

        ipyplot.plot_images(images=images, labels=labels, img_width=200, show_url=False)



        
        
def find_results(query:str, df:pd.DataFrame, k =5):
    
    relevance_dict = {'Exact': 0, 'Substitute': 1, 'Complement': 2, 'Irrelevant': 3} 
    client_search = helper_es.SearchClient()
    resp = client_search.fetch_results(query)
    
    product_ids = []
    products = []
    
    for doc in resp['hits']["hits"]:
        product_source = doc['_source']
        products.append(product_source)
        
        product_ids.append(product_source['product_id'])
    
    
    df_res = df[ df['product_id'].isin(product_ids)].drop_duplicates(['product_id'])
    
    
    df_ratings = df[df['query'] == query]
    print(query, len(df_ratings), len(df_res))
    
    if len(df_ratings) >0:
        print(len(df_ratings))
        df_res = df_res.drop(columns = ['relevance_label'])
        df_res = pd.merge(df_res,df_ratings[["product_id","relevance_label"]], on=["product_id"], how='left')
    else:
        df_res['relevance_label']=None
    

    df_res = df_res.fillna(value={'relevance_label': "Unlabelled"})
    
    data = df_res.iloc[0].to_dict()
    display(HTML(f"""
    <h2>Query: {query} </h2> (query type: {data['query_type']} )
    
    """))
    
    
#     for relevance in relevance_dict:
#         images = []
#         labels = []
       
        
#         df_tmp = df_res[df_res['relevance_label']==relevance]
#         records = df_tmp.to_dict(orient ="records")
        
#         if len(records) == 0:
#             continue
            
#         display(HTML(f"<h3>Relevance: {relevance} </h3>"))
    
#         for idx, data in enumerate( records):
#             product_id = data['product_id']

#             images.append(data["url_image"])
#             #print(data["url_image"])
#             labels.append (f"""
#                            <a href="{data["url_product"]}">{data["product_title"]} </a> <br/>
#                          """)

#         ipyplot.plot_images(images=images, labels=labels, img_width=200, show_url=False)        

                           

    records = df_res.to_dict(orient ="records")

    # if len(records) == 0:
    #     continue

    images = []
    labels = []
       

    for idx, data in enumerate( records):
        product_id = data['product_id']

        images.append(data["url_image"])
        #print(data["url_image"])
        labels.append (f"""
                       <a href="{data["url_product"]}">{data["product_title"]} </a> <br/>
                       <p> {data["relevance_label"]} </p>
                     """)

    ipyplot.plot_images(images=images, labels=labels, img_width=200, show_url=False)                            

                           
                           
def display_results(query:str, df:pd.DataFrame, k =5):
    
    df_subset = df
    


    data = df_subset.iloc[0].to_dict()
    display(HTML(f"""
    <h2>Query: {query} </h2>  
    
    """))
    
    
    records = df_subset.to_dict(orient ="records")
    images = []
    labels = []

    
    for idx, data in enumerate( records):
        product_id = data['product_id']

        images.append(data["url_image"])
        #print(data["url_image"])
        labels.append (f"""
                       <a href="{data["url_product"]}">{data["product_title"]} </a> <br/>
                     """)

    ipyplot.plot_images(images=images, labels=labels, img_width=200, show_url=False)        
