-- name,age,screentime,gender,music,pet,food,season,holiday

CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  age INTEGER,
  screentime NUMBER,
  gender TEXT,
  music TEXT,
  pet TEXT,
  food TEXT,
  season TEXT,
  holiday TEXT
);
