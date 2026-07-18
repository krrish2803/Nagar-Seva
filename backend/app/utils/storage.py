"""File storage utilities for handling uploads."""

import os
import uuid
from pathlib import Path
from typing import Optional
import aiofiles
from app.config import settings


async def save_upload_file(
    file_content: bytes, file_name: str, file_type: str = "image"
) -> str:
    """
    Save uploaded file to disk.

    Args:
        file_content: File bytes content
        file_name: Original file name
        file_type: Type of file (image, video, audio)

    Returns:
        Storage path/URL for the file
    """
    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.upload_dir) / file_type
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    file_ext = Path(file_name).suffix
    unique_name = f"{uuid.uuid4()}{file_ext}"
    file_path = upload_dir / unique_name

    # Save file
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(file_content)

    # Return relative path
    return str(file_path)


def delete_upload_file(file_path: str) -> bool:
    """
    Delete a file from storage.

    Args:
        file_path: Path to file

    Returns:
        True if deleted, False if file not found
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")
        return False


def get_file_url(file_path: str) -> str:
    """
    Convert file path to URL.

    Args:
        file_path: File path

    Returns:
        URL path for serving the file
    """
    # In production, this would be a CDN URL or proper file serving URL
    return f"/files/{file_path.replace(os.sep, '/')}"


async def get_file_content(file_path: str) -> Optional[bytes]:
    """
    Read file content from storage.

    Args:
        file_path: Path to file

    Returns:
        File bytes or None if not found
    """
    try:
        async with aiofiles.open(file_path, "rb") as f:
            return await f.read()
    except FileNotFoundError:
        return None


def validate_file_size(file_size_bytes: int) -> bool:
    """
    Validate file size against max allowed size.

    Args:
        file_size_bytes: File size in bytes

    Returns:
        True if file size is valid
    """
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    return file_size_bytes <= max_bytes
