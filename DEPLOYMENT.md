# 🚀 Deploy to Render

This guide will help you deploy your Document QnA app to Render.

## Prerequisites

1. **GitHub Repository**: Push your code to a GitHub repository
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **API Keys**: You'll need:
   - AstraDB API Endpoint and Token
   - MistralAI API Key

## Deployment Steps

### Method 1: Using render.yaml (Recommended)

1. **Push to GitHub**: Ensure your code is in a GitHub repository
2. **Connect to Render**: 
   - Go to your Render dashboard
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` file

3. **Set Environment Variables**:
   - In your Render service dashboard, go to "Environment"
   - Add these variables:
     ```
     ASTRA_DB_API_ENDPOINT=your_astra_endpoint
     ASTRA_DB_APPLICATION_TOKEN=your_astra_token
     MISTRAL_API_KEY=your_mistral_key
     ```

4. **Deploy**: Click "Create Blueprint" and Render will deploy automatically

### Method 2: Manual Deployment

1. **Create Web Service**:
   - Go to Render dashboard → "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service**:
   - **Name**: `document-qna-app`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run main.py --server.port $PORT --server.address 0.0.0.0`

3. **Set Environment Variables** (same as above)

4. **Deploy**: Click "Create Web Service"

## Important Notes

### OCR Limitations
- **Free Tier**: OCR (image processing) may not work on Render's free tier due to missing Tesseract
- **Paid Tier**: For OCR support, upgrade to a paid plan and install Tesseract

### File Storage
- Files are stored in `/tmp/uploads` and cleaned up after 1 hour
- For persistent storage, consider using cloud storage (AWS S3, etc.)

### Environment Variables
Never commit your `.env` file to Git. Use Render's environment variable interface.

## Troubleshooting

### Build Failures
- Check that all dependencies are in `requirements.txt`
- Ensure Python version compatibility (3.9.16)

### Runtime Errors
- Check Render logs in the dashboard
- Verify environment variables are set correctly
- Ensure API keys are valid

### OCR Issues
- Free tier: OCR will show a warning but continue with other file types
- Paid tier: Install Tesseract via build script if needed

## Monitoring

- **Logs**: Available in Render dashboard
- **Metrics**: Monitor CPU, memory usage
- **Uptime**: Render provides uptime monitoring

## Scaling

- **Free Tier**: 750 hours/month, sleeps after inactivity
- **Paid Plans**: Always-on, better performance, custom domains

## Security

- Environment variables are encrypted
- HTTPS is enabled by default
- No sensitive data in code repository
