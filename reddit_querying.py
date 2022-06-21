from psaw import PushshiftAPI
import praw
import praw.exceptions as excep
import datetime as dt
import json
# import logging

### Create praw object
reddit = praw.Reddit("Fan", ratelimit_seconds=10)

### Create Pushshift API with praw object
push_api_with_praw = PushshiftAPI(reddit)
### Create Pushshift API without praw object, directly return a dictionary
push_api = PushshiftAPI()

def querying_comments_with_praw(query, start_epoch, end_epoch, api=push_api_with_praw):
    comments_list = list(api.search_comments(q=query, 
                                       after=start_epoch, before=end_epoch,
                                       # subreddit='politics',
                                       # filter=['url','author', 'title', 'subreddit'],
                                       limit=20))

    submission_list = list()

    for comment in comments_list:
        if not comment.link_id == [subm for subm in submission_list]:
            submission_list.append(comment.link_id)  ### submission id with 't3_' prefix
        
    target = list()

    for count, submission in enumerate(reddit.info(fullnames=submission_list)):
        for subm in target:
            if subm['id'] == submission.id:
                continue
        
        subm = dict()
        subm['id'] = submission.id
        subm['title'] = submission.title
        try:
            subm['author'] = submission.author.id
        except AttributeError:
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
        target.append(subm)
        print('The ' + str(count+1) + ' submission has been successfully downloaded!')
    with open('data.json', 'w') as f:
        json.dump(target, f)

def querying_submissions_with_praw(query, start_epoch, end_epoch, api=push_api_with_praw):
    submission_list = [f't3_{id}' for id in api.search_submissions(q=query, 
                                                                   after=start_epoch, before=end_epoch,
                                                                   limit=50)]
        
    target = list()

    for count, submission in enumerate(reddit.info(fullnames=submission_list)):
        for subm in target:
            if subm['id'] == submission.id:
                continue
        
        subm = dict()
        subm['id'] = submission.id
        subm['title'] = submission.title
        try:
            subm['author'] = submission.author.id
        except AttributeError:
            subm['author'] = 'deleted'
        subm['created_utc'] = str(dt.datetime.fromtimestamp(submission.created_utc))
        subm['body'] = submission.selftext
        subm['score'] = submission.score
        try:
            submission.comments.replace_more(limit=None)
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
        target.append(subm)
        print('The ' + str(count+1) + ' submission has been successfully downloaded!')
    with open(dt.datetime.now().strftime('%Y_%m_%d_%H_%M') + '_data.json', 'w') as f:
        json.dump(target, f)

def querying_with_psaw(query, start_epoch, end_epoch, api=push_api):
    comments_list = list(api.search_comments(q=query, 
                                       after=start_epoch, before=end_epoch,
                                       filter='link_id',
                                       limit=20))
    submission_list = [comment.link_id.removeprefix('t3_') for comment in comments_list]
    
    return submission_list

start_epoch = int(dt.datetime(2021, 6, 1).timestamp())
end_epoch = int(dt.datetime(2022, 6, 1).timestamp())
query = '"social robot"' # Use quotation in string to do exact search


# querying_comments_with_praw(query, start_epoch, end_epoch)
querying_submissions_with_praw(query, start_epoch, end_epoch)
    

# for count, comment in enumerate(comments_list):
#     ### Get the submission target comment belonging to
#     submission = comment.submission
    
#     ### Stop redundant data
#     for subm in target:
#         if subm['id'] == submission.id:
#             continue
    
#     subm = dict()
#     subm['id'] = submission.id
#     subm['title'] = submission.title
#     try:
#         subm['author'] = submission.author.id
#     except AttributeError:
#         subm['author'] = 'deleted'
#     subm['created_utc'] = str(dt.datetime.fromtimestamp(submission.created_utc))
#     subm['body'] = submission.is_self
#     subm['score'] = submission.score
#     try:
#         submission.comments.replace_more(limit=1)
#     except excep.DuplicateReplaceException:
#         print('Exception occured, comments are updated!')
            
#     comm_list = list()
#     for comment in submission.comments.list():
#         comm = dict()
#         comm['id'] = comment.id
#         if comment.parent_id.startswith('t1_'):
#             comm['parent_id'] = comment.parent_id.removeprefix('t1_')
#         else:
#             comm['parent_id'] = comment.parent_id.removeprefix('t3_')
#         try:
#             comm['author'] = comment.author.id
#         except AttributeError:
#             comm['author'] = 'deleted'
#         comm['created_utc'] = str(dt.datetime.fromtimestamp(comment.created_utc))
#         comm['body'] = comment.body
#         comm['score'] = comment.score
#         comm_list.append(comm)
#     subm['comments'] = comm_list
#     target.append(subm)
#     print('The ' + str(count+1) + ' submission has been successfully downloaded!')
