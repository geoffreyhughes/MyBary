
'''

   Geoffrey Hughes
   002306123
   ghughes@chapman.edu
   Prof. Rene German
   CPSC 408 - Database Management
   Spring 2019
   Final Project: MyBary

'''


from flask import Flask, render_template, request, make_response, redirect
import datetime
import pyexcel as pe
import StringIO
from flask import make_response
import mysql.connector
from mysql.connector import errorcode


app = Flask(__name__)

print("hi")

curr_user = "curr_user_global"


TABLES = {}

TABLES['Users'] = ("CREATE TABLE IF NOT EXISTS Users ("
                   "UserID int NOT NULL AUTO_INCREMENT, "
                   "Username varchar(30) NOT NULL, "
                   "Password varchar(30) NOT NULL, "
                   "PRIMARY KEY (UserID))")

TABLES['UsersBooks'] = ("CREATE TABLE IF NOT EXISTS UsersBooks ("
                        "UsersBooksID int NOT NULL AUTO_INCREMENT, "
                        "UserID int NOT NULL, "
                        "BookID int NOT NULL, "
                        "PRIMARY KEY (UsersBooksID), "
                        "FOREIGN KEY (UserID) REFERENCES Users(UserID), "
                        "FOREIGN KEY (BookID) REFERENCES Books(BookID))")

TABLES['Books'] = ("CREATE TABLE IF NOT EXISTS Books ("
                   "BookID int NOT NULL AUTO_INCREMENT, "
                   "AuthorID int NOT NULL, "
                   "GenreID int NOT NULL, "
                   "PublisherID int NOT NULL, "
                   "Title varchar(45) NOT NULL, "
                   "ReadingStatus varchar(10) NOT NULL, "
                   "PRIMARY KEY (BookID), "
                   "FOREIGN KEY (AuthorID) REFERENCES Authors(AuthorID), "
                   "FOREIGN KEY (GenreID) REFERENCES Genres(GenreID), "
                   "FOREIGN KEY (PublisherID) REFERENCES Publishers(PublisherID))")

TABLES['Authors'] = ("CREATE TABLE IF NOT EXISTS Authors ("
                     "AuthorID int NOT NULL AUTO_INCREMENT, "
                     "FirstName varchar(30) NOT NULL, "
                     "LastName varchar(30) NOT NULL, "
                     "PRIMARY KEY (AuthorID))")

TABLES['Publishers'] = ("CREATE TABLE IF NOT EXISTS Publishers ("
                        "PublisherID int NOT NULL AUTO_INCREMENT, "
                        "Publisher varchar(30) NOT NULL, "
                        "DateEstablished int, "
                        "PRIMARY KEY (PublisherID))")

TABLES['Genres'] = ("CREATE TABLE IF NOT EXISTS Genres ("
                    "GenreID int NOT NULL AUTO_INCREMENT, "
                    "Genre varchar(15) NOT NULL, "
                    "PRIMARY KEY (GenreID))")


# conn = mysql.connector.connect(user='user', password='chapman', host='35.203.181.112:3306')
# cursor = conn.cursor()
# cursor.execute("CREATE TABLE 'test1' (user int)")
# conn.close()

try:

    print("1")

    # This is the failed connection to the google cloud MySQL server, not sure what's wrong:
    # cnx = mysql.connector.connect(host="35.203.181.112:3306", user="user", password="chapman", database="assignment3")

    cnx = mysql.connector.connect(host="localhost", user="root", password="mysqlshadow", database="Final")
    cursor = cnx.cursor()

    for table_name in TABLES:
        cursor.execute(TABLES[table_name])

    cnx.commit()
    print("2")

except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)
else:
  cnx.close()


print("bye")


