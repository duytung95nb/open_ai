# News Summary CLI with OpenAI

A Python command-line application that fetches news articles from Vietnamese RSS feeds (VnExpress and Thanh Nien), generates AI-powered summaries using OpenAI, and outputs formatted Markdown reports.

## Features

- **RSS Feed Fetching**: Automatically fetches articles from multiple Vietnamese news sources
- **AI Summarization**: Uses OpenAI API to generate concise summaries in Vietnamese
- **Duplicate Prevention**: Tracks processed articles to avoid re-summarizing
- **Multiple Output Formats**:
  - Individual article summaries
  - Daily digest with categorized themes
- **Markdown Output**: Clean, formatted Markdown files for easy reading

## Prerequisites

- Python 3.8 or higher
- OpenAI API key

## Installation

1. Clone or download this repository

2. Install dependencies:

```bash
pip install -r requirements.txt
```

If using python3

```bash
python3 -m pip install -r requirements.txt
```

3. Set up your OpenAI API key:

   Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=your_openai_api_key_here
```

Alternatively, you can set the environment variable directly:

```bash
export OPENAI_API_KEY=your_openai_api_key_here
```

## Usage

### Basic Commands

**Fetch and process new articles (generates both individual summaries and daily digest):**

```bash
python main.py fetch
```

**Generate only individual article summaries:**

```bash
python main.py fetch --individual
```

**Generate only daily digest:**

```bash
python main.py fetch --digest
```

**Specify custom output directory:**

```bash
python main.py fetch --output-dir ./my_summaries
```

**List all processed articles:**

```bash
python main.py list
```

**Clear processed articles database:**

```bash
python main.py clear
```

### Output Files

The application generates Markdown files in the `summaries/` directory (or your specified output directory):

- `individual_YYYY-MM-DD.md` - Individual article summaries
- `digest_YYYY-MM-DD.md` - Daily digest with categorized themes

## Configuration

### Environment Variables

- `OPENAI_API_KEY` (required): Your OpenAI API key
- `OPENAI_MODEL` (optional): OpenAI model to use (default: `gpt-4o-mini`)

### RSS Feeds

The application fetches from these RSS feeds:

- VnExpress: https://vnexpress.net/rss/tin-moi-nhat.rss
- Thanh Nien: https://thanhnien.vn/rss/home.rss

To modify the feeds, edit `rss_fetcher.py` and update the `RSS_FEEDS` list.

## How It Works

1. **Fetch RSS Feeds**: Downloads and parses RSS feeds from configured sources
2. **Filter New Articles**: Checks against processed articles database to find new content
3. **Generate Summaries**: Uses OpenAI API to create concise summaries in Vietnamese
4. **Format Output**: Formats summaries as clean Markdown files
5. **Track Processed**: Saves article IDs to avoid reprocessing

## Project Structure

```
.
├── main.py              # CLI entry point
├── rss_fetcher.py      # RSS feed fetching and parsing
├── storage.py          # Article tracking and storage
├── openai_client.py    # OpenAI API integration
├── formatter.py        # Markdown formatting
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variable template
├── README.md          # This file
└── summaries/         # Output directory (created automatically)
```

## Error Handling

The application includes comprehensive error handling:

- Network errors when fetching RSS feeds
- API errors with retry logic and exponential backoff
- File I/O errors with proper logging
- Invalid data validation
- Graceful handling of missing or malformed articles

## Troubleshooting

**"OPENAI_API_KEY environment variable is not set"**

- Make sure you've created a `.env` file with your API key, or set the environment variable

**"No articles fetched from RSS feeds"**

- Check your internet connection
- Verify the RSS feed URLs are accessible
- Check the logs for specific error messages

**"Failed to generate summaries"**

- Verify your OpenAI API key is valid
- Check your OpenAI account has sufficient credits
- Review the logs for API error messages

**Permission errors when writing files**

- Ensure the output directory is writable
- Check file system permissions

## License

This project is provided as-is for educational and personal use.

## Contributing

Feel free to submit issues or pull requests for improvements.
