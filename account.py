import tasks

master_account = ""

def set_master(uname):
    global master_account
    master_account = uname

class Account:
    def __init__(self, consumer_key=0, consumer_secret=0, access_token=0, access_token_secret=0, handle=0, id_=0, xml=None):
        if xml is None:
            self.consumer_key = consumer_key
            self.consumer_secret = consumer_secret
            self.access_token = access_token
            self.access_token_secret = access_token_secret
            self.handle = handle
            self.id = id_
        else:
            self.consumer_key = xml.find("consumer_key").text
            self.consumer_secret = xml.find("consumer_secret").text
            self.access_token = xml.find("access_token").text
            self.access_token_secret = xml.find("access_token_secret").text
            self.handle = xml.get("handle")
            self.id = xml.get("id")

    def add_tasks(self, handle=0, id_=0, task_dict=0, xml=None):
        if xml is None:
            self.tasks = tasks.Tasks(handle, id_, task_dict)
        else:
            self.tasks = tasks.Tasks(xml=xml)