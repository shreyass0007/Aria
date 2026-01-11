import os
import time
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def start_finetuning():
    api_key = os.getenv("OPEN_AI_API_KEY")
    if not api_key:
        print("Error: OPEN_AI_API_KEY not found in .env file.")
        return

    client = OpenAI(api_key=api_key)
    file_path = "fine_tuning_dataset.jsonl"

    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    print(f"Uploading {file_path} to OpenAI...")
    try:
        # Upload the file
        file_response = client.files.create(
            file=open(file_path, "rb"),
            purpose="fine-tune"
        )
        file_id = file_response.id
        print(f"File uploaded successfully. File ID: {file_id}")

        # Wait a moment for the file to be processed
        print("Waiting for file to be processed...")
        time.sleep(5)

        # Create fine-tuning job
        print("Starting fine-tuning job...")
        job_response = client.fine_tuning.jobs.create(
            training_file=file_id,
            model="gpt-4o-mini-2024-07-18" # Using a cost-effective but capable model
        )
        
        job_id = job_response.id
        print(f"\n✅ Fine-tuning job started successfully!")
        print(f"Job ID: {job_id}")
        print(f"Model: {job_response.model}")
        print(f"Status: {job_response.status}")
        print("\nYou can monitor the status using the OpenAI dashboard or by checking the Job ID.")
        
        # Save Job ID to a file for later reference
        with open("latest_finetune_job.txt", "w") as f:
            f.write(job_id)
            
    except Exception as e:
        print(f"\nError occurred: {e}")

if __name__ == "__main__":
    start_finetuning()
