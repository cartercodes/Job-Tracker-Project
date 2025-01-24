import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from dotenv import load_dotenv
import os
import json
import logging
from colorama import Fore, init
import openai
from openai import OpenAI
import requests
from bs4 import BeautifulSoup
import sys

# Initialize Colorama
init(autoreset=True)

# Configure the logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("job_tracker.log"),
        logging.StreamHandler()  # Print logs to the console
    ]
)

# Load environment variables
load_dotenv()

# Retrieve OpenAI API Key from the environment
try:
    openai.api_key = os.getenv("openai_key")
    if not openai.api_key:
        logging.critical(Fore.RED + "Error: OpenAI key not found. Please add your key to the .env file.")
        exit()
    logging.info(Fore.GREEN + "OpenAI API key successfully loaded.")
except Exception as e:
    logging.error(Fore.RED + f"Failed to load OpenAI API key. Details: {e}")
    exit()
    
# Set up Google Sheets API credentials
try:
    json_file = "credentials.json"
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_file, scope)
    # Authorize and connect to Google Sheets
    client = gspread.authorize(creds)
    sheet = client.open("Job Tracker").worksheet("job_tracker_1")  # Replace with your sheet name
    logging.info(Fore.GREEN + "Successfully connected to Google Sheets.")
except FileNotFoundError:
    logging.warning(Fore.RED + "Error: file not found or path is wrong. Please add the correct file and try again.")
    exit()
except Exception as e:
    logging.critical(Fore.RED + f"Error: Failed to connect to Google Sheets. Details: {e}")
    exit()

