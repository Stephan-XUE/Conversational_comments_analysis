import re
import json
from nltk.tokenize import sent_tokenize
import nltk
nltk.download('punkt')

from datetime import datetime

def data_washing(input_file=None, output_file=None):
    assert input_file or output_file, "Please specified the input/output file names!"
    with open(input_file, "r") as json_file:
        data_list = json.load(json_file)
    for dict in data_list:
        dict["body"] = re.sub(r'http\S+', ' ', dict["body"])
        dict["body"] = re.sub(r'www\S+', ' ', dict["body"])
        for comment in dict["comments"]:
            comment["body"] = re.sub(r'http\S+', ' ', comment["body"])
            comment["body"] = re.sub(r'www\S+', ' ', comment["body"])
            
    with open(output_file, 'w') as f:
        json.dump(data_list, f)
        
def data_merging(input_file1, input_file2, output_file):
    with open(input_file1, "r") as json_file:
        data_list1 = json.load(json_file)
    with open(input_file2, "r") as json_file:
        data_list2 = json.load(json_file)
    cnt = 0
    for dict1 in data_list1:
        for dict2 in data_list2:
            if dict2['id'] == dict1['id']:
                data_list2.remove(dict2)
                cnt += 1
    print(f"{cnt} posts in {input_file2} has been removed!")
    
    data_list = data_list1 + data_list2
    
    data_list.sort(key=lambda dict: datetime.strptime(dict["created_utc"], "%Y-%m-%d %H:%M:%S")) #"2022-07-14 23:13:49"
    
    with open(output_file, 'w') as f:
        json.dump(data_list, f)

def loading_data(directory="/home/fan/Gits/NLP_Comments_Analysis", input_file="dataset_cleaned.json", output_file="dataset_body.json"):
    print(f"start reading JSON file: {directory}/{input_file}")
    with open(input_file, "r") as json_file:
        data_list = json.load(json_file)
    data = []
    for dict in data_list:
        if dict["body"] != "" or dict["body"] != "[deleted]" or dict["body"] != "[removed]":
            data.append(dict["body"])
            for comment in dict["comments"]:
                if comment["body"] != "" or comment["body"] != "[deleted]" or comment["body"] != "[removed]":
                    data.append(comment["body"])
    with open(output_file, 'w') as f:
        json.dump(data, f)
        
def sentences_convert(input_file="dataset_body.json", output_file="dataset_body_sent.json"):
    '''
    takes in paragraphs and split them into sentences
    '''
    with open(input_file, "r") as json_file:
        text_list = json.load(json_file)
    processed_data =[]
    for text in text_list:
        processed_data += sent_tokenize(text, language='english')
    with open(output_file, 'w') as f:
        json.dump(processed_data, f)
        

        
if __name__ == "__main__":
    # data_merging("dataset_vagan_cleaned.json", "dataset_vagan_health_cleaned.json", "dataset_merged_cleaned.json")
    # data_washing('dataset_merged_cleaned.json', 'dataset_cleaned.json') 
    # loading_data() 
    sentences_convert()
    