const dialog = document.querySelector("#add-dialog");
const openDialogButton = document.querySelector("#open-dialog");
const closeDialogButton = document.querySelector("#close-dialog");
const urlForm = document.querySelector("#url-form");
const urlInput = document.querySelector("#tiktok-url");
const status = document.querySelector("#status");
const editButton = document.querySelector("#edit-button");
const renameForms = document.querySelectorAll(".rename-form");
const audioPlayers = document.querySelectorAll("audio");
const searchButton = document.querySelector("#search-button");
const searchRow = document.querySelector("#search-row");
const searchInput = document.querySelector("#search-input");
const clearSearchButton = document.querySelector("#clear-search");
const trackCards = document.querySelectorAll(".track-card");
const searchEmpty = document.querySelector("#search-empty");
const deleteButton = document.querySelector("#delete-button");
const deleteTrackButtons = document.querySelectorAll(".delete-track-button");
const playButtons = document.querySelectorAll(".play-button");
const reorderButton = document.querySelector("#reorder-button");
const saveOrderButton = document.querySelector("#save-order-button");
const dragHandles = document.querySelectorAll(".drag-handle");

// Display a duration as minutes and seconds.
function formatDuration(seconds) {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60).toString().padStart(2, "0");
  return `${minutes}:${remainingSeconds}`;
}

// Start reorder mode and make each sound draggable.
reorderButton.addEventListener("click", () => {
  document.body.classList.add("reordering");
  trackCards.forEach((card) => {
    card.draggable = false;
  });
});

let draggedCard;
let draggedPointerId = null;

// Move a sound with its handle so touch devices can reorder it.
dragHandles.forEach((handle) => {
  handle.addEventListener("pointerdown", (event) => {
    if (!document.body.classList.contains("reordering")) {
      return;
    }
    event.preventDefault();
    draggedCard = handle.closest(".track-card");
    draggedPointerId = event.pointerId;
    draggedCard.classList.add("dragging");
  });
});

// Move the active row while the handle is being held on a touch screen.
document.addEventListener("pointermove", (event) => {
  if (!draggedCard || event.pointerId !== draggedPointerId) {
    return;
  }
  event.preventDefault();
  const target = document.elementFromPoint(event.clientX, event.clientY)?.closest(".track-card");
  if (target && target !== draggedCard) {
    const afterCard = event.clientY > target.getBoundingClientRect().top + target.offsetHeight / 2;
    target.parentNode.insertBefore(draggedCard, afterCard ? target.nextSibling : target);
  }
}, {passive: false});

// Finish the reorder when the handle is released.
document.addEventListener("pointerup", (event) => {
  if (draggedCard && event.pointerId === draggedPointerId) {
    draggedCard.classList.remove("dragging");
    draggedCard = null;
    draggedPointerId = null;
  }
});

// Clean up if the phone cancels the touch gesture.
document.addEventListener("pointercancel", (event) => {
  if (draggedCard && event.pointerId === draggedPointerId) {
    draggedCard.classList.remove("dragging");
    draggedCard = null;
    draggedPointerId = null;
  }
});

// Save the dragged order and leave reorder mode.
saveOrderButton.addEventListener("click", async () => {
  const filenames = [...document.querySelectorAll(".track-card")].map(
    (card) => card.dataset.filename,
  );
  const response = await fetch("/reorder", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(filenames),
  });
  const result = await response.json();
  if (result.accepted) {
    window.location.reload();
  } else {
    window.alert(result.message);
  }
});

// Pause every other sound when one starts playing.
audioPlayers.forEach((audio) => {
  const card = audio.closest(".track-card");
  const duration = card.querySelector("[data-duration]");
  const playButton = card.querySelector(".play-button");

  audio.addEventListener("loadedmetadata", () => {
    duration.textContent = formatDuration(audio.duration);
  });

  audio.addEventListener("play", () => {
    audioPlayers.forEach((otherAudio) => {
      if (otherAudio !== audio) {
        otherAudio.pause();
        otherAudio.currentTime = 0;
      }
    });
    playButtons.forEach((button) => button.classList.remove("is-playing"));
    playButton.classList.add("is-playing");
  });

  // Reset this sound when its own play button is pressed to stop it.
  audio.addEventListener("pause", () => {
    audio.currentTime = 0;
    playButton.classList.remove("is-playing");
  });
});

// Let the black square control playback without showing browser controls.
playButtons.forEach((button, index) => {
  const audio = audioPlayers[index];
  button.addEventListener("click", () => {
    if (audio.paused) {
      audio.play();
    } else {
      audio.pause();
    }
  });
});

// Open the search bar and let the user type.
searchButton.addEventListener("click", () => {
  searchRow.classList.add("search-visible");
  searchInput.focus();
});

// Show only songs whose names match the search text.
searchInput.addEventListener("input", () => {
  const query = searchInput.value.trim().toLowerCase();
  let matches = 0;

  trackCards.forEach((card) => {
    const matchesSearch = card.dataset.title.includes(query);
    card.hidden = !matchesSearch;
    if (matchesSearch) {
      matches += 1;
    }
  });

  searchEmpty.hidden = matches > 0 || query === "";
});

// Clear the search and return to the full song list.
clearSearchButton.addEventListener("click", () => {
  searchInput.value = "";
  trackCards.forEach((card) => {
    card.hidden = false;
  });
  searchEmpty.hidden = true;
  searchRow.classList.remove("search-visible");
});

// Show or hide the rename controls.
editButton.addEventListener("click", () => {
  if (document.body.classList.contains("editing")) {
    window.location.reload();
    return;
  }
  document.body.classList.add("editing");
});

// Show or hide the delete controls.
deleteButton.addEventListener("click", () => {
  document.body.classList.toggle("deleting");
});

// Delete a sound after the user confirms the action.
deleteTrackButtons.forEach((button) => {
  button.addEventListener("click", async () => {
    if (!window.confirm("Delete this saved audio?")) {
      return;
    }

    const formData = new FormData();
    formData.append("filename", button.dataset.filename);
    const response = await fetch("/delete", {
      method: "POST",
      body: formData,
    });
    const result = await response.json();
    if (result.accepted) {
      // Remove the deleted sound while keeping delete mode open.
      button.closest(".track-card").remove();
    } else {
      window.alert(result.message);
    }
  });
});

// Save a renamed sound and refresh its displayed name.
renameForms.forEach((form) => {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const response = await fetch("/rename", {
      method: "POST",
      body: new FormData(form),
    });
    const result = await response.json();
    if (result.accepted) {
      // Update this title while keeping rename mode open.
      const card = form.closest(".track-card");
      card.querySelector("h2").textContent = form.elements.name.value;
      card.dataset.title = form.elements.name.value.toLowerCase();
      form.querySelector("button").blur();
    } else {
      window.alert(result.message);
    }
  });
});

// Open the address box from the plus button.
openDialogButton.addEventListener("click", () => {
  dialog.showModal();
  urlInput.focus();
});

// Close the address box.
closeDialogButton.addEventListener("click", () => {
  dialog.close();
});

// Close the box when the dark background is clicked.
dialog.addEventListener("click", (event) => {
  if (event.target === dialog) {
    dialog.close();
  }
});

// Send the URL and show the result.
urlForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  status.className = "status";
  status.textContent = "";

  const response = await fetch("/convert", {
    method: "POST",
    body: new FormData(urlForm),
  });
  const result = await response.json();

  if (!result.accepted) {
    status.textContent = result.message;
  } else {
    window.location.reload();
  }
});
