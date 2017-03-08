import os, sys
import requests
import boto3
from credstash import getSecret

#os.environ["AWS_PROFILE"] = "mcallb"

youtube_api_key = getSecret('youtube-api-key')

url = 'https://www.googleapis.com/youtube/v3/search'
headers = {'Cache-Control': 'no-cache'}
payload = {
  'part':      'snippet,id',
  'channelId': 'UCe3yFIa92jfAHEu4Ql4u69A',
  'type':      'video',
  'eventType': 'live',
  'key':       youtube_api_key
}

def send_sqs_message(message):
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='youtube_stream_status')
    response = queue.send_message(MessageBody=message)

def read_sqs_messages():
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='youtube_stream_status')
    messages = queue.receive_messages()
    for message in messages:
        print message.body
    message.delete()

def lambda_handler(event, context):
    try:
        r = requests.get(url, params=payload, headers=headers)
    except requests.exceptions.RequestException as e:
        print e
        sys.exit(1)

    parsed_json = r.json()

    if r.status_code <> 200:
        print 'Something bad happened status code: %s' % (r.status_code)
        sys.exit(1)
    else:

        try:
            # The stream is live
            parsed_json['items'][0]['snippet']['liveBroadcastContent']
            send_sqs_message("live")
        except IndexError:
            # The stream is down
            send_sqs_message("down")

    #read_sqs_messages()