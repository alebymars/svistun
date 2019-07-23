<a href="https://heroku.com/deploy?template=https://github.com/alebymars/svistun">A</a><br><br>
<hr>

### Running locally
#### 1. Download
```bash
$ git clone https://github.com/alebymars/svistun.git
$ cd markov
```
#### 2. Requirements
```bash
$ pipenv install --dev
```
#### 3. Env vars
In order to run the bot, you need to define the env var `TELEGRAM_TOKEN` (to generate a bot token follow [these instructions](https://core.telegram.org/bots#creating-a-new-bot)):
```bash
$ cp local.env .env
$ vim .env
```
#### 4. Run tests
```bash
$ make test
```
#### 4. Run the bot
```bash
$ make run
```
#### 5. Permissions
Disable the bot privacy settings (it means that the bot will receive all messages, not just the ones starting with "/").
Run `/sentence` (*or the command you defined using the env var `SENTENCE_COMMAND`*) to generate random sentences.
If you wish to delete the model, run `/remove`.

Have fun :)
