from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, Header
from jose import JWTError, jwt
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, auth
from .exceptions import DatabaseError
import logging
from docx import Document
from docx2pdf import convert
from tempfile import NamedTemporaryFile
import openai
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SECRET_KEY = os.getenv("JWT_SECRET")
if not SECRET_KEY:
    raise ValueError("No JWT_SECRET environment variable set")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

def initialize_firebase():
    """Initializes Firebase app if not already initialized."""
    try:
        return firebase_admin.get_app()
    except ValueError:
        sdk_path = os.getenv("FIREBASE_ADMIN_SDK_PATH")
        if not sdk_path:
            raise ValueError("FIREBASE_ADMIN_SDK_PATH environment variable is not set")
        try:
            cred = credentials.Certificate(sdk_path)
            return firebase_admin.initialize_app(cred)
        except Exception as e:
            logging.error(f"Failed to initialize Firebase: {e}")
            raise DatabaseError("Firebase initialization failed")

firebase_app = initialize_firebase()

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
    Retrieves the current user from the Authorization header.
    
    Args:
        authorization (str): Bearer token from the Authorization header.

    Returns:
        str: Email of the authenticated user.

    Raises:
        HTTPException: If the token is missing, invalid, or authentication fails.
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"},
            )
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Validate claims
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token missing required claim: 'sub'")
        
        return email
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTClaimsError:
        raise HTTPException(
            status_code=401,
            detail="Token claims are invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logging.error(f"Unexpected error during authentication: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def convert_docx_to_pdf(doc: Document) -> bytes:
    """
    Converts a docx Document object to PDF bytes.
    
    Args:
        doc (Document): python-docx Document object

    Returns:
        bytes: PDF file content
    """
    try:
        # Create temporary files for conversion
        with NamedTemporaryFile(suffix='.docx', delete=False) as docx_temp:
            doc.save(docx_temp.name)
            
            with NamedTemporaryFile(suffix='.pdf', delete=False) as pdf_temp:
                convert(docx_temp.name, pdf_temp.name)
                
                # Read PDF content
                with open(pdf_temp.name, 'rb') as pdf_file:
                    pdf_content = pdf_file.read()
                    
        # Clean up temporary files
        os.unlink(docx_temp.name)
        os.unlink(pdf_temp.name)
        
        return pdf_content
    except Exception as e:
        logging.error(f"PDF conversion failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to convert resume to PDF"
        )