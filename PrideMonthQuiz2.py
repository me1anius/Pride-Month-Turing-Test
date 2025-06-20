import tkinter as tk
import csv
import json
import random
import time

class PrideQuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pride Quiz")
        self.max_questions = 10
        self.quotes = self.load_quotes()
        self.leaderboard_file = 'leaderboard.json'
        self.user_name = "Anonymous"
        self.root.geometry("800x600")
        self.root.bind("<Configure>", self.on_resize)
        self.show_name_entry_screen()
        self.quiz_ended = False


    def load_quotes(self):
        quotes = []
        with open('pride_quotes.csv', newline='', encoding='ISO-8859-1') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                quotes.append(row)
        return quotes

    def add_pride_background(self):
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.draw_pride_background()
        self.white_frame = tk.Frame(self.canvas, bg="white", bd=2, relief="ridge")
        self.white_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8)

    def draw_pride_background(self):
        self.canvas.delete("all")
        pride_colors = ["#e40303", "#ff8c00", "#ffed00", "#008026", "#004dff", "#750787"]
        height = self.root.winfo_height()
        width = self.root.winfo_width()
        stripe_height = height // len(pride_colors)
        for i, color in enumerate(pride_colors):
            self.canvas.create_rectangle(
                0, i * stripe_height, width, (i + 1) * stripe_height,
                fill=color, outline=""
            )

    def on_resize(self, event):
        if hasattr(self, 'canvas'):
            self.draw_pride_background()

    def show_name_entry_screen(self):
        self.clear_screen()
        self.add_pride_background()
        self.name_label = tk.Label(self.white_frame, text="Pride Month Turing Test!\nPlease enter your name:", font=("Jua", 30, "bold"), bg="white")
        self.name_entry = tk.Entry(self.white_frame, font=("Jua", 30))
        self.submit_button = tk.Button(
            self.white_frame,
            text="Start Quiz",
            command=self.start_quiz,
            font=("Jua", 24, "bold"),
            bg="#4CAF50",             # Green background
            fg="white",
            activebackground="#388E3C",
            activeforeground="white",
            disabledforeground="white",
            relief="flat",
            bd=0
        )

        self.name_label.pack(pady=10)
        self.name_entry.pack(pady=10)
        self.submit_button.pack(pady=10)

    def start_quiz(self):
        if hasattr(self, 'name_entry') and self.name_entry.winfo_exists():
            name = self.name_entry.get()
            self.user_name = name if name else "Anonymous"
            self.quiz_ended = False
            self.clear_screen()
            self.add_pride_background()
            self.score = 0
            self.question_count = 0
            self.total_time = 0
            self.start_time = time.time()
            self.quiz_start_time = self.start_time
            self.session_quotes = random.sample(self.quotes, self.max_questions)

            # Scrollable content area
            content_canvas = tk.Canvas(self.white_frame, bg="white", highlightthickness=0)
            scrollbar = tk.Scrollbar(self.white_frame, orient="vertical", command=content_canvas.yview)
            scrollable_frame = tk.Frame(content_canvas, bg="white")

            scrollable_frame.bind(
                "<Configure>",
                lambda e: content_canvas.configure(scrollregion=content_canvas.bbox("all"))
            )

            content_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            content_canvas.configure(yscrollcommand=scrollbar.set)

            content_canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # Labels inside scrollable area
            self.question_counter_label = tk.Label(scrollable_frame, text=f"Question: 0/{self.max_questions}", font=("Jua", 20, "bold"), bg="white")
            self.quote_label = tk.Label(scrollable_frame, text="", wraplength=500, justify="center", font=("Jua", 28), bg="white")
            self.fact_label = tk.Label(scrollable_frame, text="", wraplength=500, justify="center", font=("Jua", 20), bg="white")
            self.points_awarded_label = tk.Label(scrollable_frame, text="", font=("Jua", 20), bg="white")
            self.score_label = tk.Label(scrollable_frame, text="Score: 0", font=("Jua", 24, "bold"), bg="white")
            self.timer_label = tk.Label(scrollable_frame, text="Time: 0.00s", font=("Jua", 20), bg="white")

            self.question_counter_label.pack(pady=10)
            self.quote_label.pack(pady=10)
            self.fact_label.pack(pady=10)
            self.points_awarded_label.pack(pady=10)
            self.score_label.pack(pady=10)
            self.timer_label.pack(pady=10)

            # Fixed button frame at the bottom
            self.button_frame = tk.Frame(self.white_frame, bg="white")
            self.button_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=20, pady=20)

            self.human_button = tk.Button(
                self.button_frame,
                text="Human",
                command=lambda: self.check_answer('real'),
                font=("Jua", 24, "bold"),
                bg="#ff6666",
                fg="white",
                relief="flat",
                bd=0
            )
            self.human_button.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(0, 10))

            self.ai_button = tk.Button(
                self.button_frame,
                text="AI",
                command=lambda: self.check_answer('ai'),
                font=("Jua", 24, "bold"),
                bg="#66b3ff",
                fg="white",
                relief="flat",
                bd=0
            )
            self.ai_button.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=(10, 0))

            self.update_timer()
            self.show_next_quote()


    def show_next_quote(self):
        self.points_awarded_label.config(text="")
        if self.question_count >= self.max_questions:
            self.end_quiz()
            return
        self.current_quote = self.session_quotes[self.question_count]
        self.quote_label.config(text=self.current_quote['quote'])
        self.fact_label.config(text=f"{self.current_quote['source']}\n \n {self.current_quote['fact']}")
        self.start_time = time.time()
        self.question_count += 1
        self.question_counter_label.config(text=f"Question: {self.question_count}/{self.max_questions}")
        self.human_button.config(state=tk.NORMAL)
        self.ai_button.config(state=tk.NORMAL)

    def check_answer(self, answer):
        time_taken = time.time() - self.start_time
        self.total_time += time_taken
        correct = answer == self.current_quote['type']
        points_awarded = self.calculate_score(correct, time_taken)
        self.score += points_awarded
        self.points_awarded_label.config(text=f"+{points_awarded}")
        correct_answer = "Human" if self.current_quote['type'] == 'real' else "AI"
        result_text = f"Correct Answer: {correct_answer}\n {self.current_quote['source']}\n \n{self.current_quote['fact']}"
        self.fact_label.config(text=result_text)
        self.score_label.config(text=f"Score: {self.score}")
        self.human_button.config(state=tk.DISABLED)
        self.ai_button.config(state=tk.DISABLED)
        if self.question_count >= self.max_questions:
            self.total_time = time.time() - self.quiz_start_time  # Finalize time immediately
            self.quiz_ended = True
            self.root.after(3000, self.end_quiz)  # Skip show_next_quote
        else:
            self.root.after(3000, self.show_next_quote)
        if self.question_count >= self.max_questions:
            self.quiz_ended = True
            self.total_time = time.time() - self.quiz_start_time


    def calculate_score(self, correct, time_taken):
        return max(200 - int(time_taken * 8), 75) if correct else 0

    def end_quiz(self):
        #self.total_time = time.time() - self.quiz_start_time
        self.save_score()
        self.show_game_over_screen()

    def save_score(self):
        leaderboard = self.load_leaderboard()
        existing_entry = next((entry for entry in leaderboard if entry['name'] == self.user_name), None)
        if existing_entry:
            existing_entry['score'] = max(existing_entry['score'], self.score)
            existing_entry['time'] = round(self.total_time, 2)
        else:
            leaderboard.append({
                "name": self.user_name,
                "score": self.score,
                "time": round(self.total_time, 2)
            })
        leaderboard.sort(key=lambda x: x['score'], reverse=True)
        with open(self.leaderboard_file, 'w') as f:
            json.dump(leaderboard, f, indent=4)

    def load_leaderboard(self):
        try:
            with open(self.leaderboard_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def show_game_over_screen(self):
        self.clear_screen()
        self.add_pride_background()

        game_over_label = tk.Label(
            self.white_frame,
            text=f"Game Over! Your final score is {self.score}.",
            wraplength=400,
            justify="center",
            font=("Jua", 40),
            bg="white"
        )
        game_over_label.pack(pady=10)

        # Scrollable frame setup
        canvas = tk.Canvas(self.white_frame, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(self.white_frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="white")

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=20)
        scrollbar.pack(side="right", fill="y")

        # Load and display top 10 leaderboard entries
        leaderboard = self.load_leaderboard()[:10]
        leaderboard_text = "Leaderboard:\n" + "\n".join(
            f"{entry['name']}: {entry['score']} ({entry.get('time', 0):.2f}s)"
            for entry in leaderboard
        )
        leaderboard_label = tk.Label(
            scroll_frame,
            text=leaderboard_text,
            wraplength=400,
            justify="center",
            font=("Jua", 28),
            bg="white"
        )
        leaderboard_label.pack(pady=10)

        # Buttons
        # retry_button = tk.Button(
          #  self.white_frame,
           # text=f"Play again as {self.user_name}",
            #command=self.start_quiz,
            #font=("Jua", 34, "bold")
       # )
        new_player_button = tk.Button(
            self.white_frame,
            text="New Player",
            command=self.show_name_entry_screen,
            font=("Jua", 34, "bold")
        )
       # retry_button.pack(pady=10)
        new_player_button.pack(pady=10)
    

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def update_timer(self):
        if not self.quiz_ended:
            elapsed = time.time() - self.quiz_start_time
            self.timer_label.config(text=f"{elapsed:.2f}s") #Put time here if you want it to say Time: before the time
            self.root.after(100, self.update_timer)
        else:
            self.timer_label.config(text=f"{self.total_time:.2f}s") #and here as well


           

    def on_resize(self, event):
        if hasattr(self, '_resize_after_id'):
            self.root.after_cancel(self._resize_after_id)
        self._resize_after_id = self.root.after(200, self._apply_resize)

    def _apply_resize(self):
        self.draw_pride_background()

if __name__ == "__main__":
    root = tk.Tk()
    app = PrideQuizApp(root)
    root.mainloop()

