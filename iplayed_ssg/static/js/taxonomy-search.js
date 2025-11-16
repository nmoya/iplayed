(function () {
    'use strict';

    function initTaxonomySearch() {
        const input = document.querySelector('[data-taxonomy-search]');
        const status = document.querySelector('[data-taxonomy-search-status]');
        const cards = Array.from(document.querySelectorAll('[data-taxonomy-card]'));

        if (!input || !status || cards.length === 0) {
            return;
        }

        const total = cards.length;
        const label = status.dataset.taxonomyLabel || 'items';

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
            status.textContent = `Showing ${visible} of ${total} ${label}${suffix}`;
        };

        input.addEventListener('input', update);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTaxonomySearch, { once: true });
    } else {
        initTaxonomySearch();
    }
})();
