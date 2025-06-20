const cardContainer = document.querySelector('.card-container');
const modalOverlay = document.getElementById('modalOverlay');
const modalScroll = document.getElementById('modalScroll');
const closeBtn = document.getElementById('closeBtn');
let storiesData = [];

// Fetch stories from JSON
fetch('/static/JS/stories.json')
  .then(response => response.json())
  .then(data => {
    storiesData = data.stories;
    renderCards(storiesData);
  })
  .catch(err => {
    console.error('Error loading JSON:', err);
    cardContainer.innerHTML = '<p>Failed to load stories.</p>';
  });

// Create and insert cards into the DOM
function renderCards(stories) {
  cardContainer.innerHTML = ''; // clear existing
  stories.forEach((story, index) => {
    const card = document.createElement('div');
    card.classList.add('card');
    card.setAttribute('data-id', story.id);

    card.innerHTML = `
      <img src="${story.image}" alt="${story.name}" class="card-image" />
      <div class="card-content">
        <h2>${story.name}</h2>
        <p><strong>Age:</strong> ${story.age}</p>
        <p><strong>Location:</strong> ${story.location}</p>
        <p>${story.excerpt}</p>
        <button class="read-more" data-index="${index}">Read More</button>
      </div>
    `;

    cardContainer.appendChild(card);
  });

  // Attach listeners to new buttons
  attachModalListeners();
}

// Attach modal open handlers
function attachModalListeners() {
  const readMoreButtons = document.querySelectorAll('.read-more');
  readMoreButtons.forEach(button => {
    button.addEventListener('click', (e) => {
      const index = e.target.getAttribute('data-index');
      const story = storiesData[index];
      if (story) {
        modalScroll.innerHTML = `
          <h2>${story.name}</h2>
          <p><strong>Age:</strong> ${story.age}</p>
          <p><strong>Location:</strong> ${story.location}</p>
          <img src="${story.image}" alt="${story.name}" class="modal-image" />
          <p>${story.content.replace(/\n/g, '<br><br>')}</p>
        `;
        modalOverlay.classList.add('active');
        document.body.classList.add('modal-open');
      }
    });
  });
}

// Close Modal
function closeModal() {
  modalOverlay.classList.remove('active');
  document.body.classList.remove('modal-open');
  modalScroll.innerHTML = '';
}

// Event listeners
closeBtn.addEventListener('click', closeModal);

modalOverlay.addEventListener('click', (e) => {
  if (e.target === modalOverlay) closeModal();
});

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeModal();
});
