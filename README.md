# NSZ to NSP Converter Web GUI

A web-based graphical user interface for converting Nintendo Switch NSZ files to NSP format using the nsz library. The application features a clean Material Design interface for easy file uploads and conversions.

## Features

- Upload production keys (prod.keys) for Nintendo Switch decryption
- Upload NSZ files for conversion to NSP format
- Server-side conversion using the nsz library
- Download converted NSP files directly from the web interface
- Clean, responsive Material Design interface
- File management and status tracking

## Requirements

- Python 3.8 or higher
- Nintendo Switch prod.keys file (you must provide your own)
- NSZ files to convert to NSP format

## Installation

1. Clone or download this repository to your local machine.

2. Create a virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Make sure you have the `nsz` tool installed in your environment. If the pip installation doesn't work properly:
   ```bash
   pip install nsz
   ```

## Running the Application

1. Navigate to the project directory in your terminal.

2. Start the application using one of these methods:

   **Option 1: Using the run script (recommended)**:
   ```bash
   ./run.sh
   ```

   **Option 2: Direct Python command**:
   ```bash
   python main.py
   ```

   **Option 3: Using Uvicorn directly**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. Open your web browser and navigate to `http://localhost:8000`

## Using the Application

### 1. Upload Production Keys

- Click the "Choose Keys File" button in the "Upload Production Keys" section
- Select your `prod.keys` file (this is required for decryption)
- Click "Upload Keys" to upload the file to the server
- You'll see a success message when the keys are uploaded

### 2. Upload and Convert NSZ Files

- Click the "Choose NSZ File" button in the "Upload NSZ File" section
- Select the NSZ file you wish to convert to NSP format
- Click "Convert to NSP" to start the conversion process
- The application will process the file and show a success message when complete

### 3. Download Converted Files

- After successful conversion, visit the "Converted Files" section
- You'll see your converted NSP files listed with download buttons
- Click the download button next to the file you want to download

## Security Notes

- The application stores uploaded prod.keys files locally on the server
- Only run this application on secure, private networks
- Remember to regularly delete temporary files (keys, uploads, output) for privacy
- Keep your prod.keys file secure and do not share it

## Project Structure

```
nsz_to_nsp_webgui/
├── main.py                 # Main FastAPI application
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html         # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css      # Custom CSS styles
│   └── js/
│       └── script.js      # Client-side JavaScript
├── keys/                   # Directory for uploaded keys (created automatically)
├── uploads/               # Directory for uploaded NSZ files (created automatically)
└── output/                # Directory for converted NSP files (created automatically)
└── README.md              # This file
```

## Troubleshooting

- If the conversion fails, make sure:
  - Your prod.keys file is valid
  - The NSZ file is not corrupted
  - The nsz library is correctly installed
  - You have enough disk space for the operation

- If you get permission errors:
  - Make sure the application has write permissions to the project directory
  - Check that the server has necessary file system permissions

- If the web interface doesn't load correctly:
  - Clear your browser cache
  - Try a different web browser
  - Check the developer console for errors

## License

This project is intended for personal use only. The use of Nintendo Switch files is governed by your agreement with Nintendo. Please ensure you have the legal right to decrypt and convert these files.