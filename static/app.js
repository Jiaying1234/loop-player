const dialog = document.querySelector("#add-dialog");
const openDialogButton = document.querySelector("#open-dialog");
const closeDialogButton = document.querySelector("#close-dialog");
const urlForm = document.querySelector("#url-form");
const urlInput = document.querySelector("#tiktok-url");
const status = document.querySelector("#status");
const editButton = document.querySelector("#edit-button");
const renameForms = document.querySelectorAll(".rename-form");

// Show or hide the rename controls.
editButton.addEventListener("click", () => {
  document.body.classList.toggle("editing");
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
      window.location.reload();
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