@app.route('/', methods=['GET', 'POST'])
def welcome():
    print("in welcome")
    if request.method == 'POST':
        print(request.form)
        userDetails = request.form
        username = userDetails['username']
        password = userDetails['password']
        global curr_user
        curr_user = username
        print(curr_user)
        print(userDetails)
        cnx = mysql.connector.connect(host="localhost", user="root", password="mysqlshadow", database="Final")
        cursor = cnx.cursor()
        cursor.execute("INSERT INTO Users(Username, Password) VALUES (%s, %s)", (username, password))
        cnx.commit()
        return redirect('/Users')

    return render_template('index.html')


@app.route('/Users', methods=['GET', 'POST'])
def Users():
    print("in users")
    if request.method == 'POST' and request.form['submit_button'] == 'Books':
        return redirect('/Books')

    cnx = mysql.connector.connect(host="localhost", user="root", password="mysqlshadow", database="Final")
    cursor = cnx.cursor(buffered=True)
    cursor.execute("SELECT * FROM Users")

    userDetails = cursor.fetchall()
    return render_template('Users.html', userDetails=userDetails)


@app.route('/Books', methods=['GET', 'POST'])
def Books():
    print("in books")

    if request.method == 'POST':
        if request.form['submit_button'] == 'Add Book':
            return redirect('/Books_Add_Book')

        elif request.form['submit_button'] == 'Delete Book':
            return redirect('/Books_Delete_Book')
        
        elif request.form['submit_button'] == 'Edit Book':
            return redirect('/Books_Edit_Book')

        elif request.form['submit_button'] == 'Query Book':
            return redirect('/Books_Query_Book')

        elif request.form['submit_button'] == 'Download As CSV':
            return redirect('/download')
                
    cnx = mysql.connector.connect(host="localhost", user="root", password="mysqlshadow", database="Final")
    cursor = cnx.cursor(buffered=True)

    cursor.execute("SELECT BookID, FirstName, LastName, Genre, Publisher, Title, ReadingStatus "
                                    "FROM Books "
                                    "INNER JOIN Authors A on Books.AuthorID = A.AuthorID "
                                    "INNER JOIN Genres G on Books.GenreID = G.GenreID "
                                    "INNER JOIN Publishers P on Books.PublisherID = P.PublisherID ")
   
    userDetails = cursor.fetchall()
    return render_template('Books.html', userDetails=userDetails)


@app.route('/Books_Add_Book', methods=['GET', 'POST'])
def Books_Add_Book():
    print("in Books_Add_Book")
    global curr_user
    print(curr_user)

    if request.method == 'POST':
        if request.form['submit_button'] == 'View Books':
            return redirect('/Books')
        
        print(request.form)
        userDetails = request.form
        author_firstName = userDetails['author_firstName']
        author_lastName = userDetails['author_lastName']
        genre = userDetails['genre']
        publisher = userDetails['publisher']
        title = userDetails['title']
        readingStatus = userDetails['readingStatus']
        print(userDetails)
        cnx = mysql.connector.connect(host="localhost", user="root", password="mysqlshadow", database="Final")
        cursor = cnx.cursor(buffered=True)

        cursor.execute("INSERT INTO Authors (FirstName, LastName)"
                       "SELECT %s, %s FROM Authors "
                       "WHERE NOT EXISTS (SELECT * "
                       "FROM Authors WHERE FirstName = %s AND LastName = %s"
                       ") LIMIT 1", (author_firstName, author_lastName, author_firstName, author_firstName))
        cnx.commit()


        # GET AUTHOR ID to create new Book
        cursor.execute("SELECT * FROM Authors")
        authors = cursor.fetchall()
        author_id = 0;
        print authors

        for i in authors:
            if i[1] == author_firstName and i[2] == author_lastName:
                author_id = i[0]
                break

        print "New AuthorID = "
        print author_id


        # GET GENRE ID to create new Book
        cursor.execute("SELECT * FROM Genres")
        genres = cursor.fetchall()
        genre_id = 0
        print genres

        for i in genres:
            print i[0], i[1]
            if i[1] == genre:
                genre_id = i[0]
                break

        print "New GenreID = "
        print genre_id


        # GET PUBLISHER ID to create new Book
        cursor.execute("SELECT * FROM Publishers")
        publishers = cursor.fetchall()
        publisher_id = 0
        print publishers

        for i in publishers:
            print i[0], i[1], i[2]
            if i[1] == publisher:
                publisher_id = i[0]
                break

        print "New PublisherID = "
        print publisher_id


        # GET TITLE to create new Book
        new_title = title
        print(new_title)


        # GET READING STATUS to create new Book
        new_readingStatus = readingStatus
        print(new_readingStatus)


        cursor.execute("INSERT INTO Books (AuthorID, GenreID, PublisherID, Title, ReadingStatus) "
                       "VALUES (%s, %s, %s, %s, %s)", (author_id, genre_id, publisher_id, new_title, new_readingStatus))

        cnx.commit()


    cnx = mysql.connector.connect(host="localhost", user="root", password="mysqlshadow", database="Final")
    cursor = cnx.cursor(buffered=True)
    cursor.execute("SELECT BookID, FirstName, LastName, Genre, Publisher, Title, ReadingStatus "
                                "FROM Books "
                                "INNER JOIN Authors A on Books.AuthorID = A.AuthorID "
                                "INNER JOIN Genres G on Books.GenreID = G.GenreID "
                                "INNER JOIN Publishers P on Books.PublisherID = P.PublisherID ")


    userDetails = cursor.fetchall()
    return render_template('Books_Add_Book.html', userDetails=userDetails)
        


