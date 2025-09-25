const audioInput = document.getElementById('audioFile');
const uploadLabel = document.getElementById('uploadLabel');

audioInput.addEventListener('change', () => {
  if (audioInput.files.length > 0) {
    uploadLabel.textContent = audioInput.files[0].name; // show selected file
  } else {
    uploadLabel.textContent = 'Choose Audio File';
  }
});


document.getElementById('uploadBtn').addEventListener('click', async () => {
  const input = document.getElementById('audioFile');
  const info = document.getElementById('patientInfo');

  if (!input.files.length) {
    alert('Please select an audio file to upload.');
    return;
  }

  const file = input.files[0];
  const formData = new FormData();
  formData.append('file', file);

  info.textContent = 'Uploading and processing...';

  try {
    const response = await fetch('/api/upload-audio', {   // 👈 updated path
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      info.textContent = 'Error: ' + (errorData.error || response.statusText);
      return;
    }

    const data = await response.json();
    info.textContent = JSON.stringify(data.patient_info, null, 2);
  } catch (error) {
    info.textContent = 'Upload failed: ' + error.message;
  }
});
