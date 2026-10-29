const fileInput = document.querySelector('#sketch');
const goalInput = document.querySelector('#goal');
const runButton = document.querySelector('#run');
const canvas = document.querySelector('#sim');
const ctx = canvas.getContext('2d');
const status = document.querySelector('#status');
const attempts = document.querySelector('#attempts');
const result = document.querySelector('#result');
const render = document.querySelector('#render');

function drawFrame(frame) {
  ctx.fillStyle = '#eee1ce';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  for (const [id, body] of Object.entries(frame.bodies || {})) {
    ctx.save();
    ctx.translate(body.x, canvas.height - body.y);
    ctx.rotate(-body.angle);
    ctx.fillStyle = id.startsWith('ball') ? '#d06b43' : id.includes('bell') ? '#d6a83d' : '#342d27';
    ctx.beginPath();
    ctx.arc(0, 0, id.startsWith('ball') ? 14 : 9, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }
}

function showSketch(file, masks) {
  const image = new Image();
  image.onload = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = '#b34e35';
    ctx.lineWidth = 3;
    for (const mask of masks || []) {
      ctx.strokeRect(mask.box[0], mask.box[1], mask.box[2], mask.box[3]);
    }
  };
  image.src = URL.createObjectURL(file);
}

function animate(frames) {
  let index = 0;
  function tick() {
    if (index >= frames.length) return;
    drawFrame(frames[index]);
    index += 1;
    requestAnimationFrame(tick);
  }
  tick();
}

runButton.onclick = async () => {
  if (!fileInput.files[0]) {
    status.textContent = 'Choose a sketch first';
    return;
  }
  runButton.disabled = true;
  attempts.innerHTML = '';
  render.style.display = 'none';
  status.textContent = 'Reading sketch…';
  const form = new FormData();
  form.append('file', fileInput.files[0]);
  form.append('goal', goalInput.value);
  const response = await fetch('/upload', { method: 'POST', body: form });
  if (!response.ok) {
    status.textContent = 'Upload failed';
    runButton.disabled = false;
    return;
  }
  const data = await response.json();
  showSketch(fileInput.files[0], data.masks);
  status.textContent = 'Verifier running…';
  const stream = new EventSource(`/run/${data.run_id}/stream`);
  stream.addEventListener('attempt', (event) => {
    const attempt = JSON.parse(event.data);
    const item = document.createElement('li');
    item.textContent = `Attempt ${attempt.n}: ${attempt.reasoning}`;
    attempts.append(item);
    animate(attempt.result.frames);
  });
  stream.addEventListener('done', (event) => {
    const done = JSON.parse(event.data);
    stream.close();
    runButton.disabled = false;
    status.textContent = done.success ? 'Verified' : 'Stopped after repair cap';
    result.textContent = done.success
      ? 'The physics verifier confirmed that the machine reaches its goal.'
      : 'The verifier could not confirm the goal within the repair cap.';
    if (done.success) {
      render.src = done.render_url;
      render.style.display = 'block';
    }
  });
};
