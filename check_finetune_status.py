import os
import time
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def update_env_file(new_model_id):
    env_path = ".env"
    if not os.path.exists(env_path):
        print("Error: .env file not found.")
        return

    try:
        with open(env_path, "r") as f:
            lines = f.readlines()

        new_lines = []
        model_updated = False
        
        for line in lines:
            if line.startswith("OPENAI_MODEL="):
                new_lines.append(f"OPENAI_MODEL={new_model_id}\n")
                model_updated = True
            else:
                new_lines.append(line)
        
        if not model_updated:
            new_lines.append(f"\nOPENAI_MODEL={new_model_id}\n")

        with open(env_path, "w") as f:
            f.writelines(new_lines)
            
        print(f"✅ Updated .env with OPENAI_MODEL={new_model_id}")
        
    except Exception as e:
        print(f"Error updating .env: {e}")

def check_status():
    api_key = os.getenv("OPEN_AI_API_KEY")
    if not api_key:
        print("Error: OPEN_AI_API_KEY not found in .env file.")
        return

    client = OpenAI(api_key=api_key)
    
    # Read job ID from file
    try:
        with open("latest_finetune_job.txt", "r") as f:
            job_id = f.read().strip()
    except FileNotFoundError:
        print("Error: latest_finetune_job.txt not found. Cannot check status.")
        return

    print(f"Checking status for Job ID: {job_id}...")
    
    try:
        job = client.fine_tuning.jobs.retrieve(job_id)
        
        print(f"\nStatus: {job.status.upper()}")
        
        if job.status == "succeeded":
            new_model_id = job.fine_tuned_model
            print(f"\n🎉 Fine-tuning complete!")
            print(f"New Model ID: {new_model_id}")
            
            # Ask to update .env
            # Since we are running in a non-interactive environment often, 
            # we will just do it or print instructions. 
            # For this script, let's automatically update it as requested by the user flow.
            print("\nUpdating .env file...")
            update_env_file(new_model_id)
            
        elif job.status == "failed":
            print(f"\n❌ Fine-tuning failed.")
            print(f"Error: {job.error}")
            
        else:
            print(f"Message: {job.object}")
            print("\nThe job is still processing. Please check again later.")
            
    except Exception as e:
        print(f"\nError checking status: {e}")

if __name__ == "__main__":
    check_status()
