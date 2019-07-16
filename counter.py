import json

class Counter:

    def __init__(self, settings):
        self.file = settings['file']
        self.map = json.load(open(self.file))
        self.num_counts = settings['num_counts_before_flush']
        self.num = 0

    def incr(self, topic, key):
        self.num += 1
        if topic not in self.map:
            self.map[topic] = {}
        if key in self.map[topic]:
            self.map[topic][key] += 1
        else:
            self.map[topic][key] = 1
        
        # flush if necessary
        if self.num >= self.num_counts:
            print "[coutner] dumping counters to map"
            self.num = 0
            with open(self.file, 'w') as f:
                json.dump(self.map, f, indent=2)
