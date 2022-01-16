import sqlite3
from datetime import datetime


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def add_user(self, user_id):
        with self.connection:
            return self.cursor.execute("INSERT INTO `users` (`user_id`) VALUES (?)", (user_id,))

    def add_played_time(self, user_id):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `played_time` = ? WHERE `user_id` = ?",
                                       ((datetime.now() - datetime.strptime('2022-01-09', '%Y-%m-%d')).days, user_id,))

    def add_winning(self, user_id):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `wins` = wins + ? WHERE `user_id` = ?", (1, user_id,))

    def add_losing(self, user_id):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `losses` = losses + ? WHERE `user_id` = ?", (1, user_id,))

    def add_current_streak(self, user_id, streak):
        with self.connection:
            if streak:
                return self.cursor.execute(
                    "UPDATE `users` SET `current_streak` = current_streak + ? WHERE `user_id` = ?", (1, user_id,))
            else:
                return self.cursor.execute(
                    "UPDATE `users` SET `current_streak` = ? WHERE `user_id` = ?", (0, user_id,))

    def add_max_streak(self, user_id):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `max_streak` = `current_streak` WHERE `user_id` = ?", (user_id,))

    def add_word(self, word):
        with self.connection:
            return self.cursor.execute("UPDATE `wordle` SET `word` = ?",(word,))

    def add_winning_plus(self, user_id):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `wins_plus` = wins_plus + ? WHERE `user_id` = ?", (1, user_id,))

    def add_losing_plus(self, user_id):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `losses_plus` = losses_plus + ? WHERE `user_id` = ?", (1, user_id,))

    def add_current_streak_plus(self, user_id, streak):
        with self.connection:
            if streak:
                return self.cursor.execute(
                    "UPDATE `users` SET `current_streak_plus` = current_streak_plus + ? WHERE `user_id` = ?", (1, user_id,))
            else:
                return self.cursor.execute(
                    "UPDATE `users` SET `current_streak_plus` = ? WHERE `user_id` = ?", (0, user_id,))

    def add_max_streak_plus(self, user_id):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `max_streak_plus` = `current_streak_plus` "
                                       "WHERE `user_id` = ?", (user_id,))

    def add_word_plus(self, user_id, word):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `user_word` = ? WHERE `user_id` = ?", (word, user_id, ))

    def user_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()
            return bool(len(result))

    def get_users(self):
        with self.connection:
            result = self.cursor.execute("SELECT user_id FROM users").fetchall()
            return result

    def get_winning(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT `wins` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()
            for row in result:
                user_num = row[0]
            return user_num

    def get_played_time(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT `played_time` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()
            for row in result:
                user_num = row[0]
            return user_num

    def get_losing(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT `losses` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()
            for row in result:
                user_num = row[0]
            return user_num

    def get_current_streak(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT `current_streak` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()
            for row in result:
                user_num = row[0]
            return user_num

    def get_max_streak(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT `max_streak` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()
            for row in result:
                user_num = row[0]
            return user_num

    def get_word(self):
        with self.connection:
            result = self.cursor.execute("SELECT `word` FROM `wordle`").fetchall()
            for row in result:
                user_num = row[0]
            return user_num

    def get_winning_plus(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT `wins_plus` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()
            for row in result:
                user_num = row[0]
            return user_num

    def get_losing_plus(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT `losses_plus` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()
            for row in result:
                user_num = row[0]
            return user_num

    def get_current_streak_plus(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT `current_streak_plus` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()
            for row in result:
                user_num = row[0]
            return user_num

    def get_max_streak_plus(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT `max_streak_plus` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()
            for row in result:
                user_num = row[0]
            return user_num

    def get_word_plus(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT `user_word` FROM `users` WHERE `user_id` = ?",
                                         (user_id,)).fetchall()
            for row in result:
                user_num = row[0]
            return user_num

    def get_count_users(self):
        with self.connection:
            result = self.cursor.execute("SELECT COUNT(*) from 'users'").fetchall()
            return result[0][0]
