from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock

KV = '''
MainScreen:
    orientation: "vertical"
    padding: 20
    spacing: 20

    MDLabel:
        text: "Typing Speed Test"
        halign: "center"
        font_style: "H5"

    MDLabel:
        text: "Set Your Paragraph (Optional):"
        halign: "left"
        font_size: 18

    ScrollView:
        size_hint_y: None
        height: dp(120)  # Adjust height for approximately 5 lines
        MDTextField:
            id: custom_paragraph_field
            hint_text: "Enter your paragraph here..."
            multiline: True

    MDRaisedButton:
        text: "Use Custom Paragraph"
        size_hint_y: None
        height: dp(40)
        on_release: app.set_custom_paragraph()

    MDLabel:
        text: "Choose Test Duration:"
        halign: "left"
        font_size: 18

    BoxLayout:
        size_hint_y: None
        height: dp(50)
        spacing: 20

        MDRaisedButton:
            text: "5 Minutes"
            on_release: app.start_test(5)

        MDRaisedButton:
            text: "15 Minutes"
            on_release: app.start_test(15)

    MDLabel:
        text: "Practice Paragraph:"
        halign: "left"
        font_size: 18

    ScrollView:
        MDLabel:
            id: paragraph_label
            text: app.paragraph
            halign: "left"
            font_size: 16
            size_hint_y: None
            height: self.texture_size[1]

    MDLabel:
        text: "Type Here:"
        halign: "left"
        font_size: 18

    MDTextField:
        id: typing_field
        hint_text: "Start typing here..."
        multiline: True
        size_hint_y: None
        height: dp(120)

    MDLabel:
        id: timer_label
        text: "Time Left: --:--"
        halign: "center"
        font_size: 18

    MDRaisedButton:
        text: "Submit Test"
        size_hint_y: None
        height: dp(40)
        on_release: app.submit_test()

    ScrollView:
        size_hint_y: None
        height: dp(100)
        MDLabel:
            id: error_highlight
            text: ""
            halign: "left"
            font_size: 16
            markup: True

    MDLabel:
        id: result_label
        text: ""
        halign: "center"
        font_size: 18
'''

class MainScreen(BoxLayout):
    pass

class TypingTestApp(MDApp):
    paragraph = "The quick brown fox jumps over the lazy dog. " * 100  # Default long paragraph
    timer_duration = 0  # Duration of the test in seconds
    elapsed_time = 0
    timer_running = False
    clock_event = None

    def build(self):
        return Builder.load_string(KV)

    def set_custom_paragraph(self):
        custom_paragraph = self.root.ids.custom_paragraph_field.text.strip()
        if custom_paragraph:
            self.paragraph = custom_paragraph
            self.root.ids.paragraph_label.text = self.paragraph
            self.root.ids.result_label.text = "Custom paragraph set successfully!"
        else:
            self.root.ids.result_label.text = "Custom paragraph is empty!"

    def start_test(self, minutes):
        # Set the timer duration
        self.timer_duration = minutes * 60
        self.elapsed_time = 0
        self.timer_running = True

        # Reset fields
        self.root.ids.typing_field.text = ""
        self.root.ids.error_highlight.text = ""
        self.root.ids.result_label.text = f"Test Started! You have {minutes} minutes."
        self.update_timer(0)

        # Start the timer
        if self.clock_event:
            self.clock_event.cancel()
        self.clock_event = Clock.schedule_interval(self.update_timer, 1)

    def update_timer(self, dt):
        if self.timer_running:
            self.elapsed_time += 1
            time_left = self.timer_duration - self.elapsed_time

            # Update timer display
            minutes = time_left // 60
            seconds = time_left % 60
            self.root.ids.timer_label.text = f"Time Left: {minutes:02}:{seconds:02}"

            # End test if time is up
            if time_left <= 0:
                self.timer_running = False
                if self.clock_event:
                    self.clock_event.cancel()
                self.root.ids.result_label.text = "Time's up! Submit your test to see the results."

    def submit_test(self):
        if not self.timer_running and self.elapsed_time == 0:
            self.root.ids.result_label.text = "Please start the test first!"
            return

        # Stop the timer
        self.timer_running = False
        if self.clock_event:
            self.clock_event.cancel()

        elapsed_minutes = self.elapsed_time / 60  # Convert seconds to minutes

        # Get user input and compare it to the paragraph
        user_input = self.root.ids.typing_field.text.strip()
        target_paragraph = self.paragraph.strip()

        # Calculate words per minute
        words_typed = len(user_input.split())
        wpm = words_typed / elapsed_minutes if elapsed_minutes > 0 else 0

        # Highlight errors
        error_highlight = self.highlight_errors(user_input, target_paragraph)
        self.root.ids.error_highlight.text = error_highlight

        # Count errors
        errors = self.calculate_errors(user_input, target_paragraph)

        # Display the result
        self.root.ids.result_label.text = f"Words Per Minute: {wpm:.2f}\nErrors: {errors}"

    def highlight_errors(self, user_input, target_paragraph):
        result = ""
        min_length = min(len(user_input), len(target_paragraph))

        # Compare character by character
        for i in range(min_length):
            if user_input[i] == target_paragraph[i]:
                result += f"[color=#000000]{user_input[i]}[/color]"  # Correct characters in black
            else:
                result += f"[color=#FF0000]{user_input[i]}[/color]"  # Errors in red

        # Add remaining characters (extra or missing)
        if len(user_input) > len(target_paragraph):
            result += f"[color=#FF0000]{user_input[min_length:]}[/color]"  # Extra characters in red
        elif len(target_paragraph) > len(user_input):
            result += f"[color=#FF0000]{target_paragraph[min_length:]}[/color]"  # Missing characters in red

        return result

    def calculate_errors(self, user_input, target_paragraph):
        errors = 0
        min_length = min(len(user_input), len(target_paragraph))

        # Compare character by character
        for i in range(min_length):
            if user_input[i] != target_paragraph[i]:
                errors += 1

        # Add extra characters as errors
        errors += abs(len(user_input) - len(target_paragraph))
        return errors

if __name__ == "__main__":
    TypingTestApp().run()