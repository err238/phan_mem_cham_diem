class InputManager:

    def __init__(self, combobox, values):

        self.box = combobox
        self.values = values

        self.box["values"] = values

        self.box.bind("<KeyRelease>", self.autocomplete)

    def set_values(self, values):

        self.values = values
        self.box["values"] = values

    def autocomplete(self, event=None):

    # nếu bấm backspace thì chỉ filter, không autocomplete
        if event and event.keysym == "BackSpace":
            text = self.box.get()

            matches = [
                v for v in self.values
                if str(v).lower().startswith(text.lower())
            ]

            self.box["values"] = matches
            return

        text = self.box.get()

        if text == "":
            self.box["values"] = self.values
            return

        matches = [
            v for v in self.values
            if str(v).lower().startswith(text.lower())
        ]

        self.box["values"] = matches

        if matches:

            match = str(matches[0])

            if match != text:

                self.box.delete(0, "end")
                self.box.insert(0, match)

                self.box.selection_range(len(text), "end")

