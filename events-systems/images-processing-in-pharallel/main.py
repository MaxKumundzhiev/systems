import asyncio
from fastapi import FastAPI, UploadFile, File
from concurrent.futures import ProcessPoolExecutor
from typing import List
import io

app = FastAPI()

# This will keep track of the number of processed images
processed_image_count = 0

# Create a ProcessPoolExecutor for true parallel processing of images
executor = ProcessPoolExecutor()


# Function to simulate image processing (e.g., resizing, encoding, etc.)
def process_image(image_bytes: bytes):
    # Simulate time-consuming image processing (e.g., resizing)
    import time

    time.sleep(1)  # Simulate a time delay
    update_processed_image_count()
    return len(image_bytes)  # Return size as a simple example


# Endpoint to upload multiple images
@app.post("/upload_images")
async def upload_images(files: List[UploadFile] = File(...)):
    global processed_image_count

    loop = asyncio.get_event_loop()

    # Add images to the processing queue, but don't wait for processing
    for file in files:
        image_bytes = await file.read()

        # Submit the processing task to the ProcessPoolExecutor (parallel processing)
        loop.run_in_executor(executor, process_image, image_bytes)

    # Return immediately after queuing the tasks
    return {
        "message": f"{len(files)} images uploaded successfully. Processing started."
    }


# Endpoint to get the number of processed images
@app.get("/processed_images")
async def processed_images_count():
    return {"processed_images": processed_image_count}


# This function will periodically update the processed_image_count after each task completes
def update_processed_image_count():
    global processed_image_count
    processed_image_count += 1
