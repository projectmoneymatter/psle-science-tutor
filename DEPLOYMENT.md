# Streamlit Community Cloud Deployment Guide

This guide will help you deploy the PSLE Science AI Tutor to Streamlit Community Cloud.

## Prerequisites

1. **GitHub Account**: Your code needs to be in a GitHub repository
2. **Streamlit Cloud Account**: Sign up at https://share.streamlit.io/ (free)
3. **Google API Key**: Get your Gemini API key from https://makersuite.google.com/app/apikey

## Step-by-Step Deployment

### 1. Push Your Code to GitHub

Make sure your code is committed and pushed to a GitHub repository:

```bash
git init
git add .
git commit -m "Initial commit: PSLE Science AI Tutor"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

**Important**: The `.env` file and `pdfs/` folder are in `.gitignore` and will NOT be uploaded to GitHub (this is intentional for security).

### 2. Deploy to Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository and branch (usually `main`)
5. Set the main file path to: `app.py`
6. Click "Deploy"

### 3. Add Your API Key (Secrets)

After deployment, you need to add your Google API key:

1. In your Streamlit Cloud app dashboard, click on "⚙️ Settings" (or "⋮" → "Settings")
2. Click on "Secrets" in the left sidebar
3. Add the following in the secrets editor:

```toml
GOOGLE_API_KEY = "your_actual_api_key_here"
```

4. Click "Save"
5. The app will automatically restart with the new secrets

### 4. Verify Deployment

1. Your app should now be accessible at: `https://<your-app-name>.streamlit.app`
2. Test the app:
   - Try generating a quiz question
   - Upload a worksheet image for marking
   - Check the dashboard

## File Structure for Deployment

```
your-repo/
├── app.py                 # Main application (required)
├── requirements.txt       # Dependencies (required)
├── .gitignore            # Git ignore rules
├── upload_pdfs.py        # Optional: PDF upload script (local use only)
├── SETUP_GUIDE.md        # Documentation
└── DEPLOYMENT.md         # This file
```

**Files NOT uploaded (in .gitignore)**:
- `.env` - Contains API keys (use Streamlit Cloud secrets instead)
- `pdfs/` - Contains copyrighted PDF files
- `__pycache__/` - Python cache files
- `*.db` - Database files

## How Secrets Work

- **Local Development**: Uses `.env` file (loaded by `python-dotenv`)
- **Streamlit Cloud**: Uses `st.secrets` (set via web interface)
- The app automatically detects which environment it's running in

## Storage Notes

- **Session State**: The app uses `st.session_state` for temporary storage
  - Works perfectly on Streamlit Cloud
  - Data persists during a user session
  - Resets when the app restarts or user refreshes

- **Permanent Storage**: Currently not implemented
  - For persistent data across sessions, consider:
    - Google Sheets API
    - Firebase / Firestore
    - Supabase
    - Streamlit's built-in database features

## Troubleshooting

### App fails to start

1. **Check requirements.txt**: Ensure all dependencies are listed
2. **Check secrets**: Verify `GOOGLE_API_KEY` is set correctly in Streamlit Cloud secrets
3. **Check logs**: View logs in Streamlit Cloud dashboard for error messages

### API Key errors

- Ensure the key is set in Streamlit Cloud secrets (not just in `.env`)
- Verify the key is valid and has Gemini API access enabled
- Check for extra spaces or quotes in the secrets

### Module not found errors

- Verify `requirements.txt` includes all necessary packages
- Check Streamlit Cloud logs for specific missing modules
- Ensure package versions are compatible

### PDF upload script

- The `upload_pdfs.py` script is for local use only
- PDF files should not be committed to GitHub (in `.gitignore`)
- For cloud deployment, consider using Gemini's file upload API directly in the app

## Support

For issues with:
- **Streamlit Cloud**: Check https://docs.streamlit.io/streamlit-community-cloud
- **This App**: Review error logs in the Streamlit Cloud dashboard

