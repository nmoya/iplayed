(function () {
    'use strict';

    function initGamesSearch() {
        const input = document.querySelector('[data-games-search-input]');
        const status = document.querySelector('[data-games-search-status]');
        const cards = Array.from(document.querySelectorAll('[data-game-card]'));

        if (!input || !status || cards.length === 0) {
            return;
        }

        const total = cards.length;

        const update = () => {
            const query = input.value.trim().toLowerCase();
            let visible = 0;

            cards.forEach((card) => {
                const haystack = card.dataset.searchText || card.textContent.toLowerCase();
                const matches = !query || haystack.includes(query);
                card.hidden = !matches;
                if (matches) {
                    visible += 1;
                }
            });

            const suffix = query ? ` for "${query}"` : '';
            status.textContent = `Showing ${visible} of ${total} games${suffix}`;
        };

        input.addEventListener('input', update);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initGamesSearch, { once: true });
    } else {
        initGamesSearch();
    }
})();
