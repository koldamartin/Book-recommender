import gradio as gr
import pandas as pd
import boto3
import dotenv
import os
import logging

from recommender_system import match_books, recommend_books

dotenv.load_dotenv()
boto3.set_stream_logger('boto3.resources', logging.DEBUG)

# Initialize S3 client and load data
s3 = boto3.client('s3',
                  aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                  aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                  region_name=os.getenv('AWS_REGION'))
bucket_name = 'martinbucket1'
obj_data = s3.get_object(Bucket=bucket_name, Key="Processed_data.csv")
dataframe = pd.read_csv(obj_data["Body"], encoding='cp1251', sep=',', low_memory=False)


def recommend_books_interface(selected_book) -> tuple:
    matched_title = match_books(selected_book, dataframe)
    if matched_title:
        correlations_df = recommend_books(dataframe, matched_title)
        message = f"Recommending these books based on your interest in: {matched_title}"
        return correlations_df, message
    else:
        return pd.DataFrame({"Error": ["No matching book found"]}), "No books found"


# Gradio interface
inputs = gr.Textbox(lines=1, placeholder="Type a book title here...")
message_output = gr.Markdown()
outputs = gr.Dataframe()

demo = gr.Interface(fn=recommend_books_interface, inputs=inputs, outputs=[outputs, message_output],
                    title="Book Recommender System",
                    description="Enter a book title to get recommendations based on similarity.",
                    fill_width=True,
                    flagging_mode='never',
                    theme=gr.themes.Soft())


if __name__ == "__main__":
    demo.launch(share=True)
