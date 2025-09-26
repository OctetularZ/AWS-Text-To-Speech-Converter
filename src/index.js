const apiUrl = import.meta.env.VITE_API_URL;

const textInput = document.getElementById('text-input');
const voiceSelect = document.getElementById('voice-select');
const convertBtn = document.getElementById('convert-btn');
const audioPlayerDiv = document.getElementById('audio-player');
const audioElem = document.getElementById('audio');
const downloadLink = document.getElementById('download-link');
const errorMsg = document.getElementById('error-msg');

convertBtn.addEventListener('click', async () => {
  errorMsg.textContent = '';
  const text = textInput.value.trim();
  const voice = voiceSelect.value;

  if (!text) {
    errorMsg.textContent = 'Please enter some text.';
    return;
  }

  convertBtn.disabled = true;
  convertBtn.textContent = 'Converting...';

  try {
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, voice })
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    const data = await response.json();

    if (!data.audioUrl) {
      throw new Error('No audio URL returned from backend.');
    }

    audioElem.src = data.audioUrl;
    downloadLink.href = data.audioUrl;
    downloadLink.download = `speech_${Date.now()}.mp3`;

    audioPlayerDiv.style.display = 'block';

  } catch (error) {
    errorMsg.textContent = error.message;
    audioPlayerDiv.style.display = 'none';
  } finally {
    convertBtn.disabled = false;
    convertBtn.textContent = 'Convert to Speech';
  }
});
