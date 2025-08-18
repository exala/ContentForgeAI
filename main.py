# File: /content_automation/main.py

import pandas as pd
import asyncio
import time

# Import the functions from our new 'content_system' package
from modules import (
    generate_content_async,
    prompt_orchestrator,
    post_processor,
    article_storage_manager
)

def load_topics_from_excel(file_path: str, column_name: str) -> list:
    """Loads topics from a specified column in an Excel file."""
    try:
        df = pd.read_excel(file_path)
        if column_name not in df.columns:
            print(f"Error: Column '{column_name}' not found in {file_path}.")
            return []
        return df[column_name].dropna().tolist()
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return []
    except Exception as e:
        print(f"An error occurred while reading the Excel file: {e}")
        return []

# --- NEW: Asynchronous Worker Function ---
async def process_single_topic(topic: str, semaphore: asyncio.Semaphore):
    """
    Defines the full async workflow for a single topic, controlled by a semaphore.
    """
    async with semaphore: # This will wait until a "slot" is free
        print(f"Processing topic: '{topic}'")

        # 1. Build the prompt (sync, fast)
        prompt = prompt_orchestrator(topic)

        # 2. Generate content (async, slow)
        raw_content = await generate_content_async(prompt, topic)
        if not raw_content:
            print(f"Failed to generate content for '{topic}'. Skipping.")
            return # Exit this task

        # 3. Process and format (sync, fast)
        title, html_content = post_processor(raw_content)

        # 4. Store the article (sync, fast)
        # Note: Database writes can be blocking. For extreme scale, you might
        # use an async database driver, but for now, this is fine.
        article_storage_manager(title, html_content, topic)

# --- UPDATED: Main function is now async ---
async def main():
    """The main async function to run the content generation pipeline."""
    # --- Configuration ---
    EXCEL_FILE_PATH = "topics.xlsx"
    TOPIC_COLUMN_NAME = "Topics"
    # Set how many articles to generate at the same time.
    # Start with a lower number (e.g., 10-25) and increase carefully.
    CONCURRENT_LIMIT = 10

    # 1. Load topics
    topics = load_topics_from_excel(EXCEL_FILE_PATH, TOPIC_COLUMN_NAME)
    if not topics:
        print("No topics found. Exiting.")
        return

    # Create a semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(CONCURRENT_LIMIT)

    print(f"--- Starting async content generation for {len(topics)} topics ---")
    print(f"--- Concurrency limit set to {CONCURRENT_LIMIT} tasks ---")
    start_time = time.time()

    # 2. Create a list of tasks to run
    tasks = [process_single_topic(topic, semaphore) for topic in topics]

    # 3. Run all tasks concurrently
    await asyncio.gather(*tasks)

    end_time = time.time()
    print("-" * 50)
    print("Asynchronous content generation process finished.")
    print(f"Total time taken: {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    # Use asyncio.run() to execute the async main function
    asyncio.run(main())