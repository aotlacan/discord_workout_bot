📋 GymBot Help Menu
GymBot is a Discord bot that helps track and log gym workout minutes, manage a **gym** role, and display a live leaderboard of the top grinders or just between you and your lazy friends.
All Dat is saved locally in 'gym_data.json' and updates automatically when commamnds are used.

## ⚡ Features
- Assign yourself a **gym** role with reactions or commands  
- Log and track your workout minutes  
- View total minutes logged  
- See the top 5 users on the leaderboard  
- Remove previously logged time if needed

- ## 📋 Commands

### Role Management
- **`!joingym`**  
  Join the gym and get the **gym** role. Required before logging minutes.  

- **`!leavegym`**  
  Remove the **gym** role from yourself.  

- **React with 🏋️**  
  If the bot’s gym role message is posted, you can react with 🏋️ to automatically receive the **gym** role.

  ### Logging Minutes
- **`!log <minutes>`**  
  Log workout time. Accepts values between 1 and 1440 minutes.  
  Example: `!log 45`  

- **`!remove <minutes>`**  
  Remove previously logged minutes. Your total will never go below zero.  
  Example: `!remove 15`  

- **`!total`**  
  View how many total minutes you have logged.

  ### Leaderboard
- **`!top`** *(alias: leaderboard update)*  
  See the top 5 users ranked by total minutes logged.  

- **`!leaderboardmessage`**  
  Post or update the leaderboard embed in the channel.

  ### Setup & Utility
- **`!gymrolemessage`**  
  Post the reaction message to allow others to join the gym role with 🏋️.  

- **`!alert`**  
  Sends an alert message reminding users to only run commands while the bot is online.  

- **`!setup`**  
  Runs the initial setup: posts the alert, gym role message, help menu, and leaderboard.  

- **`!help`**  
  Display the help menu with all commands.  

## 💾 Data Storage
- Workout minutes, gym role message ID, and leaderboard message ID are saved in `gym_data.json`.  
- Data is automatically saved when commands are used and restored when the bot restarts.  

## IMPORTANT NOTE

You must make a '.env' file in your directory folder and add the code:

```env
DISCORD_TOKEN="ENTER YOUR DISCORD TOKEN HERE"
