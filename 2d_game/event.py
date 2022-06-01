class KeyboardEvent(object):
    PRESSED: str = 'pressed'
    UP: str = 'up'
    DOWN: str = 'down'

    pygame_event: str
    # function: function
    event_object: object
    event_type: str # one of the PRESSED UP DOWN
    function_args: tuple# function: function

    def __init__(self, event, event_type, function, function_args = ()):
        self.pygame_event = event
        self.event_type = event_type
        self.function = function
        self.function_args = function_args

    # def check_event(self, )
    def get_event_type(self):
        return self.event_type

    def get_pygame_event(self):
        return self.pygame_event

    def run_event(self):
        args = () if self.function_args is None else self.function_args
        self.function(*args)


class MouseEvent(object):
    #pygame_event :
    # function: function
    event_object: object
    is_method: bool


class EventsListener(object):
    list_of_events: list[KeyboardEvent | MouseEvent]
    keyboard_prassed_events: dict
    keyboard_up_events: dict
    keyboard_down_events: dict


    def __init__(self):
        self.keyboard_prassed_events = dict()
        self.keyboard_up_events = dict()
        self.keyboard_down_events = dict()
        self._last_pressed = pygame.key.get_pressed()

    def add(self, event):
        if isinstance(event, KeyboardEvent):
            pe = event.get_pygame_event()
            et = event.get_event_type()

            if et == KeyboardEvent.PRESSED:
                if pe not in self.keyboard_prassed_events:
                    self.keyboard_prassed_events[pe] = list()
                self.keyboard_prassed_events[pe].append(event)

            elif et == KeyboardEvent.UP:
                if pe not in self.keyboard_up_events:
                    self.keyboard_up_events[pe] = list()
                self.keyboard_up_events[pe].append(event)

            elif et == KeyboardEvent.DOWN:
                if pe not in self.keyboard_down_events:
                    self.keyboard_down_events[pe] = list()
                self.keyboard_down_events[pe].append(event)

    def update(self):
        # event = pygame.event.get()
        pressed = pygame.key.get_pressed()

        for pygame_event_name in self.keyboard_prassed_events:
            if pressed[pygame_event_name]:
                for event in self.keyboard_prassed_events[pygame_event_name]:
                    event.run_event()

        for pygame_event_name in self.keyboard_up_events:
            if not pressed[pygame_event_name] and self._last_pressed[pygame_event_name]:
                for event in self.keyboard_up_events[pygame_event_name]:
                    event.run_event()

        for pygame_event_name in self.keyboard_down_events:
            if pressed[pygame_event_name] and not self._last_pressed[pygame_event_name]:
                for event in self.keyboard_down_events[pygame_event_name]:
                    event.run_event()

        self._last_pressed = pressed
