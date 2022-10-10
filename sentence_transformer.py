# from sklearn.datasets import fetch_20newsgroups
import enum
import json
from sentence_transformers import SentenceTransformer
from torch import embedding
import umap
import hdbscan
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cluster import KMeans
import os
os.environ["TOKENIZERS_PARALLELISM"] = "true"

def create_embeddings(dataset="dataset/dataset_body_sent.json"):
    with open(dataset, "r") as json_file:
        data = json.load(json_file)
    file_name = dataset.removeprefix('dataset/dataset_').removesuffix('.json')
    model_list = ['all-MiniLM-L6-v2', 'all-mpnet-base-v2', 'all-MiniLM-L12-v2', 'all-distilroberta-v1']
    models = [SentenceTransformer(m, device='cuda') for m in model_list]
    embeddings = [model.encode(data, show_progress_bar=True) for model in models]
    for cnt, m in enumerate(model_list):
        with open(f'embedding/{file_name}_{m}_embeddings.pkl', "wb") as fOut:
            pickle.dump({'sentences': data, 'embeddings': embeddings[cnt]}, fOut, protocol=pickle.HIGHEST_PROTOCOL)

def load_embeddings(embedding):
    with open(embedding, "rb") as fIn:
        stored_data = pickle.load(fIn)
        stored_sentences = stored_data['sentences']
        stored_embeddings = stored_data['embeddings']
        return stored_sentences, stored_embeddings

def clustering(embeddings, method, num_clusters=150):
    if method == 'kmeans':
        clustering_model = KMeans(n_clusters=num_clusters)
        cluster = clustering_model.fit(embeddings)
    elif method == 'hdbscan':
        cluster = hdbscan.HDBSCAN(min_cluster_size=30,
                                  min_samples=5,
                                  metric='euclidean',
                                  cluster_selection_method='eom').fit(embeddings)
    else:
        print('Cluster method is not correctly specified!')
        return
    return cluster

# #TODO compare to kmeans clustering
# #TODO TSNE dimension redution and visualization

def visulization(embeddings, cluster):
    # Prepare data
    umap_data = umap.UMAP(n_neighbors=20, 
                          n_components=2, 
                          min_dist=0.0, 
                          metric='cosine').fit_transform(embeddings)
    result = pd.DataFrame(umap_data, columns=['x', 'y'])
    result['labels'] = cluster.labels_

    # Visualize clusters
    fig, ax = plt.subplots(figsize=(20, 10))
    outliers = result.loc[result.labels == -1, :]
    clustered = result.loc[result.labels != -1, :]
    plt.scatter(outliers.x, outliers.y, color='#BDBDBD', s=0.05)
    plt.scatter(clustered.x, clustered.y, c=clustered.labels, s=0.05, cmap='hsv_r')
    plt.colorbar()
    plt.show()

# docs_df = pd.DataFrame(data, columns=["Doc"])
# docs_df['Topic'] = cluster.labels_
# docs_df['Doc_ID'] = range(len(docs_df))
# docs_per_topic = docs_df.groupby(['Topic'], as_index = False).agg({'Doc': ' '.join})

# def c_tf_idf(documents, m, ngram_range=(1, 1)):
#     count = CountVectorizer(ngram_range=ngram_range, stop_words="english").fit(documents)
#     t = count.transform(documents).toarray()
#     w = t.sum(axis=1)
#     tf = np.divide(t.T, w)
#     sum_t = t.sum(axis=0)
#     idf = np.log(np.divide(m, sum_t)).reshape(-1, 1)
#     tf_idf = np.multiply(tf, idf)

#     return tf_idf, count
  
# tf_idf, count = c_tf_idf(docs_per_topic.Doc.values, m=len(data))


# def extract_top_n_words_per_topic(tf_idf, count, docs_per_topic, n=20):
#     words = count.get_feature_names_out()
#     labels = list(docs_per_topic.Topic)
#     tf_idf_transposed = tf_idf.T
#     indices = tf_idf_transposed.argsort()[:, -n:]
#     top_n_words = {label: [(words[j], tf_idf_transposed[i][j]) for j in indices[i]][::-1] for i, label in enumerate(labels)}
#     return top_n_words

# def extract_topic_sizes(df):
#     topic_sizes = (df.groupby(['Topic'])
#                      .Doc
#                      .count()
#                      .reset_index()
#                      .rename({"Topic": "Topic", "Doc": "Size"}, axis='columns')
#                      .sort_values("Size", ascending=False))
#     return topic_sizes

# top_n_words = extract_top_n_words_per_topic(tf_idf, count, docs_per_topic, n=20)
# topic_sizes = extract_topic_sizes(docs_df); print(topic_sizes.head(10))

# for n in range(10):
#     print(f"Top {n+1} topic is : \n{top_n_words[topic_sizes.iloc[n][0]][:10]}")
    

if __name__ == '__main__':
    corpus, embeddings = load_embeddings('embedding/body_all-mpnet-base-v2_embeddings.pkl')
    
    # reduce the dimensions of embeddings
    umap_embeddings = umap.UMAP(n_neighbors=20, 
                                n_components=15,
                                metric='cosine').fit_transform(embeddings)
    cluster = clustering(umap_embeddings, 'hdbscan')
    visulization(embeddings, cluster)
    
    
    