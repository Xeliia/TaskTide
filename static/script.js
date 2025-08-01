// Most of the code in this file was developed with the assistance of GitHub Copilot and ChatGPT.
// Specifically the logic for notes, pomodoro timer syncing with the dashboard

const allSideMenu = document.querySelectorAll('#sidebar .side-menu.top li a');
const currentPage = window.location.pathname;

allSideMenu.forEach(item => {
    const li = item.parentElement;

    if (item.getAttribute('href') === currentPage) {
        li.classList.add('active');
    } else {
        li.classList.remove('active');
    }

    item.addEventListener('click', function () {
        allSideMenu.forEach(i => {
            i.parentElement.classList.remove('active');
        });
        li.classList.add('active');
    });
});

const menuBar = document.querySelector('#content nav .bx.bx-menu');
const sidebar = document.getElementById('sidebar');
const content = document.getElementById('content');

if (localStorage.getItem('sidebar-hidden') === 'true') {
    sidebar.classList.add('hide');
}

menuBar.addEventListener('click', function () {
	sidebar.classList.toggle('hide');
	localStorage.setItem('sidebar-hidden', sidebar.classList.contains('hide'));
})

/* NOTES */
const addNoteButton = document.getElementById("add-note-btn");
if (addNoteButton) {
    addNoteButton.addEventListener("click", createNewNote);
}

function createNewNote() {
  fetch('/notes', {
    method: 'POST',
  })
  .then(response => response.json())
  .then(data => {
    const noteId = data.id;
    
    const notesList = document.querySelector('.notes-list');
    const newNoteItem = document.createElement('li');
    newNoteItem.classList.add('note-item');
    newNoteItem.dataset.noteId = noteId;
    newNoteItem.innerHTML = `New Note`;
    
    notesList.appendChild(newNoteItem);

    newNoteItem.classList.add('active');
    
    window.location.href = `/notes?selected=${noteId}`;
  })
  .catch(error => {
    console.error('Error creating new note:', error);
  });
}

const notesList = document.querySelector('.notes-list');

if (notesList) {
    notesList.addEventListener('click', function(event) {
        const noteItem = event.target.closest('.note-item');
        
        if (noteItem) {
            const noteId = noteItem.dataset.noteId;
            
            window.location.href = `/notes?selected=${noteId}`;
            
            const allNoteItems = document.querySelectorAll('.note-item');
            allNoteItems.forEach(item => item.classList.remove('active'));
            noteItem.classList.add('active');
        }
    });
}

function highlightSelectedNote() {
    const urlParams = new URLSearchParams(window.location.search);
    const selectedNoteId = urlParams.get('selected');
    
    if (selectedNoteId) {
        const notesList = document.querySelector('.notes-list');
        const noteItems = notesList.querySelectorAll('.note-item');
        
        noteItems.forEach(noteItem => {
            if (noteItem.dataset.noteId === selectedNoteId) {
                noteItem.classList.add('active');
            }
        });
    }
}

window.addEventListener('load', highlightSelectedNote);

function renameNote(event) {
    const newTitle = event.target.value;
    const noteId = event.target.dataset.noteId;
    
    if (newTitle && noteId) {
      fetch('/notes/rename', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ note_id: noteId, title: newTitle })
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          console.log('Note renamed successfully');
          const noteItem = document.querySelector(`[data-note-id="${noteId}"]`);
          if (noteItem) {
            noteItem.textContent = newTitle;
          }
        } else {
          console.error('Failed to rename note');
        }
      })
      .catch(error => {
        console.error('Error renaming note:', error);
      });
    }
}
  
function checkEnter(event) {
    if (event.key === 'Enter') {
      event.preventDefault();
      renameNote(event);
    }
}

const deleteNoteButton = document.querySelector('.bxs-trash');
if (deleteNoteButton) {
  deleteNoteButton.addEventListener('click', deleteNote);
}

function deleteNote() {
  const selectedNote = document.querySelector('.note-item.active');

  if (selectedNote) {
    const noteId = selectedNote.dataset.noteId;

    fetch(`/notes/${noteId}`, {
      method: 'DELETE',
    })
    .then(response => {
      if (response.ok) {
        selectedNote.remove();
        window.location.href = '/notes';
      } else {
        console.error('Failed to delete note');
      }
    })
    .catch(error => {
      console.error('Error deleting note:', error);
    });
  } else {
    alert('Please select a note to delete.');
  }
}

function saveContent(event) {
    const newContent = event.target.value;
    const noteId = event.target.dataset.noteId;
  
    if (newContent && noteId) {
      fetch('/notes/save-content', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ note_id: noteId, content: newContent })
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          console.log('Note content saved successfully');
        } else {
          console.error('Failed to save note content');
        }
      })
      .catch(error => {
        console.error('Error saving note content:', error);
      });
    }
}


/* Pomodoro Timer */
const timerDisplay = document.getElementById('pomodoro-timer');
const startBtn = document.getElementById('start-btn');
const pauseBtn = document.getElementById('pause-btn');
const resetBtn = document.getElementById('reset-btn');
const statusText = document.getElementById('pomodoro-status');