@app.route('/Books_Delete_Book', methods=['GET', 'POST'])
def Books_Delete_Book():
    print("in Books_Delete_Book")

    if request.method == 'POST':
        if request.form['submit_button'] == 'Delete Book':

            print(request.form)
            userDetails = request.form
            delete_book = userDetails['delete_book']
            cnx = mysql.connector.connect(host="localhost", user="root", password="mysqlshadow", database="Final")
            cursor = cnx.cursor(buffered=True)

            cursor.execute("SELECT * FROM Books")
            books = cursor.fetchall()
            delete_book_id = 0
            print delete_book

            for i in books:
                print i[0], i[1]
                if i[0] == int(delete_book):
                    delete_book_id = i[0]
                    delete_book_title = i[1]
                    print delete_book_id
                    print delete_book_title

                    cursor.execute("DELETE FROM Books WHERE BookID = %s AND AuthorID = %s", (delete_book_id, delete_book_title))
                    cnx.commit()
                    break

        elif request.form['submit_button'] == 'View Books':
            return redirect('/Books')

    cnx = mysql.connector.connect(host="localhost", user="root", password="mysqlshadow", database="Final")
    cursor = cnx.cursor(buffered=True)
    curr_users = cursor.execute("SELECT BookID, FirstName, LastName, Genre, Publisher, Title, ReadingStatus "
                                "FROM Books "
                                "INNER JOIN Authors A on Books.AuthorID = A.AuthorID "
                                "INNER JOIN Genres G on Books.GenreID = G.GenreID "
                                "INNER JOIN Publishers P on Books.PublisherID = P.PublisherID ")

    cnx.commit()

    userDetails = cursor.fetchall()
    return render_template('Books_Delete_Book.html', userDetails=userDetails)





