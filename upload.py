#from boto3.session import Session
import boto3

#session = Session(aws_access_key_id=AWS_ACCESS_KEY_ID, 
#        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
#        aws_default_region=AWS_DEFAULT_REGION)
#session = Session(profile_name='default')
s3 = boto3.resource('s3')

bucket = 'kahukuweather'
filename = 'temp.csv'
s3.meta.client.upload_file(Filename=filename, Bucket=bucket, Key=filename)
