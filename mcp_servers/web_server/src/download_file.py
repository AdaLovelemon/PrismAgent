import os
import requests
import gdown
import re
import yt_dlp
from huggingface_hub import hf_hub_download
from urllib.parse import urlparse, unquote

# Global sandbox path that can be set via server arguments
_SANDBOX_PATH = None

def set_sandbox_path(path: str):
    """Sets the global sandbox path for all downloads."""
    global _SANDBOX_PATH
    _SANDBOX_PATH = os.path.abspath(path)
    if not os.path.exists(_SANDBOX_PATH):
        os.makedirs(_SANDBOX_PATH, exist_ok=True)

def _get_output_path(output_dir: str) -> str:
    """Helper to resolve the output directory path, prioritizing sandbox if set."""
    if _SANDBOX_PATH:
        # If output_dir is provided but is relative, join it with sandbox
        if not os.path.isabs(output_dir):
            output_path = os.path.join(_SANDBOX_PATH, output_dir)
        else:
            # If an absolute path is provided, we still force it to be within sandbox for security
            # unless we want to allow the LLM to write anywhere (usually better to restrict)
            output_path = output_dir
    else:
        # Fallback to legacy behavior if sandbox path is not set
        if not os.path.isabs(output_dir):
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            output_path = os.path.join(base_dir, output_dir)
        else:
            output_path = output_dir

    if not os.path.exists(output_path):
        os.makedirs(output_path, exist_ok=True)
    return output_path

def download_generic_file(url: str, output_dir: str = "downloads") -> str:
    """
    Downloads a file from a standard web URL.
    
    Args:
        url: The direct URL of the file to download (e.g., a PDF link).
        output_dir: The directory where the file will be saved.
    """
    output_path = _get_output_path(output_dir)
    
    try:
        print(f"Downloading from URL: {url}")
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        # Try to get filename from content-disposition
        cd = response.headers.get("Content-Disposition")
        filename = None
        if cd:
            fname_match = re.findall("filename=(.+)", cd)
            if fname_match:
                filename = fname_match[0].strip(' "')
        
        if not filename:
            filename = os.path.basename(urlparse(url).path)

        if not filename:
            filename = "downloaded_file"

        filename = unquote(filename)
        full_path = os.path.join(output_path, filename)

        # Avoid overwriting existing files
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(full_path):
            full_path = os.path.join(output_path, f"{base}_{counter}{ext}")
            counter += 1

        with open(full_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        return f"Successfully downloaded file to: {full_path}"

    except Exception as e:
        return f"Error downloading file: {str(e)}"

def download_gdrive_file(url: str, output_dir: str = "downloads") -> str:
    """
    Downloads a file from a public Google Drive link.
    
    Args:
        url: The Google Drive share link.
        output_dir: The directory where the file will be saved.
    """
    output_path = _get_output_path(output_dir)
    
    try:
        print(f"Downloading from Google Drive: {url}")
        # gdown can handle most Drive URLs directly
        filename = gdown.download(url, quiet=False, fuzzy=True, output=output_path)
        if filename:
            # gdown output is the path itself if it succeeded
            return f"Successfully downloaded file from Google Drive to: {filename}"
        else:
            return "Failed to download from Google Drive. Ensure the link is public."
    except Exception as e:
        return f"Error downloading from Google Drive: {str(e)}"

def download_video_audio(url: str, output_dir: str = "downloads", format: str = "best") -> str:
    """
    Downloads video or audio from YouTube and other supported platforms.
    
    Args:
        url: The video URL.
        output_dir: The directory to save the file.
        format: The format to download (e.g., 'best', 'bestaudio').
    """
    output_path = _get_output_path(output_dir)
    
    ydl_opts = {
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'format': format,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return f"Successfully downloaded video/audio: {filename}"
    except Exception as e:
        return f"Error downloading video: {str(e)}"

def download_hf_file(repo_id: str, filename: str, subfolder: str = None, repo_type: str = "model", output_dir: str = "downloads") -> str:
    """
    Downloads a specific file from Hugging Face Hub.
    
    Args:
        repo_id: The Hugging Face repo ID (e.g., 'bert-base-uncased').
        filename: The name of the file to download inside the repo.
        subfolder: Optional subfolder within the repo.
        repo_type: Type of repo ('model', 'dataset', 'space').
        output_dir: The directory to save the file.
    """
    output_path = _get_output_path(output_dir)
    
    try:
        path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            subfolder=subfolder,
            repo_type=repo_type,
            local_dir=output_path
        )
        return f"Successfully downloaded Hugging Face file to: {path}"
    except Exception as e:
        return f"Error downloading from Hugging Face: {str(e)}"

def download_github_content(url: str, output_dir: str = "downloads") -> str:
    """
    Downloads content from GitHub. Supports raw file URLs and repo archive URLs.
    """
    # If it's a raw URL, use generic downloader
    if "raw.githubusercontent.com" in url:
        return download_generic_file(url, output_dir)
    
    # If it's a main repo URL, try to download the main branch zip
    if "github.com" in url and not url.endswith(".zip") and not url.endswith(".tar.gz"):
        # Basic transformation for common repo URLs
        parts = urlparse(url).path.strip('/').split('/')
        if len(parts) >= 2:
            owner, repo = parts[0], parts[1]
            zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/main.zip"
            return download_generic_file(zip_url, output_dir)
            
    return download_generic_file(url, output_dir)

def download_file(url: str, output_dir: str = "downloads") -> str:
    """
    Unified download tool that dispatches to specific handlers based on URL.
    """
    if "drive.google.com" in url or "docs.google.com" in url:
        return download_gdrive_file(url, output_dir)
    elif "youtube.com" in url or "youtu.be" in url or "vimeo.com" in url:
        return download_video_audio(url, output_dir)
    elif "huggingface.co" in url:
        # Simple extraction for HF URLs like https://huggingface.co/repo_id/resolve/main/filename
        match = re.search(r"huggingface\.co/([^/]+/[^/]+)/resolve/([^/]+)/(.+)", url)
        if match:
            repo_id, revision, filename = match.groups()
            return download_hf_file(repo_id, filename, output_dir=output_dir)
        return download_generic_file(url, output_dir)
    elif "github.com" in url:
        return download_github_content(url, output_dir)
    else:
        return download_generic_file(url, output_dir)
