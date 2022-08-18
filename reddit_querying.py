from psaw import PushshiftAPI
import praw
import praw.exceptions as excep
import prawcore
import datetime as dt
import json
# import logging

### Create praw object
reddit = praw.Reddit("Fan", ratelimit_seconds=10)

### Create Pushshift API with praw object
push_api_with_praw = PushshiftAPI(reddit)
### Create Pushshift API without praw object, directly return a dictionary
# push_api = PushshiftAPI()

class RedditQuery:
    def __init__(self, query, start_epoch, end_epoch, api=push_api_with_praw, limit=1000):
        self.query = query
        self.start_epoch = start_epoch
        self.end_epoch = end_epoch
        self.api = api
        self.limit = limit
        self.target = list()
        
    def querying_comments_with_praw(self):
        ### Querying comments with specific target words
        comments_list = list(self.api.search_comments(q=self.query, 
                                        after=self.start_epoch, before=self.end_epoch,
                                        # subreddit='politics',
                                        limit=self.limit))

        submission_list = list()

        for comment in comments_list:
            if not comment.link_id == [subm for subm in submission_list]:
                submission_list.append(comment.link_id)  ### submission id with 't3_' prefix

        for count, submission in enumerate(reddit.info(fullnames=submission_list)):
            ### Skip redundant submissions
            for subm in self.target:
                if subm['id'] == submission.id:
                    continue
            
            subm = dict()
            subm['id'] = submission.id
            subm['title'] = submission.title
            try:
                subm['author'] = submission.author.id
            except (prawcore.exceptions.NotFound, AttributeError):
                subm['author'] = 'deleted'
            subm['created_utc'] = str(dt.datetime.fromtimestamp(submission.created_utc))
            subm['body'] = submission.selftext
            subm['score'] = submission.score
            try:
                submission.comments.replace_more(limit=1)
            except excep.DuplicateReplaceException:
                print('Exception occured, comments are updated!')
                
            comm_list = list()
            for comment in submission.comments.list():
                comment.refresh()
                comm = dict()
                comm['id'] = comment.id
                if comment.parent_id.startswith('t1_'):
                    comm['parent_id'] = comment.parent_id.removeprefix('t1_')
                else:
                    comm['parent_id'] = comment.parent_id.removeprefix('t3_')
                try:
                    comm['author'] = comment.author.id
                except AttributeError:
                    comm['author'] = 'deleted'
                comm['created_utc'] = str(dt.datetime.fromtimestamp(comment.created_utc))
                comm['body'] = comment.body
                comm['score'] = comment.score
                comm_list.append(comm)
            subm['comments'] = comm_list
            self.target.append(subm)
            print('The ' + str(count+1) + ' submission has been successfully downloaded!')
            if (count+1)%1000 == 0:
                self.save_json_file()
        self.save_json_file()

    def querying_submissions_with_praw(self):
        ### Querying submission id with specific target words
        submission_list = [f't3_{id}' for id in self.api.search_submissions(q=self.query, 
                                                                    after=self.start_epoch, before=self.end_epoch,
                                                                    limit=self.limit)]

        for count, submission in enumerate(reddit.info(fullnames=submission_list)):
            
            subm = dict()
            subm['id'] = submission.id
            subm['title'] = submission.title
            try:
                subm['author'] = submission.author.id
            except (prawcore.exceptions.NotFound, AttributeError):
                subm['author'] = 'deleted'
            subm['created_utc'] = str(dt.datetime.fromtimestamp(submission.created_utc))
            subm['body'] = submission.selftext
            subm['score'] = submission.score
            try:
                submission.comments.replace_more(limit=None)
            except excep.DuplicateReplaceException:
                print('Exception occured due to comments updated!')
                
            comm_list = list()
            for comment in submission.comments.list():
                try:
                    comment.refresh()
                except (excep.ClientException, prawcore.exceptions.ServerError):
                    print('This comment does not appear to be in the comment tree')
                comm = dict()
                comm['id'] = comment.id
                if comment.parent_id.startswith('t1_'):
                    comm['parent_id'] = comment.parent_id.removeprefix('t1_')
                else:
                    comm['parent_id'] = comment.parent_id.removeprefix('t3_')
                try:
                    comm['author'] = comment.author.id
                except (prawcore.exceptions.NotFound, AttributeError):
                    comm['author'] = 'deleted'
                comm['created_utc'] = str(dt.datetime.fromtimestamp(comment.created_utc))
                comm['body'] = comment.body
                comm['score'] = comment.score
                comm_list.append(comm)
            subm['comments'] = comm_list
            self.target.append(subm)
            print('The ' + str(count+1) + ' submission has been successfully downloaded!')
            if (count+1)%1000 == 0:
                self.save_json_file()
        self.save_json_file()  

    def save_json_file(self):
        with open(dt.datetime.now().strftime('%Y_%m_%d_%H_%M') + '_data.json', 'w') as f:
            json.dump(self.target, f)
        

start_epoch = int(dt.datetime(2017, 1, 1).timestamp())
end_epoch = int(dt.datetime(2022, 7, 20).timestamp())
### query for social robot
# query = '"chatbot" | | "virtual assistant" 
query = '"service bot" | "conversational modelling" | "conversational system" | "conversation system" | "conversational entities" | "conversational agents" | "virtual agent" | "intelligent agent"' # Use quotation in string to do exact search, use | do or search
### query for vegan food
# query = '"vegan" | "veganism" | "vegetarian"'


# querying_comments_with_praw(query, start_epoch, end_epoch)
search = RedditQuery(query, start_epoch, end_epoch, limit=5000)
search.querying_submissions_with_praw()