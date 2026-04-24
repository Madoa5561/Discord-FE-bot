# Discord IT Exam Bot

This project is a Discord bot designed to manage a question set for the Information Technology Engineer Examination. The bot posts a daily question at midnight to a specified channel, allowing users to interact with the question through buttons for their answers. It tracks responses and mentions the fastest responder.

## Project Structure

```
discord-it-exam-bot
├── src
│   ├── main.py                # Entry point of the Discord bot
│   ├── cogs
│   │   └── daily_question.py   # Logic for posting daily questions
│   ├── utils
│   │   └── question_manager.py  # Handles loading and management of questions
│   └── data
│       └── questions.json      # Stores questions, options, and explanations
├── .env                        # Environment variables for the bot
├── requirements.txt            # List of dependencies
└── README.md                   # Documentation for the project
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone https://github.com/Madoa5561/Discord-FE-bot
   cd Discord-FE-bot
   ```

2. **Install dependencies:**
   Make sure you have Python 3.8 or higher installed. Then, run:
   ```
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file in the root directory and add your Discord bot token:
   ```
   DISCORD_TOKEN=your_token_here
   ```

4. **Add questions:**
   Edit the `src/data/questions.json` file to include your questions, options, and explanations.

## Usage

To run the bot, execute the following command:
```
python src/main.py
```

The bot will start and post a question daily at midnight in the specified channel. Users can respond to the question using the provided buttons, and the bot will mention the fastest responder.

## Contributing

Feel free to submit issues or pull requests for improvements or bug fixes.
