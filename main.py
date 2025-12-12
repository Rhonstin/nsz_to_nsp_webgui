from fastapi import FastAPI, Request, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import aiofiles
import subprocess
import logging
from datetime import datetime
from typing import List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Directory paths for temporary files
KEYS_DIR = "keys"
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "output"
KEYS_FILE_PATH = os.path.join(KEYS_DIR, "prod.keys")  # Fixed path for the keys file

# Create necessary directories
os.makedirs(KEYS_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main page showing upload options."""
    logger.info(f"Home page accessed from {request.client.host}")
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload-keys/")
async def upload_keys(file: UploadFile = File(...)):
    """Upload prod.keys file."""
    try:
        logger.info(f"Uploading keys file: {file.filename}")

        # Check if keys file already exists
        if os.path.exists(KEYS_FILE_PATH):
            logger.warning("Keys file already exists, overwriting")
            return {"message": f"Keys file '{file.filename}' overwritten successfully!"}

        # Save uploaded keys file to fixed location
        async with aiofiles.open(KEYS_FILE_PATH, "wb") as buffer:
            content = await file.read()
            await buffer.write(content)

        logger.info(f"Keys file '{file.filename}' uploaded successfully to {KEYS_FILE_PATH}")
        return {"message": f"Keys file '{file.filename}' uploaded successfully!"}
    except Exception as e:
        logger.error(f"Error uploading keys file {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading keys: {str(e)}")

# Removed directory creation and upload endpoints

@app.post("/convert-nsz/")
async def convert_nsz(file: UploadFile = File(...)):
    """Upload NSZ file and convert to NSP."""
    try:
        logger.info(f"Starting conversion for NSZ file: {file.filename}")

        # Save uploaded NSZ file
        nsz_filename = file.filename
        nsz_path = f"{UPLOAD_DIR}/{nsz_filename}"

        # Check if NSZ file already exists
        if os.path.exists(nsz_path):
            logger.warning(f"NSZ file {nsz_filename} already exists, skipping upload")
            return {"message": f"NSZ file '{nsz_filename}' already exists. Skipping upload."}

        async with aiofiles.open(nsz_path, "wb") as buffer:
            content = await file.read()
            await buffer.write(content)

        logger.info(f"NSZ file saved to: {nsz_path}")

        # Prepare output path - nsz tool will create the correct filename
        output_filename = nsz_filename.replace('.nsz', '.nsp')

        # Check if keys file exists
        if not os.path.exists(KEYS_FILE_PATH):
            logger.warning("No prod.keys file found, conversion cannot proceed")
            raise HTTPException(status_code=400, detail="No prod.keys file found. Please upload keys first.")

        keys_path = KEYS_FILE_PATH

        logger.info(f"Using keys file: {keys_path}")

        # Set the environment variable for keys file
        env = os.environ.copy()
        env['KEYS_FILE_PATH'] = keys_path

        # Run nsz conversion command using subprocess (decompress mode)
        cmd = [
            "nsz",
            "-D",  # decompress option
            nsz_path,  # input file
            "-o", OUTPUT_DIR  # output directory
        ]

        logger.info(f"Executing conversion command: {' '.join(cmd)} with environment variable KEYS_FILE_PATH set")
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)

        logger.info(f"Conversion process completed with return code: {result.returncode}")
        if result.stdout:
            logger.info(f"Conversion stdout: {result.stdout}")
        if result.stderr:
            logger.warning(f"Conversion stderr: {result.stderr}")

        if result.returncode != 0:
            logger.error(f"Conversion failed with return code {result.returncode}: {result.stderr}")
            raise HTTPException(status_code=500, detail=f"Conversion failed: {result.stderr}")

        logger.info(f"Conversion completed successfully! Output file: {output_filename}")
        return {"message": f"Conversion completed successfully!", "filename": output_filename}
    except Exception as e:
        logger.error(f"Error during conversion of {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error during conversion: {str(e)}")

@app.post("/convert-nsz-multi/")
async def convert_nsz_multi(files: List[UploadFile] = File(...)):
    """Upload and convert multiple NSZ files to NSP."""
    try:
        logger.info(f"Starting conversion for {len(files)} NSZ files")

        results = []
        successful_conversions = 0
        failed_conversions = 0

        # Check if keys file exists first
        if not os.path.exists(KEYS_FILE_PATH):
            logger.warning("No prod.keys file found, conversion cannot proceed")
            raise HTTPException(status_code=400, detail="No prod.keys file found. Please upload keys first.")

        keys_path = KEYS_FILE_PATH
        logger.info(f"Using keys file: {keys_path}")

        # Set the environment variable for keys file
        env = os.environ.copy()
        env['KEYS_FILE_PATH'] = keys_path

        for file in files:
            try:
                # Save uploaded NSZ file
                nsz_filename = file.filename
                nsz_path = f"{UPLOAD_DIR}/{nsz_filename}"

                # Check if NSZ file already exists
                if os.path.exists(nsz_path):
                    logger.warning(f"NSZ file {nsz_filename} already exists, skipping upload")
                    results.append({"filename": nsz_filename, "status": "skipped", "message": "File already exists"})
                    continue

                async with aiofiles.open(nsz_path, "wb") as buffer:
                    content = await file.read()
                    await buffer.write(content)

                logger.info(f"NSZ file saved to: {nsz_path}")

                # Prepare output path - nsz tool will create the correct filename
                output_filename = nsz_filename.replace('.nsz', '.nsp')

                # Run nsz conversion command using subprocess (decompress mode)
                cmd = [
                    "nsz",
                    "-D",  # decompress option
                    nsz_path,  # input file
                    "-o", OUTPUT_DIR  # output directory
                ]

                logger.info(f"Executing conversion command: {' '.join(cmd)} with environment variable KEYS_FILE_PATH set for {nsz_filename}")
                result = subprocess.run(cmd, capture_output=True, text=True, env=env)

                logger.info(f"Conversion process completed with return code: {result.returncode}")
                if result.stdout:
                    logger.info(f"Conversion stdout: {result.stdout}")
                if result.stderr:
                    logger.warning(f"Conversion stderr: {result.stderr}")

                if result.returncode != 0:
                    logger.error(f"Conversion failed with return code {result.returncode}: {result.stderr}")
                    results.append({"filename": nsz_filename, "status": "failed", "error": result.stderr})
                    failed_conversions += 1
                else:
                    logger.info(f"Conversion completed successfully! Output file: {output_filename}")
                    results.append({"filename": nsz_filename, "status": "success", "output": output_filename})
                    successful_conversions += 1

            except Exception as file_error:
                logger.error(f"Error during conversion of {file.filename}: {str(file_error)}")
                results.append({"filename": file.filename, "status": "failed", "error": str(file_error)})
                failed_conversions += 1

        return {
            "message": f"Batch conversion completed. {successful_conversions} successful, {failed_conversions} failed.",
            "results": results,
            "successful_conversions": successful_conversions,
            "failed_conversions": failed_conversions
        }
    except Exception as e:
        logger.error(f"Error during batch conversion: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error during batch conversion: {str(e)}")

@app.post("/convert-directory/")
async def convert_directory():
    """Convert all NSZ files in the upload directory."""
    try:
        logger.info("Starting batch conversion for all files in upload directory")

        # Get all NSZ files in the upload directory
        nsz_files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith('.nsz')]

        if not nsz_files:
            logger.info("No NSZ files found in upload directory")
            return {"message": "No NSZ files found in upload directory."}

        logger.info(f"Found {len(nsz_files)} NSZ files to convert")

        # Check if keys file exists first
        if not os.path.exists(KEYS_FILE_PATH):
            logger.warning("No prod.keys file found, conversion cannot proceed")
            raise HTTPException(status_code=400, detail="No prod.keys file found. Please upload keys first.")

        keys_path = KEYS_FILE_PATH
        logger.info(f"Using keys file: {keys_path}")

        # Set the environment variable for keys file
        env = os.environ.copy()
        env['KEYS_FILE_PATH'] = keys_path

        results = []
        successful_conversions = 0
        failed_conversions = 0

        for nsz_filename in nsz_files:
            try:
                nsz_path = os.path.join(UPLOAD_DIR, nsz_filename)

                # Prepare output path
                output_filename = nsz_filename.replace('.nsz', '.nsp')

                # Run nsz conversion command using subprocess (decompress mode)
                cmd = [
                    "nsz",
                    "-D",  # decompress option
                    nsz_path,  # input file
                    "-o", OUTPUT_DIR  # output directory
                ]

                logger.info(f"Executing conversion command: {' '.join(cmd)} with environment variable KEYS_FILE_PATH set for {nsz_filename}")
                result = subprocess.run(cmd, capture_output=True, text=True, env=env)

                logger.info(f"Conversion process completed with return code: {result.returncode}")
                if result.stdout:
                    logger.info(f"Conversion stdout: {result.stdout}")
                if result.stderr:
                    logger.warning(f"Conversion stderr: {result.stderr}")

                if result.returncode != 0:
                    logger.error(f"Conversion failed with return code {result.returncode}: {result.stderr}")
                    results.append({"filename": nsz_filename, "status": "failed", "error": result.stderr})
                    failed_conversions += 1
                else:
                    logger.info(f"Conversion completed successfully! Output file: {output_filename}")
                    results.append({"filename": nsz_filename, "status": "success", "output": output_filename})
                    successful_conversions += 1

            except Exception as file_error:
                logger.error(f"Error during conversion of {nsz_filename}: {str(file_error)}")
                results.append({"filename": nsz_filename, "status": "failed", "error": str(file_error)})
                failed_conversions += 1

        return {
            "message": f"Directory conversion completed. {successful_conversions} successful, {failed_conversions} failed.",
            "results": results,
            "successful_conversions": successful_conversions,
            "failed_conversions": failed_conversions
        }
    except Exception as e:
        logger.error(f"Error during directory conversion: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error during directory conversion: {str(e)}")

# Removed specific directory conversion endpoint

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download converted NSP file."""
    file_path = os.path.join(OUTPUT_DIR, filename)

    logger.info(f"Download request for file: {filename}")

    if not os.path.exists(file_path):
        logger.warning(f"Download requested for non-existent file: {filename}")
        raise HTTPException(status_code=404, detail="File not found")

    logger.info(f"Serving download for file: {filename} from {file_path}")

    def iterfile():
        with open(file_path, mode="rb") as file_like:
            yield from file_like

    return StreamingResponse(
        iterfile(),
        media_type='application/octet-stream',
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

@app.get("/keys-status")
async def keys_status():
    """Check if prod.keys file is uploaded."""
    keys_exists = os.path.exists(KEYS_FILE_PATH)
    logger.info(f"Keys file status: {'exists' if keys_exists else 'does not exist'}")

    return {"keys_uploaded": keys_exists}

@app.post("/clean-output/")
async def clean_output():
    """Clean the output directory by removing all NSP files."""
    try:
        logger.info("Cleaning output directory")

        nsp_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.nsp')]
        deleted_count = 0

        for nsp_file in nsp_files:
            file_path = os.path.join(OUTPUT_DIR, nsp_file)
            os.remove(file_path)
            deleted_count += 1

        logger.info(f"Cleaned {deleted_count} NSP files from output directory")
        return {"message": f"Successfully cleaned {deleted_count} NSP files from output directory"}
    except Exception as e:
        logger.error(f"Error cleaning output directory: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error cleaning output directory: {str(e)}")

@app.post("/clean-uploads/")
async def clean_uploads():
    """Clean the uploads directory by removing all NSZ files."""
    try:
        logger.info("Cleaning uploads directory")

        nsz_files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith('.nsz')]
        deleted_count = 0

        for nsz_file in nsz_files:
            file_path = os.path.join(UPLOAD_DIR, nsz_file)
            os.remove(file_path)
            deleted_count += 1

        logger.info(f"Cleaned {deleted_count} NSZ files from uploads directory")
        return {"message": f"Successfully cleaned {deleted_count} NSZ files from uploads directory"}
    except Exception as e:
        logger.error(f"Error cleaning uploads directory: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error cleaning uploads directory: {str(e)}")

@app.post("/clean-all/")
async def clean_all():
    """Clean all internal folders (uploads and output) except keys."""
    try:
        logger.info("Cleaning all internal directories (uploads and output)")

        # Clean uploads directory
        nsz_files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith('.nsz')]
        uploads_deleted = 0
        for nsz_file in nsz_files:
            file_path = os.path.join(UPLOAD_DIR, nsz_file)
            os.remove(file_path)
            uploads_deleted += 1

        # Clean output directory
        nsp_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.nsp')]
        output_deleted = 0
        for nsp_file in nsp_files:
            file_path = os.path.join(OUTPUT_DIR, nsp_file)
            os.remove(file_path)
            output_deleted += 1

        total_deleted = uploads_deleted + output_deleted
        logger.info(f"Cleaned {total_deleted} files total ({uploads_deleted} from uploads, {output_deleted} from output)")
        return {
            "message": f"Successfully cleaned all internal folders. Deleted {uploads_deleted} NSZ files and {output_deleted} NSP files.",
            "uploads_deleted": uploads_deleted,
            "output_deleted": output_deleted,
            "total_deleted": total_deleted
        }
    except Exception as e:
        logger.error(f"Error cleaning all directories: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error cleaning all directories: {str(e)}")

@app.get("/files")
async def get_files():
    """Get list of files from upload directory."""
    logger.info("Request for files list")

    try:
        # List all items in the upload directory
        all_items = os.listdir(UPLOAD_DIR)

        # Also include files from root directory
        nsz_files = [f for f in all_items if f.endswith('.nsz')]
        nsp_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.nsp')]

        logger.info(f"Found {len(nsz_files)} NSZ files")

        return {
            "nsz_files": nsz_files,
            "nsp_files": nsp_files
        }
    except Exception as e:
        logger.error(f"Error getting files list: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting files list: {str(e)}")

@app.get("/uploaded-files")
async def get_uploaded_files():
    """Get list of uploaded files."""
    logger.info("Request for uploaded files list")

    nsz_files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith('.nsz')]
    nsp_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.nsp')]

    logger.info(f"Found {len(nsz_files)} NSZ files and {len(nsp_files)} NSP files")

    return {
        "nsz_files": nsz_files,
        "nsp_files": nsp_files
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)