@app.route('/Books_Edit_Book', methods=['GET', 'POST'])
def Books_Edit_Book():
    print("in Books_Delete_Book")

    cnx = mysql.connector.connect(host="localhost", user="root", password="mysqlshadow", database="Final")
    cursor = cnx.cursor(buffered=True)
    cursor.execute("SELECT BookID, FirstName, LastName, Genre, Publisher, Title, ReadingStatus "
                   "FROM Books "
                   "INNER JOIN Authors A on Books.AuthorID = A.AuthorID "
                   "INNER JOIN Genres G on Books.GenreID = G.GenreID "
                   "INNER JOIN Publishers P on Books.PublisherID = P.PublisherID ")
    userDetails = cursor.fetchall()

    if request.method == 'POST':
        userDetails = request.form
        edit_book_id = 0
        edit_book_id = userDetails['edit_book_id']

        if request.form['submit_button'] == 'Edit Genre' and edit_book_id > 0:

            edit_genre = userDetails['edit_genre']
            
            # GET GENRE ID to edit to
            cursor.execute("SELECT * FROM Genres")
            genres = cursor.fetchall()
            genre_id = 0

            for i in genres:
                if i[1] == edit_genre:
                    genre_id = i[0]
                    break
            
            print "New GenreID = "
            print genre_id

            cursor.execute("UPDATE Books "
                           "SET GenreID = %s "
                           "WHERE BookID = %s ", (genre_id, edit_book_id))
            cnx.commit()

        elif request.form['submit_button'] == 'Edit Publisher' and edit_book_id > 0:

            edit_publisher = userDetails['edit_publisher']

            # GET PUBLISHER ID to edit to
            cursor.execute("SELECT * FROM Publishers")
            publishers = cursor.fetchall()
            publisher_id = 0
            
            for i in publishers:
                if i[1] == edit_publisher:
                    publisher_id = i[0]
                    break
            
            print "New PublisherID = "
            print publisher_id
            
            cursor.execute("UPDATE Books "
                           "SET PublisherID = %s "
                           "WHERE BookID = %s ", (publisher_id, edit_book_id))
            cnx.commit()

        elif request.form['submit_button'] == 'Edit Title' and edit_book_id > 0:

            edit_title = userDetails['edit_title']

            cursor.execute("UPDATE Books "
                           "SET Title = %s "
                           "WHERE BookID = %s ", (edit_title, edit_book_id))
            cnx.commit()

        elif request.form['submit_button'] == 'Edit Reading Status' and edit_book_id > 0:

            edit_readingStatus = userDetails['edit_readingStatus']
            
            cursor.execute("UPDATE Books "    
                           "SET ReadingStatus = %s "    
                           "WHERE BookID = %s ", (edit_readingStatus, edit_book_id))
            cnx.commit()

        elif request.form['submit_button'] == 'View Books':
            return redirect('/Books')
        

    cursor.execute("SELECT BookID, FirstName, LastName, Genre, Publisher, Title, ReadingStatus "
                   "FROM Books "
                   "INNER JOIN Authors A on Books.AuthorID = A.AuthorID "
                   "INNER JOIN Genres G on Books.GenreID = G.GenreID "
                   "INNER JOIN Publishers P on Books.PublisherID = P.PublisherID ")
    userDetails = cursor.fetchall()

    return render_template('Books_Edit_Book.html', userDetails=userDetails)




