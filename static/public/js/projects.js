const projectsTrack =
    document.querySelector("[data-projects-track]");

if (projectsTrack) {
    const snapIdleDelayMs = 260;
    const snapAnimationDurationMs = 600;

    const reducedMotionQuery = window.matchMedia(
        "(prefers-reduced-motion: reduce)"
    );

    let snapTimerId = null;
    let animationFrameId = null;
    let activeWheelAxis = null;
    let lastWheelEventTime = 0;
    let isPointerDown = false;


    function stopSnap() {
        clearTimeout(snapTimerId);
        cancelAnimationFrame(animationFrameId);

        animationFrameId = null;
    }


    function scheduleSnap() {
        clearTimeout(snapTimerId);

        if (
            isPointerDown
            || animationFrameId !== null
        ) {
            return;
        }

        snapTimerId = setTimeout(
            snapToNearest,
            snapIdleDelayMs
        );
    }


    function snapToNearest() {
        const startScrollLeft =
            projectsTrack.scrollLeft;

        const maxScrollLeft = Math.max(
            0,
            projectsTrack.scrollWidth
                - projectsTrack.clientWidth
        );

        const trackViewportLeft =
            projectsTrack
                .getBoundingClientRect()
                .left
            + projectsTrack.clientLeft;

        let targetScrollLeft = 0;
        let nearestSnapDistance = Infinity;


        for (
            const slide
            of projectsTrack.children
        ) {
            const slideScrollLeft =
                startScrollLeft
                + slide
                    .getBoundingClientRect()
                    .left
                - trackViewportLeft;

            const snapPosition = Math.max(
                0,
                Math.min(
                    slideScrollLeft,
                    maxScrollLeft
                )
            );

            const candidateDistance =
                Math.abs(
                    snapPosition
                    - startScrollLeft
                );

            if (
                candidateDistance
                < nearestSnapDistance
            ) {
                nearestSnapDistance =
                    candidateDistance;

                targetScrollLeft =
                    snapPosition;
            }
        }


        const travelDistance =
            targetScrollLeft
            - startScrollLeft;

        if (
            Math.abs(travelDistance) < 1
        ) {
            return;
        }


        if (reducedMotionQuery.matches) {
            projectsTrack.scrollLeft =
                targetScrollLeft;

            return;
        }


        const animationStartTime =
            performance.now();


        function animate(frameTime) {
            const timeProgress = Math.min(
                (
                    frameTime
                    - animationStartTime
                )
                / snapAnimationDurationMs,
                1
            );

            // Превращаем линейный прогресс
            // времени в мягкий разгон
            // и мягкую остановку.
            const easedProgress =
                (
                    1
                    - Math.cos(
                        Math.PI
                        * timeProgress
                    )
                )
                / 2;

            projectsTrack.scrollLeft =
                startScrollLeft
                + travelDistance
                * easedProgress;

            if (timeProgress < 1) {
                animationFrameId =
                    requestAnimationFrame(
                        animate
                    );
            } else {
                animationFrameId = null;
            }
        }


        animationFrameId =
            requestAnimationFrame(
                animate
            );
    }


    projectsTrack.addEventListener(
        "wheel",
        (event) => {
            stopSnap();

            if (event.ctrlKey) {
                activeWheelAxis = null;
                return;
            }


            const maxScrollLeft =
                projectsTrack.scrollWidth
                - projectsTrack.clientWidth;

            if (maxScrollLeft <= 0) {
                return;
            }


            const currentWheelTime =
                performance.now();

            // Выбираем главную ось один раз
            // в начале нового жеста.
            if (
                activeWheelAxis === null
                || currentWheelTime
                    - lastWheelEventTime
                    > snapIdleDelayMs
            ) {
                activeWheelAxis =
                    Math.abs(event.deltaX)
                    > Math.abs(event.deltaY)
                        ? "x"
                        : "y";
            }

            lastWheelEventTime =
                currentWheelTime;


            let scrollDelta =
                activeWheelAxis === "x"
                    ? event.deltaX
                    : event.deltaY;


            if (
                event.deltaMode
                === WheelEvent.DOM_DELTA_LINE
            ) {
                scrollDelta *= 16;
            } else if (
                event.deltaMode
                === WheelEvent.DOM_DELTA_PAGE
            ) {
                scrollDelta *=
                    projectsTrack.clientWidth;
            }


            // Не добавляем собственное движение,
            // если браузер не позволяет отменить
            // стандартное поведение события.
            if (!event.cancelable) {
                scheduleSnap();
                return;
            }

            event.preventDefault();


            projectsTrack.scrollLeft =
                Math.max(
                    0,
                    Math.min(
                        projectsTrack.scrollLeft
                            + scrollDelta,
                        maxScrollLeft
                    )
                );

            // Даже маленькие события инерции
            // откладывают доводчик.
            scheduleSnap();
        },
        {
            passive: false,
        }
    );


    projectsTrack.addEventListener(
        "scroll",
        () => {
            scheduleSnap();
        },
        {
            passive: true,
        }
    );


    projectsTrack.addEventListener(
        "pointerdown",
        () => {
            isPointerDown = true;
            activeWheelAxis = null;

            stopSnap();
        }
    );


    function releasePointer() {
        if (!isPointerDown) {
            return;
        }

        isPointerDown = false;

        scheduleSnap();
    }


    window.addEventListener(
        "pointerup",
        releasePointer
    );

    window.addEventListener(
        "pointercancel",
        releasePointer
    );


    projectsTrack.addEventListener(
        "keydown",
        (event) => {
            const scrollKeys = [
                "ArrowLeft",
                "ArrowRight",
                "ArrowUp",
                "ArrowDown",
                "PageUp",
                "PageDown",
                "Home",
                "End",
                " ",
            ];

            if (
                scrollKeys.includes(event.key)
            ) {
                stopSnap();
                scheduleSnap();
            }
        }
    );


    window.addEventListener(
        "resize",
        () => {
            stopSnap();

            activeWheelAxis = null;

            scheduleSnap();
        }
    );
}