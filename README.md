# TaskTide

## 🎬 Demo
<!-- Place your video demo link here -->
[Watch the Demo](#)

---

## Overview

**TaskTide** is a simple yet effective productivity web application designed to help users organize their daily tasks, manage notes, and maintain focus using the Pomodoro technique. Built using Flask for the backend and HTML, CSS, and JavaScript for the frontend, TaskTide aims to provide a clean, intuitive, and distraction-free environment for anyone looking to boost their productivity.

---

## Features

- **Note Taking:**  
  Quickly jot down ideas, reminders, or meeting notes. Notes are saved per user and can be edited or deleted at any time.

- **To-Do List:**  
  Create, manage, and check off tasks as you complete them. The to-do list is designed for simplicity, allowing you to focus on what matters most.

- **Pomodoro Timer:**  
  Use the built-in Pomodoro timer to break your work into focused intervals, separated by short breaks. This helps maintain concentration and avoid burnout.

- **User Settings:**  
  Change your username, password, and profile picture, or delete your account entirely.

---

## File Structure and Descriptions

- **app.py**  
  The main Flask application. Handles routing, user authentication, session management, and all backend logic for notes, to-dos, the Pomodoro timer, and user settings. It also manages database connections and serves as the entry point for running the app.

- **/templates/**  
  Contains all HTML templates rendered by Flask.  
  - **layout.html:** The base template that includes the navigation bar, sidebar, and layout for all pages.
  - **dashboard.html:** The main landing page after login, showing a summary of notes, to-dos, and the Pomodoro widget.
  - **notes.html:** The interface for creating, viewing, editing, and deleting notes.
  - **todo.html:** The to-do list interface, allowing users to add, check off, and remove tasks.
  - **pomodoro.html:** The Pomodoro timer page, providing controls to start, pause, and reset the timer.
  - **settings.html:** The user settings page for updating profile information and account management.
  - **login.html / register.html:** Authentication pages for user login and registration.

- **/static/**  
  Contains all static assets (CSS, JS, images).  
  - **styles.css:** The main stylesheet for the app, providing a modern, clean look using Bootstrap and custom styles.
  - **script.js:** Handles all client-side interactivity, including the Pomodoro timer logic, UI updates, etc.
  - **uploads/**: Stores user-uploaded profile pictures.

---

## How to Run

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Xeliia/TaskTide.git
   ```

2. **Navigate to the project folder:**

3. **(Optional) Set up a virtual environment and install dependencies:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Run the app:**
   ```bash
   flask run
   ```

5. **Open your browser and go to the link provided by the terminal**  

---

**AI Assistance Notice:**  

Parts of this project were developed with the help of GitHub Copilot and ChatGPT, used as coding assistants for code suggestions, debugging, and documentation. All design decisions and final implementation are my own.