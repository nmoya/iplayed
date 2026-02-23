(function () {
    'use strict';

    function initGamesSearch() {
        const input = document.querySelector('[data-games-search-input]');
        const status = document.querySelector('[data-games-search-status]');
        const ratingChips = Array.from(document.querySelectorAll('[data-rating-chip]'));
        const cards = Array.from(document.querySelectorAll('[data-game-card]'));

        if (!input || !status || cards.length === 0) {
            return;
        }

        const total = cards.length;

        const update = () => {
            const query = input.value.trim().toLowerCase();
            const activeChip = ratingChips.find((chip) => chip.classList.contains('is-active'));
            const value = activeChip ? activeChip.value : '';
            const isUnrated = value === 'unrated';
            const exactRating = !isUnrated && value !== '' ? parseInt(value, 10) : NaN;
            const hasRatingFilter = value !== '';
            let visible = 0;

            cards.forEach((card) => {
                const haystack = card.dataset.searchText || card.textContent.toLowerCase();
                const matchesQuery = !query || haystack.includes(query);
                const cardRating = Number(card.dataset.rating);
                const hasCardRating = card.dataset.rating.length > 0;
                const matchesRating = !hasRatingFilter
                    || (isUnrated && !hasCardRating)
                    || (!isUnrated && hasCardRating && cardRating === exactRating);
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
                suffixParts.push(isUnrated ? 'unrated' : `rating ${exactRating}/10`);
            }
            const suffix = suffixParts.length ? ` for ${suffixParts.join(' & ')}` : '';
            status.textContent = `Showing ${visible} of ${total} games${suffix}`;
        };

        input.addEventListener('input', update);
        ratingChips.forEach((chip) => {
            chip.addEventListener('click', () => {
                ratingChips.forEach((c) => c.classList.remove('is-active'));
                chip.classList.add('is-active');
                update();
            });
        });

        update();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initGamesSearch, { once: true });
    } else {
        initGamesSearch();
    }
})();