# Retry operation helper
def retry_operation(func, *args, **kwargs):
    retries = 3
    for attempt in range(retries):
        try:
            func(*args, **kwargs)
            return
        except Exception as e:
            logging.error(Fore.YELLOW + f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                logging.info(Fore.CYAN + "Retrying...")
            else:
                logging.critical(Fore.RED + "All attempts failed.")
                raise

# Function to add a job entry
def add_entry(company, position, date_applied, status, notes=""):
    try:
        if not company or not position:
            raise ValueError("Company name and position title cannot be empty.")
        sheet.append_row([date_applied, company, position, status, "", "", notes])
        logging.info(Fore.GREEN + f"Added application for {position} at {company}.")
    except Exception as e:
        logging.error(Fore.RED + f"Failed to add job entry for {company}. Details: {e}")

# Function to update a job's status
def update_status(company, new_status):
    try:
        if not company or not new_status:
            raise ValueError("Company name and status cannot be empty.")
        records = sheet.get_all_records()
        for idx, record in enumerate(records, start=2):  # Skip the header row
            if record["Company Name"].strip().lower() == company.strip().lower():
                sheet.update_cell(idx, 4, new_status)  # Update 'App Status' column
                logging.info(Fore.GREEN + f"Updated status for {company} to {new_status}.")
                return
        logging.warning(Fore.YELLOW + f"Company {company} not found.")
    except Exception as e:
        logging.error(Fore.RED + f"Failed to update job status for {company}. Details: {e}")

# Function to update interview date
def update_interview_date(company, interview_date):
    try:
        datetime.strptime(interview_date, "%Y-%m-%d")  # Validate date format
        records = sheet.get_all_records()
        for idx, record in enumerate(records, start=2):  # Skip the header row
            if record["Company Name"].strip().lower() == company.strip().lower():
                sheet.update_cell(idx, 5, interview_date)  # Update 'Interview Date' column
                logging.info(Fore.GREEN + f"Updated interview date for {company} to {interview_date}.")
                return
        logging.warning(Fore.YELLOW + f"Company {company} not found.")
    except ValueError:
        logging.error(Fore.RED + "Invalid date format. Please use YYYY-MM-DD.")
    except Exception as e:
        logging.error(Fore.RED + f"Failed to update interview date for {company}. Details: {e}")

# Function to update offer details
def update_offer_details(company, offer_details):
    try:
        if not company or not offer_details:
            raise ValueError("Company name and offer details cannot be empty.")
        records = sheet.get_all_records()
        for idx, record in enumerate(records, start=2):  # Skip the header row
            if record["Company Name"].strip().lower() == company.strip().lower():
                sheet.update_cell(idx, 6, offer_details)  # Update 'Offer' column
                logging.info(Fore.GREEN + f"Updated offer details for {company} to {offer_details}.")
                return
        logging.warning(Fore.YELLOW + f"Company {company} not found.")
    except Exception as e:
        logging.error(Fore.RED + f"Failed to update offer details for {company}. Details: {e}")

# Function to update notes
def update_notes(company, notes):
    try:
        if not company or not notes:
            raise ValueError("Company name and notes cannot be empty.")
        records = sheet.get_all_records()
        for idx, record in enumerate(records, start=2):  # Skip the header row
            if record["Company Name"].strip().lower() == company.strip().lower():
                sheet.update_cell(idx, 7, notes)  # Update 'Notes' column
                logging.info(Fore.GREEN + f"Updated notes for {company} to {notes}.")
                return
        logging.warning(Fore.YELLOW + f"Company {company} not found.")
    except Exception as e:
        logging.error(Fore.RED + f"Failed to update notes for {company}. Details: {e}")

def fetch_job_description(url):
    try:
        # Fetch the page content
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse the page with BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract visible text
        visible_text = "\n".join([line.strip() for line in soup.get_text().splitlines() if line.strip()])

        # Extract JSON data from <script> tags
        json_data = []
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                json_data.append(json.loads(script.string))
            except (json.JSONDecodeError, TypeError):
                continue

        # Return structured data
        return {
            "html": soup.prettify(),
            "visible_text": visible_text,
            "json_data": json_data
        }

    except requests.exceptions.RequestException as e:
        logging.error(Fore.RED + f"Failed to fetch URL: {url}. Details: {e}")
        return None
    except Exception as e:
        logging.error(Fore.RED + f"An unexpected error occurred. Details: {e}")
        return None

    
def parse_job_description(data):
    try:
        if not openai.api_key:
            raise ValueError("OpenAI key not found or is not set.")

        # Extract raw components
        visible_text = data.get("visible_text", "")

        # Prepare OpenAI request
        messages = [
            {"role": "system", "content": "You are a helpful assistant that extracts and summarizes job information."},
            {
                "role": "user",
                "content": (
                    f"Analyze the provided job description and extract the following:\n"
                    f"1. Company Name\n"
                    f"2. Job Title\n"
                    f"3. Job Location Type (Remote, Hybrid, or Onsite)\n"
                    f"4. Summary of the Position\n"
                    f"5. Required Skills, Technology Stack or Experience needed (summarized)\n"
                    f"6. Benefits Summary (list key benefits offered, 401K, types of insurance offered, if mentioned (summarized))\n"
                    f"7. Application Deadline (if mentioned)\n"
                    f"8. Salary or Compensation (if mentioned)\n\n"
                    f"Data:\n{visible_text}\n\n"
                    f"Provide the details in the following structured format:\n"
                    f"Company Name: <company name>\n"
                    f"Job Title: <job title>\n"
                    f"Job Location Type: <Remote/Hybrid/Onsite>\n"
                    f"Position Summary: <summary of the position>\n"
                    f"Skills/Technology Stack: <skills or technologies>\n"
                    f"Benefits Summary: <benefits summary>\n"
                    f"Application Deadline: <deadline>\n"
                    f"Salary: <salary or compensation>"
                ),
            },
        ]

        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0,
        )

        # Extract the assistant's response
        parsed_details = response.choices[0].message.content.strip()
        logging.info(Fore.GREEN + "Successfully parsed job description.")
        return parsed_details

    except Exception as e:
        logging.error(Fore.RED + f"Failed to parse job description. Details: {e}")
        return None

    
def add_parsed_details_to_sheet(parsed_details):
    try:
        details = {}
        for line in parsed_details.split('\n'):
            key, _, value = line.partition(':')
            details[key.strip()] = value.strip()

        company = details.get("Company Name", "")
        position = details.get("Job Title", "")
        location_type = details.get("Job Location Type", "")  # Consolidated column
        summary = details.get("Position Summary", "")
        skills = details.get("Skills/Technology Stack", "")
        benefits = details.get("Benefits Summary", "")  # New field for benefits
        deadline = details.get("Application Deadline", "")
        salary = details.get("Salary", "")
        date_applied = datetime.now().strftime("%Y-%m-%d")

        if not company or not position:
            raise ValueError("Company name and job title are required.")

        # Append details to the Google Sheet
        sheet.append_row([
            date_applied,
            company,
            position,
            salary,
            skills,
            benefits,  # Added benefits summary column
            location_type,  # Consolidated column for Remote/Hybrid/Onsite
            "Applied",
            "",
            "",
            summary,
            deadline
        ])
        logging.info(Fore.GREEN + f"Added parsed job details for {company}.")
    except Exception as e:
        logging.error(Fore.RED + f"Failed to add parsed details to Google Sheets. Details: {e}")

