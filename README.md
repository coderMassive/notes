# Notes
#### [Video Demo](https://youtu.be/Wn-I-0-JoUI)
## Login and Register
If you are not logged in, you will be sent to the login page. You can register with the button in the top right corner. An error will occur if you log in with the wrong username or password, register with a username that already exists, or fail to input one of the fields.
## Home Page
Once you log in, there will be a list of notes on the left in order of last updated (most recently updated at the top). Above the sidebar is the search bar, and below it is the add field and button. When you click on a note, two fields on the right will appear, the top, short text field is the title (seen on the sidebar when selecting notes), and the bottom, long text area is the body. Below that are the share (and username field for it), save, and delete buttons. Each of these functions are described below.
## Adding
To add a note, type in the name of it into the field and press the add button. This will add it to your list of notes and open it up for you to edit.
## Editing
You can type in the title and body fields to change them and click the save button to save your changes. Pressing enter on the title also works to save the note.
## Deleting
The button either removes the note from the database if you are the owner (creator) or only removes your access to it if you are not (the note is shared with you).
## Searching
The search bar searches through the title and body of the notes and displays them in the sidebar. A match occurs when the note **contains** the search criteria as a whole. Clicking the "x" to the right of the search bar will clear the text in it and refresh the page to show all of the notes instead of only the ones that match your search criteria.
## Sharing
You can share your notes with other users, letting them view and edit them, by typing in their username and pressing the button.
<br><br>
An error will occur if you try to share with someone who is already shared, a non-existent user, or try to share while not being the owner (creator) of the note. Also, as previously stated, if a note is shared with you, meaning you haven't created it, the delete button only removes your access from the note.
## Database structure
The commands to create the SQL tables are in `create-tables.sql`. Here's a quick summary of them:
<br><br>
The `users` table contains an autoincrementing `id` field, a `username` text field, and a `hash` text field representing the hashed password. There is also a unique index on the username to make sure people can't have the same one.
<br><br>
The `notes` table contains an autoincrementing `id` field, a `name` text field representing the title of the note, a `content` text field representing the body of the note, and an `owner` field representing the id of the user that created the note.
<br><br>
The `note_access` table (who has access to which notes) contains an autoincrementing `id` field, a `userid` field representing the id of the user who has access, and a `noteid` field representing the id of the note the user has access to. There is also a unique constraint that makes sure `(userid, noted)` pairs are unique.
