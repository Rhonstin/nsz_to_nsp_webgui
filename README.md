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

### Option 1: Using the run script (recommended for local development)
   ```bash
   ./run.sh
   ```

### Option 2: Direct Python command
   ```bash
   python main.py
   ```

### Option 3: Using Uvicorn directly
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Option 4: Using Docker (recommended for production)
Make sure you have Docker and Docker Compose installed on your system.

#### Basic Docker Compose commands:

1. **Build and start the application:**
   ```bash
   docker-compose up -d
   ```
   This will start the application in detached mode, accessible at `http://localhost:8002`

2. **View application logs:**
   ```bash
   docker-compose logs -f
   ```

3. **Stop the application:**
   ```bash
   docker-compose down
   ```

4. **Rebuild the application after code changes:**
   ```bash
   docker-compose up -d --build
   ```

5. **Remove containers and volumes:**
   ```bash
   docker-compose down -v
   ```

#### Advanced Docker Compose configurations:

The project includes specialized configuration files for different deployment scenarios:

**Development mode** (includes debugging capabilities):
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

**Production mode** (includes resource limits and security configurations):
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

**Note:** The application will be accessible at `http://localhost:8002` when running with Docker Compose.

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
- When running with Docker, ensure your Docker daemon is secured and only trusted users have access
- Regularly update the Docker base image to include the latest security patches
- Consider using Docker secrets or environment variables for sensitive information in production environments
- Monitor Docker container logs for any suspicious activity

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

### General Issues

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

### Docker Specific Issues

- **Container won't start or crashes immediately:**
  - Check the logs with `docker-compose logs -f` to see error messages
  - Ensure all dependencies in `requirements.txt` are compatible with the Docker image

- **Port binding errors:**
  - Make sure port 8002 is not already in use by another service
  - Stop conflicting services or change the external port in `docker-compose.yml`

- **Permission errors with mounted volumes:**
  - Ensure Docker has access to the local directories (uploads, output, keys)
  - On Linux, you may need to adjust directory ownership to match the container user
  - If the directories don't exist, create them manually first: `mkdir -p uploads output keys`

- **Docker build fails:**
  - Check that your `Dockerfile` and `requirements.txt` don't have syntax errors
  - Ensure all required files exist in the build context
  - Try running `docker build .` directly to see detailed error messages

- **Health check fails:**
  - The application might need more time to start; adjust the `start_period` in docker-compose.yml
  - Make sure the application is actually binding to the correct port (8000 inside container)

## License

This project is intended for personal use only. The use of Nintendo Switch files is governed by your agreement with Nintendo. Please ensure you have the legal right to decrypt and convert these files.