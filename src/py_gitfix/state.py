class State:
    """
    Defines an individual state within the state machine.
    """

    def __init__(self, options=None):
        self.options = None

    def parse_choice(self, event):
        try:
            code = int(event)
        except ValueError:
            return None
        if not self.options or code > len(self.options):
            return None
        else:
            return self.options[code]

    def on_event(self, event):
        """
        Handle events that are delegated to this State.
        """
        pass

    def __repr__(self):
        """
        Leverages the __str__ method to describe the State.
        """
        return self.__str__()

    def __str__(self):
        """
        Returns the name of the State.
        """
        return self.__class__.__name__