@app.route('/Books_Query_Book', methods=['GET', 'POST'])
def Books_Query_Book():

    cnx = mysql.connector.connect(host="localhost", user="root", password="mysqlshadow", database="Final")
    cursor = cnx.cursor(buffered=True)
    cursor.execute("SELECT BookID, FirstName, LastName, Genre, Publisher, Title, ReadingStatus "
                                        "FROM Books "
                                        "INNER JOIN Authors A on Books.AuthorID = A.AuthorID "
                                        "INNER JOIN Genres G on Books.GenreID = G.GenreID "
                                        "INNER JOIN Publishers P on Books.PublisherID = P.PublisherID ")
    userDetails = cursor.fetchall()
    queryDetails = cursor.fetchall()


    if request.method == 'POST':

        userDetails = request.form

        query_lastName = userDetails['query_lastName']
        query_genre = userDetails['query_genre']
        query_readingStatus = userDetails['query_readingStatus']
        query_genre_in_unread = userDetails['query_genre_in_unread']

        cnx = mysql.connector.connect(host="localhost", user="root", password="mysqlshadow", database="Final")
        cursor = cnx.cursor(buffered=True)        


        if request.form['submit_button'] == 'Query by Author Last Name':
            cursor.execute("SELECT BookID, FirstName, LastName, Genre, Publisher, Title, ReadingStatus "
                           "FROM Books "
                           "INNER JOIN Authors A on Books.AuthorID = A.AuthorID "
                           "INNER JOIN Genres G on Books.GenreID = G.GenreID "
                           "INNER JOIN Publishers P on Books.PublisherID = P.PublisherID "
                           "WHERE LastName = %s ", (query_lastName,))
            userDetails = cursor.fetchall()


        elif request.form['submit_button'] == 'Query by Genre':
            print query_genre
            cursor.execute("SELECT BookID, FirstName, LastName, Genre, Publisher, Title, ReadingStatus "
                           "FROM Books "
                           "INNER JOIN Authors A on Books.AuthorID = A.AuthorID "
                           "INNER JOIN Genres G on Books.GenreID = G.GenreID "
                           "INNER JOIN Publishers P on Books.PublisherID = P.PublisherID "
                           "WHERE Genre = %s ", (query_genre,))
            userDetails = cursor.fetchall()


        elif request.form['submit_button'] == 'Query by Reading Status':
            cursor.execute("SELECT BookID, FirstName, LastName, Genre, Publisher, Title, ReadingStatus "
                           "FROM Books "
                           "INNER JOIN Authors A on Books.AuthorID = A.AuthorID "
                           "INNER JOIN Genres G on Books.GenreID = G.GenreID "
                           "INNER JOIN Publishers P on Books.PublisherID = P.PublisherID "
                           "WHERE ReadingStatus = %s ", (query_readingStatus,))
            userDetails = cursor.fetchall()

            cursor.execute("SELECT ReadingStatus, COUNT(BookID) "
                           "FROM Books "                           
                           "GROUP BY ReadingStatus ")
            queryDetails = cursor.fetchall()


        elif request.form['submit_button'] == 'Query Unread Books by Genre':
            cursor.execute("SELECT BookID, FirstName, LastName, Genre, Publisher, Title, ReadingStatus "
                           "FROM Books "
                           "INNER JOIN Authors A on Books.AuthorID = A.AuthorID "
                           "INNER JOIN Genres G on Books.GenreID = G.GenreID "
                           "INNER JOIN Publishers P on Books.PublisherID = P.PublisherID "
                           "WHERE ReadingStatus = %s AND Genre IN "
                               "(SELECT Genre FROM Genres WHERE Genre = %s)", ("Unread", query_genre_in_unread))
            userDetails = cursor.fetchall()


        elif request.form['submit_button'] == 'View Books':
            return redirect('/Books')

    cnx.commit()

    return render_template('Books_Query_Book.html', userDetails=userDetails, queryDetails=queryDetails)



@app.route('/download')
def download():

    cnx = mysql.connector.connect(host="localhost", user="root", password="mysqlshadow", database="Final")
    cursor = cnx.cursor(buffered=True)
    cursor.execute("SELECT BookID, FirstName, LastName, Genre, Publisher, Title, ReadingStatus "
                   "FROM Books "
                   "INNER JOIN Authors A on Books.AuthorID = A.AuthorID "
                   "INNER JOIN Genres G on Books.GenreID = G.GenreID "
                   "INNER JOIN Publishers P on Books.PublisherID = P.PublisherID ")

    books = cursor.fetchall()

    sheet = pe.Sheet(books)
    io = StringIO.StringIO()
    sheet.save_to_memory("csv", io)
    output = make_response(io.getvalue())


    curr_time = datetime.datetime.now().strftime("%I:%M%p_%B_%d_%Y")
    download_name = "MyBary_" + curr_time + ".csv"
    print download_name

    output.headers["Content-Disposition"] = "attachment; filename=%s" % (download_name)
    output.headers["Content-type"] = "text/csv"
    return output



