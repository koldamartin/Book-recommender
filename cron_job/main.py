import dotenv
import os
import time
import schedule
import pandas as pd
import boto3
import tempfile
import io
import logging
dotenv.load_dotenv()

from kaggle.api.kaggle_api_extended import KaggleApi
boto3.set_stream_logger('boto3.resources', logging.DEBUG)


# Initialize the Kaggle API client
api_key = os.getenv('KAGGLE_KEY')
api_username = os.getenv('KAGGLE_USERNAME')
api = KaggleApi()
api.authenticate()
# Set the dataset details
dataset_owner = "arashnic"
dataset_name = "book-recommendation-dataset"

# Initialize S3 client
s3 = boto3.client('s3',
                  aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                  aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))
bucket_name = 'martinbucket1'


def download_kaggle_dataset():

    try:
        # Download the dataset to temporary file
        with tempfile.TemporaryDirectory() as temporary_dir:
            api.dataset_download_files(f"{dataset_owner}/{dataset_name}", unzip=True, path=temporary_dir)
            # Upload each file in the dataset to S3
            for root, _, files in os.walk(temporary_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    s3.upload_file(file_path, bucket_name, file)
        logging.info("Dataset downloaded successfully")
    except Exception as e:
        logging.error(f"Error downloading dataset: {str(e)}")


def process_data(min_reviews: int, file_name_1, file_name_2) -> pd.DataFrame:
    # load ratings
    obj_ratings = s3.get_object(Bucket=bucket_name, Key=f"{file_name_1}.csv")
    ratings = pd.read_csv(obj_ratings["Body"], encoding='cp1251', sep=',', low_memory=False)
    ratings = ratings[ratings['Book-Rating'] != 0]

    # load books
    obj_books = s3.get_object(Bucket=bucket_name, Key=f"{file_name_2}.csv")
    books = pd.read_csv(obj_books["Body"], encoding='cp1251', sep=',', low_memory=False)

    # Merge datasets base od User-ID
    dataset = pd.merge(ratings, books, on=['ISBN'])
    dataset_lowercase = dataset.apply(lambda x: x.str.lower() if (x.dtype == 'object') else x)

    # Discard books with less than 50 reviews
    grouped = dataset_lowercase.groupby("ISBN").size()
    filtered_df = grouped[grouped > min_reviews]
    dataset_lowercase = dataset_lowercase[dataset_lowercase['ISBN'].isin(filtered_df.index)]

    return dataset_lowercase


def upload_to_s3(dataset: pd.DataFrame):
    # Save dataset_lowercase to S3 bucket
    csv_buffer = io.StringIO()
    dataset.to_csv(csv_buffer, index=False)
    s3.put_object(Bucket=bucket_name, Key="Processed_data.csv", Body=csv_buffer.getvalue())
    logging.info("DataFrame uploaded to s3")


def job():
    logging.info(f"Starting scheduler at {time.strftime('%Y-%m-%d %H:%M:%S')}...")
    download_kaggle_dataset()
    processed_data = process_data(min_reviews=50, file_name_1="Ratings", file_name_2="Books")
    upload_to_s3(processed_data)
    logging.info(f"Job completed at {time.strftime('%Y-%m-%d %H:%M:%S')}...")
