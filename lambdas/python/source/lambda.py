import json
import logging
import shutil
import os

import boto3
import pylibmagic
import magic
from PIL import Image

logging.getLogger().setLevel(logging.INFO)

s3 = boto3.resource('s3')

base_path = '/tmp'
images_folder = 'images'
processed_images_folder = 'watermark'
watermark_file_name = os.getenv('WATERMARK_FILE_NAME')
allowed_mime_types = ['image/jpeg']

def handler(event, context):
    logging.info(f'Received an event: {json.dumps(event)}')
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']
        logging.info(f'Archive was uploaded to bucket {bucket} with key {object_key}')
        # Downloading object from S3
        s3.meta.client.download_file(bucket, object_key, f'{base_path}/{object_key}')
        # Unzipping file
        shutil.unpack_archive(
            f'{base_path}/{object_key}',
            f'{base_path}/{images_folder}'
        )
        # Creating list of images filenames
        file_list = []
        for file in os.listdir(f'{base_path}/{images_folder}'):
            try:
                if os.path.isfile(f'{base_path}/{images_folder}/{file}'):
                    mime_type = magic.from_file(
                        f'{base_path}/{images_folder}/{file}',
                        mime=True
                    )
                    if mime_type in allowed_mime_types:
                        file_list.append(file)
                    else:
                        raise ValueError('Wrong MIMEType!')
                else:
                    raise IsADirectoryError('Not a file!')
            except:
                continue
        # Creating folder for processed images
        if not os.path.isdir(f'{base_path}/{images_folder}/{processed_images_folder}'):
            os.mkdir(f'{base_path}/{images_folder}/{processed_images_folder}')
        s3.meta.client.download_file(
            bucket,
            watermark_file_name,
            f'{base_path}/{watermark_file_name}'
        )
        watermark = Image.open(f'{base_path}/{watermark_file_name}')
        # Adding watermark
        for file in file_list:
            # Opening main file
            image = Image.open(f'{base_path}/{images_folder}/{file}')
            # Downloading and opening watermark file
            # Adding watermark
            image.paste(watermark)
            image.save(f'{base_path}/{images_folder}/{processed_images_folder}/{file}')
            processed_image = file_list.pop()
            logging.info(f'Added watermark to image with filename: {processed_image}')
        # Making zip archive
        shutil.make_archive(
            f'{base_path}/output',
            format='zip',
            root_dir=f'{base_path}/{images_folder}/{processed_images_folder}',
        )
        # Uploading output archive to s3
        s3.meta.client.upload_file(
            f'{base_path}/output.zip',
            bucket,
            'output.zip'
        )