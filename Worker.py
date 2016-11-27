from watson_developer_cloud import AlchemyLanguageV1
import json
import boto3
import boto
from boto import sns
from concurrent.futures import ThreadPoolExecutor
import time





REGION = 'us-west-2'
TOPIC  = 'arn:aws:sns:us-west-2:256492600394:tweett'
URL    = 'www.googhfdhdle.com'


conn = boto.sns.connect_to_region( REGION )



pub = conn.publish(topic=TOPIC, message=URL)




queueName = "tweets"
# alchemy_language = AlchemyLanguageV1(api_key='a505cc1904981e440eb6c34fd3ff4d11fe0715fa')


sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName=queueName)

arn = 'arn:aws:sns:us-east-1:207910673185:tweets'       # enter your SNS ARN here
sns = boto3.resource('sns')
platform_endpoint = sns.PlatformEndpoint(arn)


def process_tweets():
	for message in queue.receive_messages(MessageAttributeNames=['All']):
		if message.message_attributes is not None:
			# print message
			sns_doc={}
			coords = message.message_attributes.get('coordinates').get('StringValue')
			# senti_output = alchemy_language.sentiment(text = message.body)
			if True: #senti_output['status'] == 'OK':
				senti_answer = 0 # senti_output['docSentiment']
				sns_doc['coordinates']= coords
				sns_doc['sentiment'] = senti_answer
				sns_doc['text']= message.body
				# print sns_doc
				print "1:"
				snsInput = json.dumps(sns_doc)
				#Uncomment this after figuring out SNS

				print "2:"
				pub = conn.publish(topic=TOPIC, message=snsInput)
				# response = platform_endpoint.publish(Message=snsInput,Subject='tweets')
				time.sleep(1)
				print pub

				print "4"
			else:
				print ""
				# print('Error in sentiment analysis calcultion ', senti_output['statusInfo'])
			message.delete()

def main():
    #process_tweets()
    executor = ThreadPoolExecutor(max_workers=1)
    while True:
        executor.submit(process_tweets)

if __name__ == '__main__':
    main()