# Job Application Tracker

## Overview

The **Job Application Tracker** is a Python-based application designed to streamline the process of tracking job applications. It allows users to log job details, update statuses, and even parse job descriptions from URLs using OpenAI's GPT-4 Turbo. The application integrates with Google Sheets to store and manage job application data securely.

---

## Features

- **Add Job Applications**: Log new job applications with company name, position, and other relevant details.
- **Update Job Details**:
  - Change the application status (e.g., Applied, Interview, Offer).
  - Add or update interview dates.
  - Record offer details and additional notes.
- **Parse Job Descriptions**:
  - Fetch job descriptions from URLs and extract key information using OpenAI's GPT-4 Turbo.
- **Delete Applications**: Remove job entries directly from the Google Sheet.
- **Google Sheets Integration**: All data is stored and managed via a connected Google Sheet.
- **Error Handling & Logging**: Comprehensive error handling with detailed logs for troubleshooting.

---
## 2. Install Dependencies

Ensure you have Python 3.7 or higher installed. Then, install the required libraries:

```bash
pip install -r requirements.txt
```

## 3. Setup Google Sheets API

1. Create a Google Cloud project and enable the Google Sheets and Drive APIs.
2. Generate a `credentials.json` file for the service account.
3. Place the `credentials.json` file in the project root.

## 4. Setup Environment Variables

Create a `.env` file in the project root with the following content:

```env
openai_key=your_openai_api_key
```

Replace `your_openai_api_key` with your OpenAI API key.

## 5. Update `.gitignore`

Ensure sensitive files like `.env` and `credentials.json` are excluded from version control:

```plaintext
# Ignore environment variables and credentials
.env
credentials.json
```

## Usage

### Run the Application

```bash
python job_tracker.py
```

### Interactive Options

- `add`: Add a job application.
- `update_status`: Update the application status (e.g., Interview, Offer, Denied).
- `update_date`: Add or update an interview date.
- `update_offer`: Record offer details.
- `update_notes`: Add or update additional notes for an application.
- `delete`: Delete a job application from the tracker.
- `add_from_url`: Parse a job description from a URL and add details to the tracker.

### Google Sheet Format

| Date Applied | Company Name | Job Title | App Status | Interview Date | Offer Details | Notes | Summary | Required Skills | Application Deadline |
|--------------|--------------|-----------|------------|----------------|---------------|-------|---------|-----------------|-----------------------|

The application automatically appends new rows with the appropriate format.

## Dependencies

### Python Libraries:

- `gspread`
- `oauth2client`
- `openai`
- `dotenv`
- `requests`
- `bs4` (BeautifulSoup)
- `colorama`

### APIs:

- OpenAI GPT-4 Turbo
- Google Sheets API

## Logs

Logs are stored in a `job_tracker.log` file in the project root. They include detailed timestamps and messages for debugging and tracking application events.

## Security

- Ensure that the `.env` and `credentials.json` files are never shared or uploaded to a public repository.
- Use `.gitignore` to exclude sensitive files from version control.

## Future Enhancements

- Add support for exporting reports (e.g., CSV or PDF) summarizing application statuses.
- Implement email notifications for upcoming interviews or status changes.
- Enhance parsing capabilities with AI models to handle diverse job description formats.

## Contributing

1. Fork the repository.
2. Create a new branch for your feature/bugfix.
3. Submit a pull request with detailed descriptions of your changes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
