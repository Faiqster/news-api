# News API

A Flask-based web service that scrapes and summarizes news articles from Euronews (`euronews.com`) based on a provided search keyword. It uses headless Google Chrome and Selenium to find relevant articles via DuckDuckGo, extracts paragraph text, and returns an extractive summary in JSON format.

## How to Run

### Using Docker (Recommended)

1. **Build the Docker image:**
   ```bash
   docker build -t news-api .
   ```

2. **Run the container:**
   ```bash
   docker run -d -p 7000:7000 --name news-api news-api
   ```

### Running Locally

Ensure Google Chrome and compatible ChromeDriver are installed and available on your system path.

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the application:**
   ```bash
   python app.py
   ```

## Usage / Endpoints

- **Root Info:**
  `GET http://localhost:7000/`
- **Search & Summarize:**
  `GET http://localhost:7000/get?keyword=<your_keyword>`

**Example:**
```bash
curl "http://localhost:7000/get?keyword=technology"
```

