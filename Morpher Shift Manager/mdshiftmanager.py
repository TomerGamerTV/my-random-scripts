import datetime
import os
import time
import json
import threading


class Roleplayer:
    def __init__(self):
        self.options = {
            1: {"name": "Users Morphed", "points": 0},
            2: {"name": "Remorphed", "points": 0},
            3: {"name": "Unmorphed", "points": 0},
            4: {"name": "Startergear", "points": 0},
            5: {"name": "Tech Support Given", "points": 0}  # New category
        }
        self.error_message = ""
        self.temp_file = "temp_morphlog.txt"
        self.version = "1.0.3"  # Updated version
        self.last_checked = datetime.datetime.now()
        self.load_temp_file()

    def load_temp_file(self):
        if os.path.exists(self.temp_file):
            with open(self.temp_file, "r") as file:
                self.options = json.load(file)
            # Convert keys back to integers
            self.options = {int(k): v for k, v in self.options.items()}

    def save_temp_file(self):
        with open(self.temp_file, "w") as file:
            json.dump(self.options, file)

    def select_option(self, option):
        if option in self.options:
            self.options[option]["points"] += 1
            self.error_message = ""
            self.save_temp_file()
        else:
            self.error_message = "Invalid option. Please enter a valid option."

    def remove_points(self, option, points):
        if option in self.options:
            if self.options[option]["points"] >= points and points > 0:
                self.options[option]["points"] -= points
                self.error_message = ""
                self.save_temp_file()
            else:
                self.error_message = "Invalid number of points. Please enter a number greater than 0 and less than or equal to the current points."
        else:
            self.error_message = "Invalid option. Please enter a valid option."

    def finish_deployment(self, start_time):
        print("Are you sure you want to finish your shift? Press 'Y' to confirm or 'N' to return back.")
        confirm = input().lower()
        if confirm == 'y':
            total_points = sum([self.options[option]["points"]
                               for option in self.options])
            print(f"Deployment finished. Total points: {total_points}")
            for option in self.options:
                print(
                    f"{self.options[option]['name']}: {self.options[option]['points']} points")
            elapsed_time = time.time() - start_time

            # Create the "logs" directory if it doesn't exist
            if not os.path.exists("logs"):
                os.makedirs("logs")

            with open(f"logs/morphlog_{datetime.datetime.now().strftime('%Y%m%d')}.txt", "w") as file:
                file.write(f"Total points: {total_points}\n")
                for option in self.options:
                    file.write(
                        f"{self.options[option]['name']}: {self.options[option]['points']} points\n")
                file.write(
                    f"Time elapsed: {time.strftime('%H:%M:%S', time.gmtime(elapsed_time))}\n")
            os.remove(self.temp_file)
            return True
        elif confirm == 'n':
            self.error_message = ""  # Reset the error message
            return False
        else:
            self.error_message = "Invalid input. Please enter a valid option."
            return False


def main():
    start_time = time.time()
    roleplayer = Roleplayer()
    print("Tool created by TomerGamerTV, Do not steal.")
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Tool created by TomerGamerTV, Do not steal.")
        print(
            f"Current time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\nOptions:")
        for option in roleplayer.options:
            print(
                f"{option}: {roleplayer.options[option]['name']} [x{roleplayer.options[option]['points']}]")
        if roleplayer.error_message:
            print(f"Latest Error: {roleplayer.error_message}")
        user_input = input(
            "Select an option or type 'F' to finish deployment or 'R' to remove points or 'K' to exit the program: ")
        if user_input.lower() == 'f':
            if roleplayer.finish_deployment(start_time):
                elapsed_time = time.time() - start_time
                print(
                    f"Time elapsed: {time.strftime('%H:%M:%S', time.gmtime(elapsed_time))}")
                break
        elif user_input.lower() == 'r':
            try:
                option = int(
                    input("Choose which category you want to remove points from: "))
                points = int(input("How many points do you want to remove? "))
                roleplayer.remove_points(option, points)
            except ValueError:
                roleplayer.error_message = "Invalid input. Please enter a valid option."
        elif user_input.lower() == 'k':
            print("Exiting the program...")
            break
        elif user_input.lower() == 'i':
            print(f"Version: {roleplayer.version}")
            time.sleep(10)
        else:
            try:
                roleplayer.select_option(int(user_input))
            except ValueError:
                roleplayer.error_message = "Invalid input. Please enter a valid option."


if __name__ == "__main__":
    main()
