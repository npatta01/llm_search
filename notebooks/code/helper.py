import pandas as pd
from IPython.display import Image, JSON
from IPython.core.display import HTML
import ipyplot
from . import helper_es
import rich


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



        
        
def find_results(query:str, df:pd.DataFrame, num_hits =5 , show_ground_truth=False):
    
    relevance_dict = {'Exact': 0, 'Substitute': 1, 'Complement': 2, 'Irrelevant': 3} 
    relevancy_emoji = {'Exact': '✅', 'Substitute': '🔀', 'Complement': '🧩', 'Irrelevant': '❌' ,'Unlabelled':'❓' } 
    
    parsed_tokens = None
    if show_ground_truth==False:
        client_search = helper_es.SearchClient()
        resp = client_search.fetch_results(query, num_hits=num_hits)
        
        parsed_tokens = client_search.analyze(query)

        product_ids = []
        products = []
        scores = []

        for doc in resp['hits']["hits"]:
            product_source = doc['_source']
            products.append(product_source)

            product_ids.append(product_source['product_id'])
            scores.append(doc['_score'])
                
                

        df_raw_res = pd.DataFrame({'product_id':product_ids , 'product':products, 'score':scores})
        df_res = df[ df['product_id'].isin(product_ids)].drop_duplicates(['product_id'])
        df_res = pd.merge(df_raw_res[['product_id','score']], df_res, on =['product_id'] )
        df_res = df_res.sort_values(['score'], ascending=False)
        

    else:
        df_res = df[df['query'] == query]
        df_res = df_res.sort_values(by=['relevance_label'], key=lambda x: x.map(relevance_dict))
        
    df_ratings = df[df['query'] == query]

    
    if len(df_ratings) >0:
        df_res = df_res.drop(columns = ['relevance_label'])
        df_res = pd.merge(df_res,df_ratings[["product_id","relevance_label"]], on=["product_id"], how='left')
    else:
        df_res['relevance_label']=None
    

    df_res = df_res.fillna(value={'relevance_label': "Unlabelled"})
    df_res['relevancy_emoji'] = df_res['relevance_label'].apply(lambda x: relevancy_emoji[x] ) 
    
    
    data = df_res.iloc[0].to_dict()
    
     
    payload = {
       "query" : query,
        "num_records_with_ratings":len(df_ratings) ,
        "num_records" : len(df_res) ,
        "query_type": data['query_type']
    }
    
    if parsed_tokens:
        payload['parsed_tokens'] = parsed_tokens
    
    
    
    
    rich.print( payload)
        
    display(HTML(f"""
    <h2>Query: {query} </h2>
    
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
       

#     for idx, data in enumerate( records):
#         product_id = data['product_id']

#         images.append(data["url_image"])
#         #print(data["url_image"])
#         labels.append (f"""
#                        <a href="{data["url_product"]}">{data["product_title"]} </a> <br/>
#                        <p> {data["relevance_label"]} </p>
#                      """)

#     ipyplot.plot_images(images=images, labels=labels, img_width=200, show_url=False)        



    html = '<div style="display: flex; flex-wrap: wrap;">'
    for idx, row in enumerate( records):
        score= row.get('score','-')
        
        product_card = f"""
        <div style="margin: 10px; padding: 10px; border: 1px solid #ddd; border-radius: 8px; width: 200px;">
            <img src="{row['url_image']}" alt="{row['product_title']}" style="width:100%; height:auto; border-radius: 5px;">
            <h5><a href="{row['url_product']}" target="_blank">{row['product_title']}</a></h5>
            <hr>
            <p>Relevance: {row['relevance_label']} {row['relevancy_emoji']}  </p>
            <p>Score: {score}  </p>
        </div>
        """
        html += product_card
    html += '</div>'

    display(HTML(html))
                           
                           
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
