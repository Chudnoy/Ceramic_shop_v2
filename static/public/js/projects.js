const projectsTrack =
    document.querySelector("[data-projects-track]");

if (projectsTrack) {
    function getWheelDelta(event) {
        let delta = event.deltaY;

        if (event.deltaMode === WheelEvent.DOM_DELTA_LINE) {
            delta *= 16;
        }

        if (event.deltaMode === WheelEvent.DOM_DELTA_PAGE) {
            delta *= window.innerHeight;
        }

        return delta;
    }

    projectsTrack.addEventListener(
        "wheel",
        (event) => {
            if (event.ctrlKey) {
                return;
            }

            /*
             * Если устройство уже посылает настоящий
             * горизонтальный жест, браузер сам умеет
             * прокручивать track по X.
             */
            if (
                Math.abs(event.deltaX)
                > Math.abs(event.deltaY)
            ) {
                return;
            }

            const maxScrollLeft =
                projectsTrack.scrollWidth
                - projectsTrack.clientWidth;

            if (maxScrollLeft <= 0) {
                return;
            }

            const delta = getWheelDelta(event);

            event.preventDefault();

            projectsTrack.scrollLeft += delta;
        },
        {
            passive: false,
        }
    );
}