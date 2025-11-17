(function () {
    'use strict';

    function initGamesSearch() {
        const input = document.querySelector('[data-games-search-input]');
        const status = document.querySelector('[data-games-search-status]');
        const ratingCheckboxes = Array.from(document.querySelectorAll('[data-rating-filter-checkbox]'));
        const cards = Array.from(document.querySelectorAll('[data-game-card]'));

        if (!input || !status || cards.length === 0) {
            return;
        }

        const total = cards.length;

        const update = () => {
            const query = input.value.trim().toLowerCase();
            const selectedRatings = ratingCheckboxes
                .filter((checkbox) => checkbox.checked)
                .map((checkbox) => parseInt(checkbox.value, 10))
                .filter((value) => Number.isFinite(value));
            const hasRatingFilter = selectedRatings.length > 0;
            let visible = 0;

            cards.forEach((card) => {
                const haystack = card.dataset.searchText || card.textContent.toLowerCase();
                const matchesQuery = !query || haystack.includes(query);
                const cardRating = Number(card.dataset.rating);
                const matchesRating = !hasRatingFilter
                    || (Number.isFinite(cardRating) && selectedRatings.includes(cardRating));
                const matches = matchesQuery && matchesRating;
                card.hidden = !matches;
                if (matches) {
                    visible += 1;
                }
            });

            const suffixParts = [];
            if (query) {
                suffixParts.push(`"${query}"`);
            }
            if (hasRatingFilter) {
                const formattedRatings = selectedRatings.sort((a, b) => b - a).map((rating) => `${rating}/10`);
                suffixParts.push(`ratings ${formattedRatings.join(', ')}`);
            }
            const suffix = suffixParts.length ? ` for ${suffixParts.join(' & ')}` : '';
            status.textContent = `Showing ${visible} of ${total} games${suffix}`;
        };

        input.addEventListener('input', update);
        ratingCheckboxes.forEach((checkbox) => {
            checkbox.addEventListener('change', update);
        });

        update();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initGamesSearch, { once: true });
    } else {
        initGamesSearch();
    }
})();
