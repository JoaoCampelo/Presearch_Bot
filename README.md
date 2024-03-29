# Presearch_Bot
Simple bot to automate Presearch searches and get cryptocurrencies daily.

## Notes
The `requirements.txt` file should list all Python libraries that your notebooks
depend on, and they will be installed using:

```
pip install -r requirements.txt
```

# How Use
After installing the project's dependencies, the first thing to do is put your email and password for your Presearch account in the accounts.txt file.
Then run the Presearch_Bot.py file using the following command:

```
python Presearch_Bot.py
```

The first time you run the bot you will have to log in to your account, the only thing you will have to do is the challenge to prove that you are not a robot.

![Challenge](https://user-images.githubusercontent.com/31993611/193428532-4f72b46b-38f6-4c8a-9201-a2d33b83936b.png)

After completing the challenge, you have to go to the command line and press Enter, for the bot to continue the process.

![AfterChallenge](https://user-images.githubusercontent.com/31993611/193428534-4767b1d9-503b-47d6-aa42-8060af7a4a65.png)

Then the bot does the rest by itself. 
The next times when you run the bot it already logs in by itself using cookies.


# Update 2022-11-10
Now, after logging in to the account, a validation is carried out to test if all the daily paid searches have been made, and if all the searches have already been made, the bot displays a message and exits.
A message has also been added that indicates how many tokens have been accumulated in the account so far.

![update20221110](https://user-images.githubusercontent.com/31993611/201214161-9bfb7648-2630-4ea4-9c58-36f4fcd1bc03.png)


# Update 2023-05-08
Now it is possible to use a proxy to do our daily searches. The bot creates a list of possible proxies, then tests until it finds a valid proxy to use.
For the bot to run with a proxy we have to go to the "configuration.py" file and set the "proxy" option to True.

![configs](https://user-images.githubusercontent.com/31993611/236926960-998b59d3-896b-470c-9e7c-c9b453a9c74e.png)

In this version, some messages were changed, and new ones were created, so that we can have a better perception of what is happening in the bot.

![NewMessages](https://user-images.githubusercontent.com/31993611/236927523-8c534bb3-c34b-460d-a7c9-705336715bf3.png)
