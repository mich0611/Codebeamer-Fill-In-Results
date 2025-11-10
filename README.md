### Usage:
This is a Python application designed to automatically update the status of test cases in CodeBeamer. It provides an intuitive Graphical User Interface (GUI) that allows users to easily batch-update test case results for a specific Test Set, including their status and any associated comments.

### Key Features:

- GUI Interface: Built with Tkinter to provide a user-friendly interface.

- Batch Updates: Supports importing update data for multiple test cases from a JSON file.

- Manual Entry: Allows you to manually enter the ID, status, and comments for individual test cases.

- Status Options: You can set test case statuses to `PASSED`, `FAILED`, `NOT_APPLICABLE`, or `BLOCKED`.

- Preview: All pending updates are displayed in a table before you run the script, making it easy to review your changes.

- Error Handling: The application automatically detects and reports any test case IDs that do not exist within the target Test Set.


### Run the Application

- python main.py
- All packages are built-in, no need to pip install any packages.


### Step-by-Step Guide
1. Enter the Test Set ID: In the "Test Set ID" field, enter the ID of the Test Set you want to update.
2. Add Test Case Data:
    - Method1: Click the Import JSON button to batch-import data from a JSON file.
    - Method2: Manually enter the "Test Case ID", "Status", and "Comment" for a single test case, then click the Add button.
3. Execute the Update: Once you have confirmed the data in the table, click the Run button in the bottom-right corner.
4. Review Results: A message box will pop up to let you know if the update was successful. Any IDs that could not be updated will be printed to the console.
<img width="1832" height="488" alt="image" src="https://github.com/user-attachments/assets/a12348e2-ac05-43f6-b3dd-14825fc20350" />
<img width="1266" height="283" alt="image" src="https://github.com/user-attachments/assets/3e38a47c-229f-4101-badd-faadda54170d" />
<img width="796" height="622" alt="image" src="https://github.com/user-attachments/assets/0416af85-372f-4680-8c40-838794de25a4" />
<img width="959" height="608" alt="image" src="https://github.com/user-attachments/assets/ddfabd13-0089-45a8-a89c-7528d5e247a4" />

### Before You Start
Before using this application, please configure the following required settings:

- USERNAME and PASSWORD: Open main.py and enter your CodeBeamer account username and password.
- CODEBEAMER_URL: Open codebeamer_client.py and set the URL of your organization's CodeBeamer API server.
Example: https://alm.<company_name>.com/cb/api/v3/

