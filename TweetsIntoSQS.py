from elasticsearch import Elasticsearch
import tweepy
import time
import boto3
import json
# Retrieve tweet text, id, coordinates, user, user id, time, number of re-tweet, number of liked

# consumer_key="sfdO3gvj4zJnETO9CEQUMdone"
# consumer_secret="rgmvdcRB1tnCCuTQYSLraQlIGyV7kBsPJACRkJ3onzzVbByD5u"
# access_token="789732948014665728-Jy1V5z1yH6S6ZFn2lOl1lTLHKofVXpC"
# access_token_secret="pxpC4pRRoDR7syZph7UDqFA7PnHS3OlX7eWCLVdxGp1gE"


consumer_key = "UQdmHGVPgZVQ62xYp7Ra48Unl"

consumer_secret = "iakx9dqpGnp9WyKhv7jCJ6U2ePAplcyEpxCiwQVxlOd1a7atUr"

access_token = "246909929-804KKzEDQS4vG3pCuOKnzrlge0WBfbFATuy58hTt"

access_token_secret = "Lw9LKTzR80FWuNk20nJelepmHy1SsPauYd84WIxb76fl3"




auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Authentication
api = tweepy.API(auth)
# Add location search to India
places = api.geo_search(query="United States", granularity="country")
place_id = places[0].id

queueName = "tweets"

# Get the service resource
sqs = boto3.resource('sqs')
# Create/Get the SQS Queue instance
queue = sqs.create_queue(QueueName=queueName)

while True:
		data = api.search(q="place:%s" % place_id, count = 300)
		for singleTweet in data:
			try:
				if not singleTweet.coordinates:
					continue
				if singleTweet.lang != "en":
					continue
				tweet_text = singleTweet.text
				tweet_text_filtered = ''.join(i for i in tweet_text if ord(i)<128 and ord(i) > 65 or ord(i) == 32 )
				#tweet_doc['user-name'] = singleTweet.user.name
				#tweet_doc['user-id'] = singleTweet.user.id
				#tweet_doc['hashtag'] = [hashtag['text'] for hashtag in singleTweet.entities['hashtags']]
				#tweet_doc['coordinates'] = singleTweet.coordinates['coordinates']
				tweet_place = ''
				if singleTweet.place:
					tweet_place = singleTweet.place.full_name
				tweet_created_at = ''
				if singleTweet.created_at:
					tweet_created_at = singleTweet.created_at.strftime("%Y-%m-%d %H:%M:%S")
				#tweet_doc['retweet-count'] = singleTweet.retweet_count
				#tweet_doc['favorite-count'] = singleTweet.favorite_count
				msgAttr = {
					"user_name": {
						'StringValue': singleTweet.user.name,
						'DataType' : 'String'
					},
					"coordinates":{
						'StringValue': json.dumps(singleTweet.coordinates),
						'DataType': 'String'
					},
					"place":{
						'StringValue':tweet_place,
						'DataType':'String'
					},
					"created-at":{
						'StringValue': tweet_created_at,
						'DataType':'String'
					}
				}
				print "Sending msg of location ", singleTweet.coordinates
				response = queue.send_message(MessageBody= tweet_text_filtered, MessageAttributes=msgAttr)
				print response.get('MessageId')
				print(response.get('Failed'))
				time.sleep(1)
			except Exception, e:				
				time.sleep(1)
				print e
				pass
				
					
