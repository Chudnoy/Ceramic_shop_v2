const projectsTrack = document.querySelector("[data-projects-track]");

if (projectsTrack) {
    const snapDelay = 260;
    const snapDuration = 600;

    const reducedMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)"
    );

    let snapTimer = null;
    let animationId = null;
    let wheelAxis = null;
    let lastWheelTime = 0;
    let pointerDown = false;

    function stopSnap() {
        clearTimeout(snapTimer);
        cancelAnimationFrame(animationId);
        animationId = null;
    }

    function scheduleSnap() {
        clearTimeout(snapTimer);

        if (pointerDown || animationId !== null) {
            return;
        }

        snapTimer = setTimeout(snapToNearest, snapDelay);
    }

    function snapToNearest() {
        const start = projectsTrack.scrollLeft;
        const maxScroll = Math.max(
            0,
            projectsTrack.scrollWidth - projectsTrack.clientWidth
        );

        const trackLeft =
            projectsTrack.getBoundingClientRect().left
            + projectsTrack.clientLeft;

        let target = 0;
        let shortestDistance = Infinity;

        for (const card of projectsTrack.children) {
            const cardLeft =
                start + card.getBoundingClientRect().left - trackLeft;

            const position = Math.max(
                0,
                Math.min(cardLeft, maxScroll)
            );

            const distance = Math.abs(position - start);

            if (distance < shortestDistance) {
                shortestDistance = distance;
                target = position;
            }
        }

        const distance = target - start;

        if (Math.abs(distance) < 1) {
            return;
        }

        if (reducedMotion.matches) {
            projectsTrack.scrollLeft = target;
            return;
        }

        const startTime = performance.now();

        function animate(time) {
            const progress = Math.min(
                (time - startTime) / snapDuration,
                1
            );

            // Мягкий разгон и мягкая остановка.
            const eased = (1 - Math.cos(Math.PI * progress)) / 2;

            projectsTrack.scrollLeft = start + distance * eased;

            if (progress < 1) {
                animationId = requestAnimationFrame(animate);
            } else {
                animationId = null;
            }
        }

        animationId = requestAnimationFrame(animate);
    }

    projectsTrack.addEventListener("wheel", (event) => {
        stopSnap();

        if (event.ctrlKey) {
            wheelAxis = null;
            return;
        }

        const maxScroll =
                projectsTrack.scrollWidth - projectsTrack.clientWidth;

        if (maxScroll <= 0) {
            return;
        }

        const now = performance.now();

        // Выбираем ось один раз в начале жеста.
        if (wheelAxis === null || now - lastWheelTime > snapDelay) {
            wheelAxis =
                Math.abs(event.deltaX) > Math.abs(event.deltaY)
                    ? "x"
                    : "y";
        }

        lastWheelTime = now;

        let delta =
                wheelAxis === "x" ? event.deltaX : event.deltaY;

        if (event.deltaMode === WheelEvent.DOM_DELTA_LINE) {
            delta *= 16;
        } else if (event.deltaMode === WheelEvent.DOM_DELTA_PAGE) {
            delta *= projectsTrack.clientWidth;
        }

        // Не добавляем своё движение, если браузер нельзя остановить.
        if (!event.cancelable) {
            scheduleSnap();
            return;
        }

        event.preventDefault();

        projectsTrack.scrollLeft = Math.max(
            0,
            Math.min(projectsTrack.scrollLeft + delta, maxScroll)
        );

        // Даже маленькие события инерции откладывают доводчик.
        scheduleSnap();
    }, { passive: false });

    projectsTrack.addEventListener("scroll", () => {
        scheduleSnap();
    }, { passive: true });

    projectsTrack.addEventListener("pointerdown", () => {
        pointerDown = true;
        wheelAxis = null;
        stopSnap();
    });

    function releasePointer() {
        if (!pointerDown) {
            return;
        }

        pointerDown = false;
        scheduleSnap();
    }

    window.addEventListener("pointerup", releasePointer);
    window.addEventListener("pointercancel", releasePointer);

    projectsTrack.addEventListener("keydown", (event) => {
        const scrollKeys = [
            "ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown",
            "PageUp", "PageDown", "Home", "End", " "
        ];

        if (scrollKeys.includes(event.key)) {
            stopSnap();
            scheduleSnap();
        }
    });

    window.addEventListener("resize", () => {
        stopSnap();
        wheelAxis = null;
        scheduleSnap();
    });
}