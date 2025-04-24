# S3 Command-Line Tool

A simple Python script to interact with S3-compatible storage using the command line. Built with Python, `boto3`.

## Features

*   **Upload:** Upload local files to an S3 bucket. Automatically creates a dated/hostname-based prefix if no specific object name is given.
*   **Download:** Download files from an S3 bucket to a local path. Can download to the current directory, a specified directory, or a specific file path.
*   **List:** List objects within an S3 bucket root or a specific directory prefix.
*   **Delete:** Delete specified objects from an S3 bucket.

## Prerequisites

*   Python 3.12 or higher

## Installation & Setup

1.  **Clone the repository (optional):**
    ```bash
    git clone <your-repo-url>
    cd s3-tool-directory
    ```
2.  **Install dependencies:**
    Navigate to the project directory in your terminal and run:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure S3 Credentials:**
    The script requires S3 credentials and endpoint information. You can provide these in two ways:
    *   **`.env` file (Recommended):** Create a file named `.env` in the project's root directory with the following content:
        ```dotenv
        # .env
        ACCESS_KEY=YOUR_ACCESS_KEY_ID
        SECRET_KEY=YOUR_SECRET_ACCESS_KEY
        BUCKET_NAME=your-target-bucket-name
        URL=https://your-s3-compatible-endpoint.com
        ```
        *(Ensure `.env` is listed in your `.gitignore` file to avoid committing credentials)*
    *   **Command-Line Arguments:** You can override or provide credentials directly via command-line options (`--url`, `--access_key`, `--secret_key`, `--bucket_name`) when running the script. If you provide all necessary credentials via the command line and no `.env` file exists, the script will prompt to save them to a new `.env` file for future use.

## Usage

The script uses a command-line interface with subcommands for different actions.

**General Format:**

```bash
python main.py [common_options] <action> [action_options]
```
Or, if using the compiled executable:
```bash
./s3tool-linux [common_options] <action> [action_options]
# or on Windows
.\s3tool-win.exe [common_options] <action> [action_options]
```

**Common Options (Override `.env`):**

*   `--url <S3_URL>`: Specify the S3 endpoint URL.
*   `--access_key <ACCESS_KEY>`: Specify the S3 Access Key ID.
*   `--secret_key <SECRET_KEY>`: Specify the S3 Secret Access Key.
*   `--bucket_name <BUCKET_NAME>`: Specify the target S3 bucket name.

**Actions:**

*   **Upload:**
    ```bash
    # Upload a file, letting the script determine the S3 object name (date/hostname/filename)
    python main.py upload --file_path /path/to/local/document.txt

    # Upload a file with a specific S3 object name/path
    python main.py upload --file_path ./example.zip --object_name example.zip
    ```

*   **List:**
    ```bash
    # List all objects in the bucket root
    python main.py ls

    # List objects under a specific prefix/directory (ensure trailing slash if needed)
    python main.py ls --directory images/2024/
    ```

*   **Download:**
    ```bash
    # Download a file to the current working directory
    python main.py download --file_name path/in/s3/data.csv

    # Download a file to a specific local directory (file keeps its original name)
    python main.py download --file_name path/in/s3/data.csv --local_path /path/to/save/downloads/
    ```

*   **Delete:**
    ```bash
    # Delete a specific file from S3
    python main.py delete --file_name path/in/s3/obsolete_file.log
    ```

## Building Executables

This project includes a GitHub Actions workflow (`.github/workflows/build.yml`) that automatically builds standalone executables for Windows (`s3tool-win.exe`) and Linux (`s3tool-linux`) using PyInstaller and UPX (for compression).

Builds are triggered on pushes to the `main` branch. You can download the compiled executables as artifacts from the workflow runs in the "Actions" tab of the GitHub repository.

**Manual Build:**

1.  Ensure you have Python and pip installed.
2.  Install dependencies: `pip install -r requirements.txt`
3.  Install PyInstaller: `pip install pyinstaller`
4.  (Optional) Install UPX: Download from [https://upx.github.io/](https://upx.github.io/) and ensure `upx.exe` (or `upx`) is in your system's PATH or specify its location using `--upx-dir`.
5.  Run PyInstaller from the project root:
    ```bash
    pyinstaller --name s3tool-win --onefile --clean main.py
    ```
    The executable will be located in the `dist` folder.