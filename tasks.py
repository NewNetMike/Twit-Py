class Tasks:
    def __init__(self, handle=0, id_=0, task_dict=0, xml=None):
        if xml is None:
            self.handle = handle
            self.id = id_
            self.tasks = task_dict
        else:
            d = {}
            for i in range(24):
                d[i] = []
            for t in xml.findall("task"):
                args = t.get("time").split(" ")
                if len(args) == 1:
                    d[int(args[0])].append(t.text)
                if len(args) == 2:
                    r = range(int(args[0]), int(args[1]) + 1)
                    for i in r:
                        d[i].append(t.text)
                if len(args) == 3:
                    r = range(int(args[0]), int(args[1]) + 1, int(args[2]))
                    for i in r:
                        d[i].append(t.text)
            self.tasks = d
    def get(self):
        return self.tasks