# Notes
#### Video Demo: https://youtu.be/Wn-I-0-JoUI
## Login and Register
If you are not logged in, you will be sent to the login page. You can register with the button in the top right corner.
## Home Page
Once you log in, there will be a list of notes on the left in order of last updated. Below the sidebar is the add field and button. When you click on a note, two fields on the right will appear, the top one is the title (seen on the sidebar when selecting notes), and the bottom is the body. Below that are the share (and username field), save, and delete buttons.
## Adding
To add a note, type in the name of it and press the add button. This will add it to your list of notes and open it up for you to edit.
## Editing
You can click the title and body fields to change them and click the save button to save your changes.
## Deleting
This button either removes the note from the database if you are the owner (creator) or only removes your access to it if you are not (shared with).
## Sharing
You can share your notes with other users, letting them view and edit them, by typing in their username and pressing the button.
<br><br>
An error will occur if you try to share with someone who is already shared, a non-existent user, or try to share while not being the owner (creator) of the note.
## Database structure
The commands to create the SQL tables are in `create-tables.sql`. Here's a quick summary of them:
<br><br>
The `users` table contains an autoincrementing `id` field, a `username` text field, and a `hash` text field representing the hashed password. There is also a unique index on the username to make sure people can't have the same one.
<br><br>
The `notes` table contains an autoincrementing `id` field, a `name` text field representing the title of the note, a `content` text field representing the body of the note, and an `owner` field representing the id of the user that created the note.
<br><br>
The `note_access` table (who has access to which notes) contains an autoincrementing `id` field, a `userid` field representing the id of the user who has access, and a `noteid` field representing the id of the note the user has access to. There is also a unique constraint that makes sure `(userid, noted)` pairs are unique.
