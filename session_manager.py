from io import BytesIO
import os
import json
import uuid
import redis
import pandas as pd
from dotenv import load_dotenv
import base64
from constants import session_ttl
from datetime import datetime
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
if not REDIS_URL:
    raise ValueError("REDIS_URL environment variable is required. Please set it in your .env file.")
r = redis.from_url(REDIS_URL, decode_responses=True)


# =============================================================================
# ENCRYPTION FOR CUI COMPLIANCE - Data at Rest Protection
# =============================================================================

def _get_encryption_key() -> bytes:
    """
    Get or generate the encryption key for session data.
    In production, this should be stored securely (e.g., environment variable, secrets manager).
    """
    key = os.getenv("SESSION_ENCRYPTION_KEY")
    if key:
        return key.encode()

    # Default key for backwards compatibility - SHOULD BE OVERRIDDEN IN PRODUCTION
    # Generate a new key with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    default_key = os.getenv("SESSION_ENCRYPTION_KEY_DEFAULT", "ZmVybmV0LWtleS1mb3ItcGFjZS1iYWNrZW5kLTIwMjU=")

    # Ensure key is valid Fernet format (32 url-safe base64-encoded bytes)
    try:
        # Try to use as-is
        Fernet(default_key.encode())
        return default_key.encode()
    except:
        # Generate a proper key if default is invalid
        return Fernet.generate_key()


def _get_fernet() -> Fernet:
    """Get Fernet instance for encryption/decryption."""
    return Fernet(_get_encryption_key())


def _encrypt_data(data: str) -> str:
    """Encrypt string data for storage."""
    fernet = _get_fernet()
    encrypted = fernet.encrypt(data.encode())
    return encrypted.decode()


def _decrypt_data(encrypted_data: str) -> str:
    """Decrypt string data from storage."""
    fernet = _get_fernet()
    decrypted = fernet.decrypt(encrypted_data.encode())
    return decrypted.decode()


def _is_encrypted(data: str) -> bool:
    """Check if data appears to be Fernet encrypted."""
    try:
        # Fernet tokens start with 'gAAAAA'
        return data.startswith('gAAAAA') and len(data) > 100
    except:
        return False


# =============================================================================
# SESSION MANAGEMENT FUNCTIONS
# =============================================================================

def create_session(processed_df: pd.DataFrame, pdf_df: pd.DataFrame, session_id: Optional[str] = None) -> str:
    if session_id is None:
        session_id = str(uuid.uuid4())

    def convert_datetime_columns(df):
        """Convert all datetime columns to strings before creating records"""
        df_copy = df.copy()
        for col in df_copy.columns:
            if pd.api.types.is_datetime64_any_dtype(df_copy[col]):
                df_copy[col] = df_copy[col].dt.strftime('%Y-%m-%d').fillna('')
            else:
                # Check for datetime objects in object columns
                if df_copy[col].dtype == 'object':
                    df_copy[col] = df_copy[col].apply(
                        lambda x: x.isoformat() if isinstance(x, (datetime, pd.Timestamp)) else x
                    )
        return df_copy

    # Convert datetime columns first
    processed_clean = convert_datetime_columns(processed_df)
    pdf_clean = convert_datetime_columns(pdf_df)

    def simple_sanitize(records):
        for record in records:
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = None
        return records

    session_data = {
        "dataframe": simple_sanitize(processed_clean.to_dict(orient="records")),
        "pdf_dataframe": simple_sanitize(pdf_clean.to_dict(orient="records")),
    }

    # Encrypt session data before storing
    json_data = json.dumps(session_data)
    encrypted_data = _encrypt_data(json_data)

    r.set(session_id, encrypted_data, ex=session_ttl)
    return session_id


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    raw = r.get(session_id)
    if not raw:
        return None

    # Handle both encrypted and legacy unencrypted data
    if _is_encrypted(raw):
        try:
            decrypted = _decrypt_data(raw)
            return json.loads(decrypted)
        except Exception as e:
            # If decryption fails, try as plain JSON (legacy data)
            try:
                return json.loads(raw)
            except:
                return None
    else:
        # Legacy unencrypted data
        return json.loads(raw)


def update_session(session_id: str, **kwargs) -> Optional[Dict[str, Any]]:
    raw = r.get(session_id)
    if not raw:
        return None

    # Handle both encrypted and legacy unencrypted data
    if _is_encrypted(raw):
        try:
            decrypted = _decrypt_data(raw)
            session = json.loads(decrypted)
        except:
            session = json.loads(raw)
    else:
        session = json.loads(raw)

    def comprehensive_sanitize(obj):
        """Recursively sanitize any datetime objects in nested structures"""
        if isinstance(obj, dict):
            return {k: comprehensive_sanitize(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [comprehensive_sanitize(item) for item in obj]
        elif pd.isna(obj):
            return None
        elif isinstance(obj, (pd.Timestamp, datetime)):
            return obj.isoformat()
        elif hasattr(obj, 'isoformat'):  # Catch any other datetime-like objects
            try:
                return obj.isoformat()
            except:
                return str(obj)
        else:
            return obj

    for key, value in kwargs.items():
        if isinstance(value, pd.DataFrame):
            # Convert DataFrame to records and sanitize
            records = value.to_dict(orient="records")
            session[key] = comprehensive_sanitize(records)
        else:
            session[key] = comprehensive_sanitize(value)

    # Encrypt updated session data
    json_data = json.dumps(session)
    encrypted_data = _encrypt_data(json_data)

    r.set(session_id, encrypted_data, ex=session_ttl)
    return session


def delete_session(session_id: str) -> None:
    r.delete(session_id)


def store_pdf_in_redis(session_id: str, pdf_buffer: BytesIO) -> None:
    """Store PDF in Redis with encryption."""
    pdf_bytes = pdf_buffer.getvalue()
    # Encrypt the PDF bytes
    encrypted = _encrypt_data(base64.b64encode(pdf_bytes).decode())
    r.set(f"{session_id}_pdf", encrypted, ex=session_ttl)


def get_pdf_from_redis(session_id: str) -> Optional[BytesIO]:
    """Retrieve and decrypt PDF from Redis."""
    encrypted = r.get(f"{session_id}_pdf")
    if not encrypted:
        return None

    # Handle both encrypted and legacy unencrypted data
    if _is_encrypted(encrypted):
        try:
            decrypted = _decrypt_data(encrypted)
            pdf_bytes = base64.b64decode(decrypted)
        except:
            # Legacy unencrypted data
            pdf_bytes = base64.b64decode(encrypted)
    else:
        pdf_bytes = base64.b64decode(encrypted)

    return BytesIO(pdf_bytes)
