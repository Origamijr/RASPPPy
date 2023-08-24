

def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

class MovingAverage:
    def __init__(self, alpha=0):
        self.alpha = alpha
        self.value = 0
        self.n = 0

    def add(self, x, count=1):
        self.n += count
        if self.alpha == 0:
            self.value += count * (x - self.value) / self.n
        else:
            self.value *= 1 - self.alpha
            self.value += self.alpha * x
        return self.value
    
    def reset(self):
        self.value = 0
        self.n = 0