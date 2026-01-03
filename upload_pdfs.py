"""
Script to upload PSLE Science PDFs to Gemini API for caching.

This script:
1. Loads API key from .env file
2. Finds all PDF files in the 'pdfs' folder
3. Uploads each PDF to Gemini API
4. Prints the file URIs (file.name) for use in the main app
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    print("❌ Error: GOOGLE_API_KEY not found in .env file")
    exit(1)

genai.configure(api_key=api_key)

# Find PDFs folder
pdfs_folder = Path('pdfs')

# Check if folder exists
if not pdfs_folder.exists():
    print(f"❌ Error: 'pdfs' folder not found. Please create it and add PDF files.")
    exit(1)

# Find all PDF files
pdf_files = list(pdfs_folder.glob('*.pdf'))

# Check if folder is empty
if len(pdf_files) == 0:
    print("⚠️  Warning: The 'pdfs' folder is empty. No PDF files found.")
    print(f"   Please add PDF files to: {pdfs_folder.absolute()}")
    exit(0)

print(f"📚 Found {len(pdf_files)} PDF file(s) to upload:\n")

# List files to be uploaded
for pdf_file in pdf_files:
    print(f"   - {pdf_file.name}")

print("\n" + "="*60)
print("🚀 Starting upload process...\n")

# Upload files and collect URIs
uploaded_files = []
failed_files = []

for pdf_file in pdf_files:
    try:
        print(f"📤 Uploading: {pdf_file.name}...")
        
        # Upload file to Gemini API
        uploaded_file = genai.upload_file(path=str(pdfs_folder / pdf_file.name))
        
        uploaded_files.append({
            'filename': pdf_file.name,
            'uri': uploaded_file.name
        })
        
        print(f"   ✅ Success! URI: {uploaded_file.name}\n")
        
    except Exception as e:
        print(f"   ❌ Error uploading {pdf_file.name}: {str(e)}\n")
        failed_files.append(pdf_file.name)

print("="*60)
print("\n📋 UPLOAD SUMMARY\n")
print(f"✅ Successfully uploaded: {len(uploaded_files)} file(s)")
if failed_files:
    print(f"❌ Failed to upload: {len(failed_files)} file(s)")

print("\n" + "="*60)
print("📝 FILE URIs (Copy these for your main app):\n")

if uploaded_files:
    for item in uploaded_files:
        print(f"Filename: {item['filename']}")
        print(f"URI: {item['uri']}")
        print()
else:
    print("No files were successfully uploaded.")

print("="*60)
print("\n💡 To use these files in your app, reference them by their URI (file.name)")
print("   Example: file = genai.get_file('the-uri-here')")