function setPomodoroBg(state) {
  document.body.classList.remove('pomodoro-running', 'pomodoro-paused', 'pomodoro-alarm');
  if (state) document.body.classList.add(state);
}

if (timerDisplay && startBtn && pauseBtn && resetBtn && statusText) {
  let workDuration = 25 * 60;
  let breakDuration = 5 * 60;
  let timeLeft = workDuration;
  let timer = null;
  let isRunning = false;
  let isWork = true;
  let endTime = null;

  const tickAudio = new Audio('/static/tick.mp3');
  const alarmAudio = new Audio('/static/alarm.mp3');
  alarmAudio.loop = true;

  setPomodoroBg();

  function syncFromLocalStorage() {
    const saved = localStorage.getItem('pomodoroState');
    if (saved) {
      const state = JSON.parse(saved);
      if (state.endTime && state.endTime > Date.now()) {
        endTime = state.endTime;
        isWork = state.isWork;
        timeLeft = Math.max(0, Math.round((endTime - Date.now()) / 1000));
        isRunning = true;
        startBtn.disabled = true;
        pauseBtn.disabled = false;
        resetBtn.disabled = false;
        setPomodoroBg('pomodoro-running');
        updateDisplay();
        timer = setInterval(timerTick, 1000);
      } else {
        isWork = state.isWork ?? true;
        timeLeft = state.timeLeft ?? workDuration;
        isRunning = false;
        endTime = null;
        updateDisplay();
        startBtn.disabled = false;
        pauseBtn.disabled = true;
        resetBtn.disabled = timeLeft === workDuration;
        setPomodoroBg();
      }
    } else {
      isWork = true;
      timeLeft = workDuration;
      isRunning = false;
      endTime = null;
      updateDisplay();
      startBtn.disabled = false;
      pauseBtn.disabled = true;
      resetBtn.disabled = true;
      setPomodoroBg();
    }
  }

  function saveState() {
    localStorage.setItem('pomodoroState', JSON.stringify({
      timeLeft,
      isWork,
      endTime
    }));
  }

  function clearState() {
    localStorage.removeItem('pomodoroState');
  }

  function updateDisplay() {
    const min = String(Math.floor(timeLeft / 60)).padStart(2, '0');
    const sec = String(timeLeft % 60).padStart(2, '0');
    timerDisplay.textContent = `${min}:${sec}`;
    statusText.textContent = isWork ? (isRunning ? "Work session running" : "Work session") : (isRunning ? "Break running" : "Break time!");
  }

  function timerTick() {
    const now = Date.now();
    timeLeft = Math.max(0, Math.round((endTime - now) / 1000));

    if (timeLeft <= 10 && timeLeft > 0) {
      tickAudio.currentTime = 0;
      tickAudio.play();
    }
    updateDisplay();
    localStorage.setItem('pomodoroState', JSON.stringify({
      timeLeft,
      isWork,
      endTime
    }));

    if (timeLeft <= 0) {
      clearInterval(timer);
      isRunning = false;
      alarmAudio.currentTime = 0;
      alarmAudio.play();
      setPomodoroBg('pomodoro-alarm');
      if (isWork) {
        isWork = false;
        timeLeft = breakDuration;
        statusText.textContent = "Break time! 🎉 (Click Start)";
      } else {
        isWork = true;
        timeLeft = workDuration;
        statusText.textContent = "Back to work! (Click Start)";
      }
      updateDisplay();
      localStorage.setItem('pomodoroState', JSON.stringify({
        timeLeft,
        isWork,
        endTime: null
      }));
      startBtn.disabled = false;
      pauseBtn.disabled = true;
      endTime = null;
    }
  }

  function startTimer() {
    alarmAudio.pause();
    alarmAudio.currentTime = 0;
    setPomodoroBg('pomodoro-running');

    if (!isRunning) {
      endTime = Date.now() + timeLeft * 1000;
      localStorage.setItem('pomodoroState', JSON.stringify({
        timeLeft,
        isWork,
        endTime
      }));

      timer = setInterval(timerTick, 1000);

      isRunning = true;
      startBtn.disabled = true;
      pauseBtn.disabled = false;
      resetBtn.disabled = false;
    }
  }

  function pauseTimer() {
    if (isRunning) {
      clearInterval(timer);
      isRunning = false;
      timeLeft = Math.max(0, Math.round((endTime - Date.now()) / 1000));
      endTime = null;
      startBtn.disabled = false;
      pauseBtn.disabled = true;
      saveState();
      setPomodoroBg('pomodoro-paused');
    }
  }

  function resetTimer() {
    clearInterval(timer);
    isRunning = false;
    isWork = true;
    timeLeft = workDuration;
    endTime = null;
    updateDisplay();
    startBtn.disabled = false;
    pauseBtn.disabled = true;
    resetBtn.disabled = true;
    statusText.textContent = "Ready to work!";
    clearState();
    alarmAudio.pause();
    alarmAudio.currentTime = 0;
    setPomodoroBg();
  }

  startBtn.addEventListener('click', startTimer);
  pauseBtn.addEventListener('click', pauseTimer);
  resetBtn.addEventListener('click', resetTimer);

  syncFromLocalStorage();
}