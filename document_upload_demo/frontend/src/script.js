document.getElementById("source-type").addEventListener("change", function () {
  const type = this.value;
  document.getElementById("api-fields").style.display = type === "api" ? "block" : "none";
  document.getElementById("upload-field").style.display = type === "upload" ? "block" : "none";
  document.getElementById("manual-field").style.display = type === "manual" ? "block" : "none";
});

document.getElementById("ingestion-form").addEventListener("submit", async function (e) {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData();

  const data = {
    instance_id: form.instance_id.value,
    document_type: form.document_type.value,
    source_type: form.source_type.value,
    source_system: form.source_system.value,
    document_metadata: {
      title: form.title.value,
      language: form.language.value,
      region: form.region.value,
      author: form.author.value,
      tags: form.tags.value.split(",")
    },
    api_connection_info: {
      auth_type: form.auth_type?.value || null,
      client_id: form.client_id?.value || null,
      client_secret: form.client_secret?.value || null,
      token_url: form.token_url?.value || null,
      data_url: form.data_url?.value || null,
    },
    manual_text: form.manual_text?.value || null
  };

  formData.append("data", JSON.stringify(data));
  console.log("Form Data:", data);
  const fileInput = document.getElementById("file-upload");
  if (fileInput?.files?.length > 0) {
    formData.append("file_upload", fileInput.files[0]);
  }
  // Inspect FormData contents for debugging
  const formDataEntries = [];
  for (let pair of formData.entries()) {
    formDataEntries.push([pair[0], pair[1]]);
  }
  // alert("Submitting data: " + JSON.stringify(formDataEntries));

  try {
    const res = await fetch("http://localhost:8000/admin/documents/ingest", {
      method: "POST",
      body: formData
    });
    const result = await res.json();
    document.getElementById("message").textContent = " Success: " + JSON.stringify(result);
  } catch (err) {
    document.getElementById("message").textContent = " Error: " + err.message;
  }
});
