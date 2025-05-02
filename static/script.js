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
          // Update the note title in the sidebar as well
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
  