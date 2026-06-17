<h2>Main features of TelegramMaster-PRO:</h2>

- As of 10/02/2025, the program has 41 features
- As of 10/02/2025, 33 of the program's features have been rewritten from scratch
- Update readiness as of 10/02/2025 is 80.48%

### Inviting:

In the settings of the "Inviting" feature, you can select a group and set the start time for the "Inviting at a specific
time" feature. In the inviting settings, you can configure the minimum and maximum time delay; the delay is chosen
randomly within the specified range. For example, if the user enters 5–8, it means the delay will be chosen randomly
between 5 and 8 seconds, such as 6, 7, or 5. In the menu, you can set a limit per account, meaning the program will
retrieve the specified number of users from the database. If the user enters 10, the program will retrieve 10 usernames.
In the "Inviting" menu, you can enter a link for inviting (the group where users will be invited to) or select a group
for inviting. Cupertino Switch toggles are used to select the desired feature.

- 🔄 Regular inviting (10/26/2025)
- ⏰ Inviting once an hour (10/26/2025)
- 📅 Inviting at a specific time (10/26/2025)
- 🗓️ Daily inviting (10/26/2025)

### Parsing:

- Parsing group members (select account, check the corresponding box, enter the link, click "Parse").
- Parsing a single group or multiple groups
- Parsing a selected group from the ones the account is subscribed to
- Parsing active group members
- Parsing groups/channels that the account is subscribed to
- Clearing the list of previously parsed data

### 📒 Contact Management:

The contact management functionality allows you to generate, parse, add, and delete contacts in the Telegram account's
phone book.  
All data is stored in the database at user_data/software_database.db.  
In the "Generate contact list" feature, the user compiles a list of phone numbers to check for Telegram registration.
Example:   
+11323535395  
+11323535397 +11323535398 +11323535335  
If a number is registered, the program will add it to the phone book. Phone numbers are written to the contact table in
the database at user_data/software_database.db.

In the "Parse contact list" feature, the program connects to the account in the user_data/accounts folder, parses the
Telegram account's phone book, and if a contact is found, writes the details to the account_contacts table in the
database at user_data/software_database.db.  
The "Delete contacts" feature cleans up the phone book of the account located at user_data/accounts. It is recommended
to run the "Parse contact list" feature before performing this action.  
In the "Add contacts" feature, the program retrieves contacts from the contact table in the database at
user_data/software_database.db and adds them to the phone book of the account located at user_data/accounts.

- Contact list generation
- Parsing the contact list
- Deleting contacts
- Adding contacts

### Subscribing, unsubscribing:

- Subscribing
- Unsubscribing

### Connecting Accounts:

- Connecting accounts via phone number
- Connecting session accounts

### Message Distribution:

- Sending direct messages (broadcasting text messages, files, or messages + files)
- Broadcasting messages to chats (broadcasting text messages, files, or messages + files)

### Reactions Management:

- Setting reactions
- Boosting post views
- Automatic reactions placement

### Account Verification:

- Checking via Spam Bot
- Validity check
- Renaming accounts
- Full verification

### Creating Groups (Chats)

In the "Create groups (chats)" feature, you need to select an account and click "Start". If successful, the program will
create the group.

### BIO Editing:

In the "Change username" feature, the user inputs a username for the account. If the username is already taken, the
program notifies the user that it exists. In the description feature, the user inputs a biography/description for the
Telegram profile. In the "Change first name" feature, the user can change the first name by entering a new name. To
change the profile picture on an account, place the photo in the user_data/bio folder.

- Changing username
- Changing profile picture
- Changing biography/description
- Changing first name
- Changing last name

### Settings:

- 👍 Select reactions
- 🔐 Save proxy
- 🔄 Switch accounts
- Save api_id, api_hash
- ✉️ Save messages
- Save reaction links

### Import List of Previously Parsed Data

### Documentation
