from datetime import datetime, timedelta
from typing import Optional, Tuple
from fastapi import Depends, HTTPException, Header
from jose import JWTError, jwt
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, auth
from .exceptions import DatabaseError
from docx import Document
from docx2pdf import convert
import tempfile
from tempfile import NamedTemporaryFile
import openai
from openai import OpenAI
import logging
import sys
import subprocess
from pathlib import Path

logging.basicConfig(level=logging.INFO)

def initialize_firebase_admin():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        cred_path = os.path.join(current_dir, "..", "career-craft-98538-firebase-adminsdk-g7rtc-992c68a834.json")
        cred = credentials.Certificate(os.path.abspath(cred_path))
        firebase_admin.initialize_app(cred)
    except ValueError:
        # App has already been initialized
        pass

# Initialize Firebase Admin when the module loads
initialize_firebase_admin()

try:
    apps = firebase_admin._apps
    logging.info(f"Firebase Admin SDK initialized successfully. Active apps: {len(apps)}")
except Exception as e:
    logging.error(f"Error checking Firebase initialization: {str(e)}")

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
if not client.api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

SECRET_KEY = os.getenv("JWT_SECRET")
if not SECRET_KEY:
    raise ValueError("No JWT_SECRET environment variable set")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Token Creation
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Generates a JWT access token with expiration."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Current User Retrieval
async def get_current_user(authorization: str = Header(None)):
    """
    Validates Firebase token and returns user info.
    """
    logging.info(f"Received authorization header: {authorization}")
    
    if not authorization:
        logging.error("No authorization header provided")
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        scheme, token = authorization.split()
        logging.info(f"Auth scheme: {scheme}")
        
        if scheme.lower() != "bearer":
            logging.error(f"Invalid scheme: {scheme}")
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Verify the Firebase token
        logging.info("Attempting to verify token...")
        decoded_token = auth.verify_id_token(token)
        logging.info(f"Token verified successfully. User email: {decoded_token['email']}")
        return decoded_token['email']
        
    except ValueError as e:
        logging.error(f"ValueError in token verification: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except auth.InvalidIdTokenError as e:
        logging.error(f"Invalid token error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logging.error(f"Unexpected error in token verification: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

def convert_docx_to_pdf(doc: Document) -> Tuple[bytes, str]:
    """
    Convert a python-docx Document object to PDF bytes using LibreOffice/soffice as fallback
    Returns: Tuple of (pdf_bytes, conversion_method)
    """
    # Create a temporary directory with a guaranteed cleanup
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        docx_path = temp_dir_path / 'resume.docx'
        pdf_path = temp_dir_path / 'resume.pdf'
        
        # Save the DOCX
        logging.info(f"Saving DOCX to {docx_path}")
        doc.save(str(docx_path))
        
        # Try primary conversion method (docx2pdf)
        try:
            from docx2pdf import convert
            logging.info("Attempting conversion with docx2pdf")
            convert(str(docx_path), str(pdf_path))
            if pdf_path.exists():
                with open(pdf_path, 'rb') as pdf_file:
                    return pdf_file.read(), 'docx2pdf'
        except Exception as e:
            logging.warning(f"docx2pdf conversion failed: {e}. Trying alternative method...")

        # Fallback to LibreOffice (if available)
        try:
            # Detect operating system and set appropriate LibreOffice binary
            if sys.platform == "darwin":  # macOS
                soffice_paths = [
                    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
                    "/Applications/OpenOffice.app/Contents/MacOS/soffice"
                ]
            elif sys.platform == "win32":  # Windows
                soffice_paths = [
                    r"C:\Program Files\LibreOffice\program\soffice.exe",
                    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"
                ]
            else:  # Linux
                soffice_paths = [
                    "/usr/bin/soffice",
                    "/usr/bin/libreoffice"
                ]

            soffice_path = next((path for path in soffice_paths if Path(path).exists()), None)
            
            if not soffice_path:
                raise FileNotFoundError("LibreOffice/OpenOffice not found")

            logging.info("Attempting conversion with LibreOffice")
            subprocess.run([
                soffice_path,
                '--headless',
                '--convert-to',
                'pdf',
                str(docx_path),
                '--outdir',
                str(temp_dir_path)
            ], check=True, capture_output=True)

            if pdf_path.exists():
                with open(pdf_path, 'rb') as pdf_file:
                    return pdf_file.read(), 'libreoffice'
                    
            raise FileNotFoundError("PDF was not created by LibreOffice")

        except Exception as e:
            logging.error(f"All conversion methods failed. LibreOffice error: {e}")
            raise RuntimeError("PDF conversion failed with all available methods") from e