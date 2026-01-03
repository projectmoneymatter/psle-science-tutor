# PSLE Science AI Tutor - Setup Guide

## Step 1: Install Python

If Python is not installed:

1. **Download Python**: Go to https://www.python.org/downloads/
2. **Install Python 3.9 or later**
3. **IMPORTANT**: During installation, check the box "Add Python to PATH"
4. **Restart your terminal/PowerShell** after installation

## Step 2: Verify Installation

Open PowerShell and run:
```powershell
python --version
```

You should see something like: `Python 3.11.x`

## Step 3: Install Dependencies

Run one of these commands:

```powershell
# Method 1 (recommended)
python -m pip install -r requirements.txt

# Method 2 (alternative)
pip install -r requirements.txt
```

## Step 4: Set Up API Key

### Option A: Using .env file (Recommended for local development)

1. Create a file named `.env` in the project folder
2. Add this line to the file:
```
GOOGLE_API_KEY=your_api_key_here
```
3. Replace `your_api_key_here` with your actual Google API key

### Option B: Using Streamlit Secrets (Recommended for deployment)

1. Create a folder named `.streamlit` in the project folder
2. Create a file named `secrets.toml` inside `.streamlit`
3. Add this content:
```toml
GOOGLE_API_KEY = "your_api_key_here"
```

## Step 5: Get Your Google API Key

1. Go to https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Create a new API key
4. Copy the key and add it to your `.env` file or `secrets.toml`

## Step 6: Run the Application

```powershell
streamlit run app.py
```

The app will open in your default web browser automatically!

## Troubleshooting

### "pip is not recognized"
- Make sure Python is installed and added to PATH
- Try: `python -m pip install -r requirements.txt`

### "streamlit is not recognized"
- Install Streamlit: `python -m pip install streamlit`
- Then run: `python -m streamlit run app.py`

### "Module not found" errors
- Make sure all dependencies are installed: `python -m pip install -r requirements.txt`

### API Key errors
- Double-check your `.env` file or `secrets.toml` file
- Make sure there are no extra spaces or quotes around the API key
- Restart the Streamlit app after adding the API key
