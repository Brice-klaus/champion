document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('search-input');
  if (!input) return;

  const wrapper = input.closest('.search-wrapper');
  const dropdown = document.getElementById('search-dropdown');
  const suggestionsUrl = input.dataset.suggestionsUrl;

  let debounceTimer;
  let currentController = null;
  let activeIndex = -1;

  function closeDropdown() {
    dropdown.innerHTML = '';
    dropdown.classList.add('hidden');
    activeIndex = -1;
  }

  function renderLoading() {
    dropdown.innerHTML = '<div class="search-loading">Recherche...</div>';
    dropdown.classList.remove('hidden');
  }

  function iconFor(type) {
    if (type === 'produit') return 'ti-shopping-cart';
    if (type === 'recette') return 'ti-chef-hat';
    if (type === 'article') return 'ti-news';
    return 'ti-search';
  }

  function renderResults(data) {
    if (!data.resultats.length) {
      dropdown.innerHTML = `
        <div class="search-empty">Aucun résultat pour "${data.query}"</div>
      `;
      dropdown.classList.remove('hidden');
      return;
    }

    const items = data.resultats.map((r, i) => `
      <a href="${r.url}" class="search-result-item" data-index="${i}">
        <div class="search-result-thumb">
          ${r.image
            ? `<img src="${r.image}" alt="">`
            : `<i class="ti ${iconFor(r.type)}"></i>`}
        </div>
        <div class="search-result-text">
          <p class="search-result-titre">${r.titre}</p>
          <p class="search-result-sous">${r.sous_titre}${r.prix ? ' · ' + r.prix : ''}</p>
        </div>
      </a>
    `).join('');

    dropdown.innerHTML = `
      <div class="search-results-list">${items}</div>
      <a href="${data.url_recherche_complete}" class="search-see-all">
        Voir tous les résultats pour "${data.query}"
      </a>
    `;
    dropdown.classList.remove('hidden');
  }

  input.addEventListener('input', () => {
    const query = input.value.trim();
    clearTimeout(debounceTimer);

    if (query.length < 2) {
      closeDropdown();
      return;
    }

    debounceTimer = setTimeout(async () => {
      if (currentController) currentController.abort();
      currentController = new AbortController();

      renderLoading();

      try {
        const res = await fetch(`${suggestionsUrl}?q=${encodeURIComponent(query)}`, {
          signal: currentController.signal,
        });
        const data = await res.json();
        renderResults(data);
      } catch (err) {
        if (err.name !== 'AbortError') {
          dropdown.innerHTML = '<div class="search-empty">Erreur de recherche.</div>';
        }
      }
    }, 300);
  });

  // Navigation clavier
  input.addEventListener('keydown', (e) => {
    const items = dropdown.querySelectorAll('.search-result-item');
    if (!items.length) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      activeIndex = Math.min(activeIndex + 1, items.length - 1);
      items.forEach((el, i) => el.classList.toggle('is-active', i === activeIndex));
      items[activeIndex]?.scrollIntoView({ block: 'nearest' });
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      activeIndex = Math.max(activeIndex - 1, 0);
      items.forEach((el, i) => el.classList.toggle('is-active', i === activeIndex));
    } else if (e.key === 'Enter' && activeIndex >= 0) {
      e.preventDefault();
      items[activeIndex].click();
    } else if (e.key === 'Escape') {
      closeDropdown();
      input.blur();
    }
  });

  document.addEventListener('click', (e) => {
    if (!wrapper.contains(e.target)) closeDropdown();
  });
});