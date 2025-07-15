const form = document.getElementById("uploadForm");
const statusDiv = document.getElementById("status");
const logDiv = document.getElementById("log");
const downloadLink = document.getElementById("downloadLink");
const fattureList = document.getElementById("fattureList");
const previewContainer = document.getElementById("previewContainer");
const pdfPreview = document.getElementById("pdfPreview");

form.addEventListener("submit", e => {
  e.preventDefault();
  downloadLink.style.display = "none";
  fattureList.innerHTML = "";
  previewContainer.style.display = "none";
  statusDiv.textContent = "Caricamento in corso...";
  const btn = form.querySelector("button");
  btn.disabled = true;

  const formData = new FormData(form);

  fetch("/upload", {
    method: "POST",
    body: formData
  })
  .then(res => res.json())
  .then(data => {
    if(data.status === "success"){
      statusDiv.textContent = "Fatture generate con successo!";
      downloadLink.href = data.download;
      downloadLink.style.display = "block";

      if(data.pdf_files && data.pdf_files.length){
        data.pdf_files.forEach(file => {
          const link = document.createElement("a");
          link.textContent = file;
          link.href = "#";
          link.addEventListener("click", e => {
            e.preventDefault();
            pdfPreview.src = "/pdf/" + encodeURIComponent(file);
            previewContainer.style.display = "block";
          });
          fattureList.appendChild(link);
        });
      }
    } else {
      statusDiv.textContent = "Errore: " + data.message;
    }
    btn.disabled = false;
  })
  .catch(err => {
    statusDiv.textContent = "Errore di rete o server.";
    btn.disabled = false;
  });
});
