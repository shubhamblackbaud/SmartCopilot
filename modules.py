import requests

class SlackAPI:
    def __init__(self, slack_token):
        self.slack_token = slack_token
        self.headers = {"Authorization": f"Bearer {self.slack_token}"}

    def fetch_channels(self):
        url = "https://slack.com/api/conversations.list"
        response = requests.get(url, headers=self.headers)
        return response.json()["channels"]

    def fetch_channel_messages(self, channel_id):
        url = f"https://slack.com/api/conversations.history?channel={channel_id}"
        response = requests.get(url, headers=self.headers)
        return response.json()["messages"]

    def fetch_thread_messages(self, channel_id, thread_ts):
        url = f"https://slack.com/api/conversations.replies?channel={channel_id}&ts={thread_ts}"
        response = requests.get(url, headers=self.headers)
        return response.json()["messages"]
