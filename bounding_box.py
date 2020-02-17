class BoundingBox:
    def __init__(self, xmin, ymin, xmax, ymax):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax

    def surface(self):
        return (self.xmax - self.xmin) * (self.ymax - self.ymin)

    def center(self):
        return (
            self.xmin + int((self.xmax - self.xmin) / 2),
            self.ymin + int((self.ymax - self.ymin) / 2)
        )
