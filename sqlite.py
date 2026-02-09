import sqlite3

connection = sqlite3.connect("student.db")

cursor = connection.cursor()

table_info = """
create table STUDENT(
NAME VARCHAR(25),
CLASS VARCHAR(25),
SECTION VARCHAR(25),
MARKS INT
)
"""


cursor.execute(table_info)
cursor.execute("INSERT INTO STUDENT VALUES ('Krish','Data science','A',90)")
cursor.execute("INSERT INTO STUDENT VALUES ('John','Data science','B',100)")
cursor.execute("INSERT INTO STUDENT VALUES ('Mukesh','Data science','A',86)")
cursor.execute("INSERT INTO STUDENT VALUES ('Jacob','Devops','A',50)")
cursor.execute("INSERT INTO STUDENT VALUES ('Dipesh','Devops','A',35)")


print("the inserted records are:")
data = cursor.execute(" SELECT * FROM STUDENT")
for row in data:
    print(row)


connection.commit()
connection.close()

