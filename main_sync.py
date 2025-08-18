# File: /content_automation/main.py

import pandas as pd
import time

# Import the functions from our new 'content_system' package
from modules import (
    generate_content,
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

def main():
    """The main function to run the automated content generation pipeline."""
    # Configuration
    EXCEL_FILE_PATH = "topics.xlsx"
    TOPIC_COLUMN_NAME = "Topics"

    # 1. Load topics from the external Excel file
    topics = load_topics_from_excel(EXCEL_FILE_PATH, TOPIC_COLUMN_NAME)
    if not topics:
        print("No topics found. Exiting.")
        return

    print(f"--- Starting content generation for {len(topics)} topics ---")

    # The main workflow orchestrator
    for topic in topics:
        time.sleep(2)
        print("-" * 50)
        print(f"Processing topic: '{topic}'")

        # 2. Build the prompt (from generation module)
        prompt = prompt_orchestrator(topic)

        # 3. Generate the raw content (from generation module)
        raw_content = generate_content(prompt)
        if not raw_content:
            print(f"Failed to generate content for '{topic}'. Skipping.")
            continue

        # 4. Process and format the content (from processing module)
        title, html_content = post_processor(raw_content)

        # 5. Store the final article (from storage module)
        article_storage_manager(title, html_content, topic)

    print("-" * 50)
    print("Content generation process finished.")
    time.sleep(2)

if __name__ == "__main__":
    main()