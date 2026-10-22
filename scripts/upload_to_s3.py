import os
import time
import boto3

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# Configuration
LOCAL_FOLDER = r"C:\data\to_upload"

S3_BUCKET = "student-csv-ingestion-jp"

S3_PREFIX = "uploads/"

AWS_REGION = "ap-south-1"


# Create S3 clients3
s3 = boto3.client("s3", region_name=AWS_REGION)


def upload_file(file_path):

    if not os.path.isfile(file_path):
        return

    # Wait for file copy/write to complete
    time.sleep(2)

    file_name = os.path.basename(file_path)

    s3_key = f"{S3_PREFIX}{file_name}"

    try:

        print(f"Uploading: {file_path}")

        s3.upload_file(
            file_path,
            S3_BUCKET,
            s3_key
        )

        print(f"Uploaded: s3://{S3_BUCKET}/{s3_key}")

    except Exception as e:

        print(f"Upload failed: {e}")


class FolderHandler(FileSystemEventHandler):

    def on_created(self, event):

        if not event.is_directory:
            upload_file(event.src_path)

    def on_modified(self, event):

        if not event.is_directory:
            upload_file(event.src_path)


# Check whether local folder exists
if not os.path.exists(LOCAL_FOLDER):

    print(f"Folder does not exist: {LOCAL_FOLDER}")

    exit(1)


# Create event handler
event_handler = FolderHandler()

observer = Observer()

observer.schedule(
    event_handler,
    LOCAL_FOLDER,
    recursive=True
)

# Start monitoring
observer.start()

print("S3 folder monitor started...")
print(f"Watching: {LOCAL_FOLDER}")


try:

    while True:
        time.sleep(5)

except KeyboardInterrupt:

    observer.stop()


observer.join()
