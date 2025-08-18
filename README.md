
# AI Content Generation System

An automated content creation pipeline that generates high-quality articles using Google Gemini AI with WordPress publishing capabilities.

## Features

- 🤖 **AI-Powered Content Generation** - Uses Google Gemini AI for creating SEO-optimized articles
- 📊 **Excel Integration** - Bulk processing from Excel files for scalable content creation
- 📝 **WordPress Publishing** - Direct publishing to WordPress with featured images
- 🎯 **SEO Optimization** - Structured HTML output with proper formatting
- 🖥️ **Web Interface** - User-friendly Flask web app for easy management
- 💾 **Database Storage** - SQLite database for article management and tracking

## Project Structure

```
├── modules/
│   ├── generation.py      # AI content generation with Gemini
│   ├── processing.py      # Content processing and formatting
│   ├── storage.py         # Database operations
│   └── wordpress_publisher.py  # WordPress API integration
├── templates/
│   └── index.html         # Web interface template
├── uploads/               # File upload directory
├── .env-copy             # Environment variables template
├── demo_app.py           # Flask web application
├── main.py               # Async batch processing script
├── main_sync.py          # Synchronous batch processing script
├── articles.db           # SQLite database
└── topics.xlsx           # Sample topics file
```

## Quick Start

### 1. Environment Setup

1. Copy the environment template file:
   ```bash
   cp .env-copy .env
   ```

2. Edit the `.env` file and add your credentials:
   ```
   GOOGLE_API_KEY=your_gemini_api_key_here
   MODEL_NAME=gemini-2.0-flash-lite
   WP_URL=https://yoursite.com
   WP_USER=admin
   WP_APP_PASSWORD=your_app_password_here
   ```

### 3. Dependencies

Run the following command to install all the dependencies
   ```
   pip install -r requirements.txt
   ```

### 3. Running the Application

**Web Interface (Recommended):**
```bash
python demo_app.py
```
Access the web interface at `http://localhost:5000`

**Batch Processing:**
```bash
# Async processing (faster)
python main.py

# Sync processing (sequential)
python main_sync.py
```

### 4. Usage Options

**Single Article Generation:**
- Use the web interface to generate individual articles
- Enter a topic and optionally publish directly to WordPress

**Bulk Processing:**
- Upload an Excel file with topics in any column
- Select the column containing your topics
- Choose whether to publish all articles to WordPress
- Process multiple articles automatically

## Configuration

### Content Settings
Modify `modules/generation.py` to adjust:
- AI model selection (currently using `gemini-2.0-flash-lite`)
- Content length and structure requirements
- SEO optimization parameters

## API Endpoints

- `GET /` - Web interface
- `POST /generate` - Generate single article
- `POST /upload_excel` - Upload Excel file
- `POST /process_excel` - Process bulk topics

## Database Schema

The system uses SQLite with the following structure:
- **articles** table: id, title, content, topic, created_at
- Automatic article storage and retrieval
- Built-in duplicate prevention

## Performance

**Async Processing:**
- Concurrent limit: 10 simultaneous requests
- Processes ~50 articles in ~20 seconds
- Controlled rate limiting to prevent API overload

**Sync Processing:**
- Sequential processing with 2-second delays
- More predictable but slower execution
- Better for debugging and monitoring

## Future Considerations

### 🎨 Dynamic Image Generation
**Current State:** Uses fixed featured images for all articles
**Planned Enhancement:**
- Integrate AI image generation (DALL-E, Midjourney, or Stable Diffusion)
- Generate contextual images based on article content
- Automatic image optimization and WordPress upload
- Multiple image sizes for different content sections

**Implementation Approach:**
```python
# Future image generation module
async def generate_article_image(title: str, content_summary: str):
    # Use AI to create relevant images
    # Optimize for web performance
    # Upload to WordPress media library
    pass
```

### ⚡ Enhanced Async Performance
**Current State:** Basic async implementation with semaphore limiting
**Planned Improvements:**
- Convert Flask app to Quart (async Flask alternative)
- Implement real-time progress updates via WebSockets
- Add async database operations with aiosqlite
- Enhanced error handling and retry mechanisms
- Background task processing with Celery or similar

**Performance Goals:**
- 10x faster bulk processing
- Real-time progress tracking in web interface
- Concurrent image generation alongside content
- Smart rate limiting based on API quotas

### 🔧 Additional Enhancements
- **Multi-language Support** - Generate content in multiple languages
- **Content Templates** - Predefined article structures for different niches
- **Analytics Dashboard** - Track performance metrics and success rates
- **Content Scheduling** - Schedule WordPress publications
- **API Integration** - RESTful API for external integrations
- **Content Quality Scoring** - AI-powered content quality assessment

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - Feel free to use and modify for your projects.

## Support

For issues and questions:
- Check the console output for detailed error messages
- Ensure all API keys are properly configured
- Verify WordPress credentials and permissions
- Review the logs in the database for processing history

## Deployment

Deploy on Replit for easy hosting and scaling:
1. Import this repository to Replit
2. Set environment variables in Secrets
3. Use the built-in deployment features
4. Configure custom domains if needed

---

**Note:** This system is designed for educational and small-scale commercial use. For enterprise deployments, consider additional security measures and API rate limit management.
