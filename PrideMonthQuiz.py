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
        self.user_name = "Anonymous"  # Default to avoid missing attribute
        self.show_name_entry_screen()

    def load_quotes(self):
        quotes = []
        with open('pride_quotes.csv', newline='', encoding='ISO-8859-1') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                quotes.append(row)
        return quotes

    def show_name_entry_screen(self):
        self.clear_screen()
        self.name_label = tk.Label(self.root, text="Please enter your name:")
        self.name_label.pack(pady=20)
        self.name_entry = tk.Entry(self.root)
        self.name_entry.pack(pady=10)
        self.submit_button = tk.Button(self.root, text="Start Quiz", command=self.start_quiz)
        self.submit_button.pack(pady=10)

    def start_quiz(self):
        if hasattr(self, 'name_entry') and self.name_entry.winfo_exists():
            name = self.name_entry.get()
            self.user_name = name if name else "Anonymous"
        self.clear_screen()
        self.score = 0
        self.question_count = 0
        self.total_time = 0
        self.start_time = time.time()
        self.quiz_start_time = self.start_time
        self.session_quotes = random.sample(self.quotes, self.max_questions)

        self.question_counter_label = tk.Label(self.root, text=f"Question: 0/{self.max_questions}")
        self.question_counter_label.pack(pady=10)
        self.quote_label = tk.Label(self.root, text="", wraplength=400, justify="center")
        self.quote_label.pack(pady=20)
        self.fact_label = tk.Label(self.root, text="", wraplength=400, justify="center")
        self.fact_label.pack(pady=20)
        score_frame = tk.Frame(self.root)
        score_frame.pack(pady=20)
        self.points_awarded_label = tk.Label(score_frame, text="", font=("Courier", 12))
        self.points_awarded_label.pack()
        self.score_label = tk.Label(score_frame, text="Score: 0", font=("Courier", 14, "bold"))
        self.score_label.pack()
        self.timer_label = tk.Label(self.root, text="Time: 0.00s", font=("Courier", 12))
        self.timer_label.pack(pady=10)
        self.update_timer()
        self.human_button = tk.Button(self.root, text="Human", command=lambda: self.check_answer('real'))
        self.human_button.pack(side="left", padx=20)
        self.ai_button = tk.Button(self.root, text="AI", command=lambda: self.check_answer('ai'))
        self.ai_button.pack(side="right", padx=20)
        self.show_next_quote()

    def show_next_quote(self):
        self.points_awarded_label.config(text="")
        if self.question_count >= self.max_questions:
            self.end_quiz()
            return
        self.current_quote = self.session_quotes[self.question_count]
        self.quote_label.config(text=self.current_quote['quote'])
        self.fact_label.config(text=f"Source: {self.current_quote['source']}\nFact: {self.current_quote['fact']}")
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
        result_text = f"Correct Answer: {correct_answer}\nSource: {self.current_quote['source']}\nFact: {self.current_quote['fact']}"
        self.fact_label.config(text=result_text)
        self.score_label.config(text=f"Score: {self.score}")
        self.human_button.config(state=tk.DISABLED)
        self.ai_button.config(state=tk.DISABLED)
        self.root.after(3000, self.show_next_quote)

    def calculate_score(self, correct, time_taken):
        return max(200 - int(time_taken * 8), 10) if correct else 0

    def end_quiz(self):
        self.total_time = time.time() - self.quiz_start_time
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
        game_over_label = tk.Label(
            self.root,
            text=f"Game Over! Your final score is {self.score}.",
            wraplength=400,
            justify="center"
        )
        game_over_label.pack(pady=20)
        leaderboard = self.load_leaderboard()
        leaderboard_text = "Leaderboard:\n" + "\n".join(
            f"{entry['name']}: {entry['score']} ({entry.get('time', 0):.2f}s)" for entry in leaderboard
        )
        leaderboard_label = tk.Label(self.root, text=leaderboard_text, wraplength=400, justify="center")
        leaderboard_label.pack(pady=20)
        retry_button = tk.Button(self.root, text=f"Play again as {self.user_name}", command=self.start_quiz)
        retry_button.pack(pady=10)
        new_player_button = tk.Button(self.root, text="New Player", command=self.show_name_entry_screen)
        new_player_button.pack(pady=10)

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def update_timer(self):
        if self.question_count < self.max_questions:
            elapsed = time.time() - self.quiz_start_time
            self.timer_label.config(text=f"Time: {elapsed:.2f}s")
            self.root.after(100, self.update_timer)

if __name__ == "__main__":
    root = tk.Tk()
    app = PrideQuizApp(root)
    root.mainloop()
