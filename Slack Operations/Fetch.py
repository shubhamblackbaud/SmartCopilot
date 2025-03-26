from modules import SlackAPI
from DBCC import DatabaseManager
import os
import logging

def main():
    slack_token = os.getenv("SLACK_TOKEN")
    server = os.getenv("SQL_SERVER")
    database = os.getenv("SQL_DATABASE")
    username = os.getenv("SQL_USERNAME")
    password = os.getenv("SQL_PASSWORD")

    try:
        # Initialize SlackAPI and DatabaseManager
        slack_api = SlackAPI(slack_token)
        db_manager = DatabaseManager(server, database, username, password)

        # Create tables
        db_manager.create_tables()

        # Fetch and store data
        channels = slack_api.fetch_channels()
        for channel in channels:
            process_channel(db_manager, slack_api, channel)

        # Commit changes
        db_manager.commit()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        db_manager.close()

def process_channel(db_manager, slack_api, channel):
    channel_id = channel["id"]
    messages = slack_api.fetch_channel_messages(channel_id)
    db_manager.insert_channel_messages(messages)
    for message in messages:
        if "thread_ts" in message:
            thread_ts = message["thread_ts"]
            thread_messages = slack_api.fetch_thread_messages(channel_id, thread_ts)
            db_manager.insert_thread_messages(thread_messages, thread_ts)

if __name__ == "__main__":
    main()
