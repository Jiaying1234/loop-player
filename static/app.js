const dialog = document.querySelector("#add-dialog");
const openDialogButton = document.querySelector("#open-dialog");
const closeDialogButton = document.querySelector("#close-dialog");
const urlForm = document.querySelector("#url-form");
const urlInput = document.querySelector("#tiktok-url");
const status = document.querySelector("#status");

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

  status.textContent = result.message;
  if (result.accepted) {
    status.classList.add("success");
  }
});
