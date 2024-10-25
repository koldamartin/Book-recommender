# Book recommender - A Data engineering homework

### Schema
(Red colour is not implemented in this project)

![Alt text](diagram.jpg?raw=true "Title")
## About
- Data engineering app, that periodically loads csv datasets from Kaggle, process it and save it to S3 storage.
- Application with frontend, that recommends books, based on correlation with other book ratings
  
## Tech Stack
- Pandas, numpy, fuzzywuzzy, kaggle
- Frontend: Gradio
- Cloud storage: AWS S3 bucket
- Docker

## Cron Job for data loading
- inside the `cron_job folder`
- Create an `.env` file with Kaggle and AWS credentials
- Open the Docker desktop program.
- Create docker image with `docker build -t cron_job_image .`
- Run the container localy with `docker run -d --name cron_job_container cron_job_image`
- or deploy the container as a CRON JOB on cloud (currently not working, cron jobs cannot read .env files)


## API for predictions
- `recommender_system.py` and `app.py`
- load the app from [Huggingface-Spaces](https://huggingface.co/spaces/Wintersmith/Book_recommender) and try it yourself
