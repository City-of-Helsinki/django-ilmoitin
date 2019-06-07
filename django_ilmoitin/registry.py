class NotificationsRegistry:
    registry = {}

    def register(self, code, label):
        self.registry[code] = label


notifications = NotificationsRegistry()
