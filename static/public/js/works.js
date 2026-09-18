const worksGrid = document.querySelector("[data-works-grid]");
const siteHeader = document.querySelector(".site-header");

if (worksGrid && siteHeader) {
    const workCards = [
        ...worksGrid.querySelectorAll(".works-card"),
    ];

    function updateWorksGeometry() {
        if (!workCards.length) {
            return;
        }

        const headerHeight =
            siteHeader.getBoundingClientRect().height;

        const lastRowTop = Math.max(
            ...workCards.map((card) => card.offsetTop)
        );

        const lastRowCards = workCards.filter(
            (card) =>
                Math.abs(card.offsetTop - lastRowTop) < 1
        );

        const lastRowHeight = Math.max(
            ...lastRowCards.map(
                (card) =>
                    card.getBoundingClientRect().height
            )
        );

        const tailSpace = Math.max(
            0,
            window.innerHeight
                - headerHeight
                - lastRowHeight
        );

        worksGrid.style.setProperty(
            "--works-sticky-top",
            `${headerHeight}px`
        );

        worksGrid.style.setProperty(
            "--works-tail-space",
            `${tailSpace}px`
        );
    }

    updateWorksGeometry();

    window.addEventListener(
        "resize",
        updateWorksGeometry
    );

    if (document.fonts) {
        document.fonts.ready.then(
            updateWorksGeometry
        );
    }
}