def delete_job(company):
    try: 
        if not company or not company.strip():
            raise ValueError("Company name cannot be empty or whitespace.")
        
        records = sheet.get_all_records()
        for idx, record in enumerate(records, start=2):  # Start at row 2 to skip the header
            if record["Company Name"].strip().lower() == company.strip().lower():
                sheet.delete_rows(idx)  # Correct method to delete the row using its index
                logging.info(Fore.GREEN + f"Deleted {company} from the job tracker.")
                return
        
        logging.warning(Fore.YELLOW + f"Company {company} not found in the job tracker.")
    except Exception as e:
        logging.error(Fore.RED + f"Failed to delete {company} from the job tracker. Details: {e}")

# Main interactive script
if __name__ == "__main__":
    logging.info(Fore.CYAN + "Job Tracker started.")
    print(Fore.CYAN + "Welcome to the Job Tracker!")
    try:
        while True:
            action = input(Fore.CYAN + "Do you want to (add), (update_status), (update_date), (update_offer), (update_notes), (delete), (add_from_url), or (add_from_text)? Type 'exit' to quit: ").lower()
            if action == "exit":
                logging.info(Fore.GREEN + "Exiting Job Tracker.")
                logging.info(Fore.GREEN + "Shutting down the application.")
                print(Fore.GREEN + "Goodbye!")
                break
            elif action == "add":
                company = input(Fore.CYAN + "Enter the company name: ").strip()
                position = input(Fore.CYAN + "Enter the position title: ").strip()
                date_applied = datetime.now().strftime("%Y-%m-%d")
                status = "Applied"
                notes = input(Fore.CYAN + "Any additional notes? (Press Enter to skip): ").strip()
                retry_operation(add_entry, company, position, date_applied, status, notes)
            elif action == "update_status":
                company = input(Fore.CYAN + "Enter the company name: ").strip()
                new_status = input(Fore.CYAN + "Enter the new status (e.g., Interview, Denied, Offer): ").strip()
                retry_operation(update_status, company, new_status)
            elif action == "update_date":
                company = input(Fore.CYAN + "Enter the company name: ").strip()
                interview_date = input(Fore.CYAN + "Enter the interview date (YYYY-MM-DD): ").strip()
                retry_operation(update_interview_date, company, interview_date)
            elif action == "update_offer":
                company = input(Fore.CYAN + "Enter the company name: ").strip()
                offer_details = input(Fore.CYAN + "Enter the offer details: ").strip()
                retry_operation(update_offer_details, company, offer_details)
            elif action == "update_notes":
                company = input(Fore.CYAN + "Enter the company name: ").strip()
                notes = input(Fore.CYAN + "Enter the new notes: ").strip()
                retry_operation(update_notes, company, notes)
            elif action == "add_from_url":
                url = input(Fore.CYAN + "Enter the URL of the job description: ").strip()
                if not url:
                    logging.error(Fore.RED + "Invalid input: URL cannot be empty.")
                    continue
                # Step 1: Fetch job data
                data = fetch_job_description(url)
                # Step 2: Parse job details
                if data:
                    parsed_details = parse_job_description(data)

                    # Step 3: Add parsed details to the Google Sheet
                    if parsed_details:
                        add_parsed_details_to_sheet(parsed_details)
            elif action == "add_from_text":
                print(Fore.CYAN + "Paste the entire job description below. Type 'DONE' on a new line to finish:")

                # Initialize a list to capture lines of input
                job_description_lines = []

                while True:
                    # Capture input line by line
                    line = input()
                    if line.strip().upper() == "DONE":  # Check for termination keyword
                        break
                    job_description_lines.append(line)

                # Combine all lines into a single string
                job_description = "\n".join(job_description_lines).strip()

                if not job_description:
                    logging.error(Fore.RED + "Invalid input: Job description cannot be empty.")
                    continue

                # Step 1: Parse job details
                parsed_details = parse_job_description({"visible_text": job_description, "json_data": []})

                # Step 2: Add parsed details to the Google Sheet
                if parsed_details:
                    add_parsed_details_to_sheet(parsed_details)
            elif action == "delete":
                company = input(Fore.CYAN + "Enter the company name: ").strip()
                retry_operation(delete_job, company)
            else:
                logging.warning(Fore.YELLOW + "Invalid option selected.")
                print(Fore.YELLOW + "Invalid option. Please choose 'add', 'delete', 'update_status', 'update_date', 'update_offer','update_notes', 'add_from_url', or 'add_from_text'.")
    except KeyboardInterrupt:
        logging.info(Fore.YELLOW + "User interrupted the program with Ctrl+C.")
        print(Fore.YELLOW + "\nGoodbye!")
    except Exception as e:
        logging.critical(Fore.RED + f"Unexpected error in main loop: {e}")