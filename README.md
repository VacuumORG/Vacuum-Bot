# Vacuum Bot

Vacuum Bot is a Discord bot developed for the [Vacuum community](https://twitter.com/VacuumORG). It is built using
Python and the discord.py library. The bot provides various features to enhance the community's experience.

## Features

- **Pomodoro**: The bot allows users to start and manage Pomodoro sessions, helping them stay focused and productive.
- **Job Search**: Users can utilize the bot to search for job opportunities.

## Getting Started

To run Vacuum Bot locally, follow these steps:

1. Make sure that FFmpeg was installed in your system.

   Windows user:
    1. Can be installed [using the installer](https://video.stackexchange.com/a/20496) and setting up environment
       variables.
    2. Or [using a package manager](https://video.stackexchange.com/a/28321) like chocolatey


2. Clone the repository:

```shell
git clone https://github.com/masachetti/Vacuum-Bot.git
cd Vacuum-Bot
```

3. Install the required dependencies:

```shell
pip install -r requirements.txt
```

4. Obtain a Discord bot token
   by [creating a new bot](https://discord.com/developers/docs/getting-started#step-1-creating-an-app) on the Discord
   Developer Portal.

5. Create a `.env` file in the root directory and add
   your [bot token](https://www.writebots.com/discord-bot-token/#4-retrieve-your-token)
   and [guild id](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-):

```plaintext
TOKEN=YOUR_TOKEN
GUILD_ID=YOUR_GUILD_ID
```

5. [Add the bot](https://www.writebots.com/discord-bot-token/#5-add-your-bot-to-a-discord-server) to your server with
   those permissions:

```plaintext
bot
bot:Send Messages
bot:Connect
bot:Speak
applications.commands
```

7. Run the bot:

```shell
python main.py
```

## Project Structure

The project follows a feature-based structure, where each feature has its own folder and cog. This organization allows
for modularity and easy addition of new features. Additionally, a shared folder exists to store files that are used
across multiple features.

```
├── shared
│   ├── file1.py
│   └── file2.py
├── cogs
│   ├── pomodoro.py
│   ├── vagas.py
│   ├── other_feature.py
│   ├── ...
├── pomodoro
│   ├── file.py
│   ├── ...
├── jobs
│   ├── file.py
│   ├── ...
├── other_feature
│   ├── file.py
│   ├── ...
├── main.py
└── ...
```

## Contributing

Contributions to Vacuum Bot are welcome! If you would like to contribute, please follow these guidelines:

1. Fork the repository and create a new branch for your feature/bug fix.
2. Commit your changes with descriptive commit messages.
3. Push your changes to your forked repository.
4. Submit a pull request, explaining the changes you have made.

Please ensure that your code follows the project's coding conventions.

## License

This project is licensed under the [MIT License](LICENSE).
