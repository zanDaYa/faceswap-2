
import boto3
import sys
import os

# this file is a wrapper for Amazon AWS S3 service
# we have stored our posebin on that server
# in order to direct the request to certain bucket, please make sure
# that the .aws dir exists and well configured

S3_BUCKET_NAME = 'posebinus'
S3_BUCKET_POSEBIN_FOLDER = 'posebin_lfw_funneled'
S3_PAGE_SIZE = 100

POSEBIN_DATA_FILE = 'datafile.txt'

s3_client = \
boto3.session.Session(aws_access_key_id=os.env['AWS_KEY_ID'],
             		  aws_secret_access_key=os.env['AWS_ACCESS_KEY'],
                  	  region_name='us-east-1').client('s3')

def get_posebin_data(s3_client):
	datafile_path = S3_BUCKET_POSEBIN_FOLDER+'/'+POSEBIN_DATA_FILE
	# create a local data file
	s3_client.download_file(S3_BUCKET_NAME, datafile_path,  POSEBIN_DATA_FILE)

def get_image(posebin_id, img_name):
	tmp_path = img_name + '.png'
	img_path = S3_BUCKET_POSEBIN_FOLDER+'/'+str(posebin_id)+'/'+img_name+'.png'
	print 'downloading %s to %s ...' % (img_path, tmp_path)
	s3_client.download_file(S3_BUCKET_NAME, img_path, tmp_path)
	print 'done'
	return tmp_path

if __name__ == '__main__':
	get_posebin_data(s3_client)
