# Google Maps Scraper Web Application

A Flask-based web application for scraping business information from Google Maps.

## Features

- Modern web interface with Bootstrap 5
- Configurable search parameters
- Real-time scraping status updates
- Clean results display
- Customizable search queries
- Error handling and validation

## Requirements

- Python 3.8+
- Chrome Browser
- ChromeDriver compatible with your Chrome version

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your configuration:
   ```
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here
   ```

## Usage

1. Start the Flask application:
   ```bash
   flask run
   ```
2. Open your browser and navigate to `http://localhost:5000`
3. Enter your ChromeDriver path and Chrome browser path
4. Configure your search parameters
5. Click "Start Scraping" to begin

## Notes

- Make sure your ChromeDriver version matches your Chrome browser version
- The application requires proper paths to both Chrome and ChromeDriver
- Results are displayed in a clean, tabulated format
- The scraper includes an inactivity timeout to prevent hanging
