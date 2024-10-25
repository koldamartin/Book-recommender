import logging
import time
from main import job

if __name__ == "__main__":
    logging.info(f"Starting job at {time.strftime('%Y-%m-%d %H:%M:%S')}...")
    job()
    print("Job completed")
    logging.info(f"Job completed at {time.strftime('%Y-%m-%d %H:%M:%S')}...")