document.querySelector('.play-button').addEventListener('click', function () {
  const videoOverlay = document.getElementById('video-overlay');
  const videoIframe = document.getElementById('video-iframe');
  videoOverlay.style.display = 'flex';
});

// To close the video overlay when clicking outside of the video
document.getElementById('video-overlay').addEventListener('click', function (event) {
  if (event.target.id === 'video-overlay') {
    this.style.display = 'none';
    document.getElementById('video-iframe').src = '';
  }
});