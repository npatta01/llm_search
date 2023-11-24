import pandas as pd
from IPython.display import Image, JSON
from IPython.core.display import HTML
import ipyplot




def find_results(query:str, df:pd.DataFrame, k =5):
    
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
