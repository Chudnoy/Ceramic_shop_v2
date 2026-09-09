const story = document.querySelector(".work-story");
const storyDescription = story?.querySelector("[data-story-description]");
const storyToggle = story?.querySelector("[data-story-toggle]");

const storyToggleLabel = story?.querySelector("[data-story-toggle-label]");

if (story && storyDescription && storyToggle && storyToggleLabel) {
    story.classList.add("is-collapsible");

    const isOverflowing = storyDescription.scrollHeight > storyDescription.clientHeight;

    if (isOverflowing) {
        storyToggle.hidden = false;

        storyToggle.addEventListener("click", () => {
            const isExpanded = story.classList.toggle("is-expanded");

            storyToggle.setAttribute("aria-expanded", String(isExpanded));

            storyToggleLabel.textContent = isExpanded ? "Свернуть" : "Читать далее";
        });
    } else {
        story.classList.remove("is-collapsible");
    }
}


const workCarousel = document.querySelector("[data-work-carousel]");
const workCarouselTrack = workCarousel?.querySelector("[data-work-carousel-track]");
const workCarouselItems = workCarousel?.querySelectorAll("[data-work-carousel-item]");
const workCarouselControls = workCarousel?.querySelector("[data-work-carousel-controls]");
const workCarouselPrev = workCarousel?.querySelector("[data-work-carousel-prev]");
const workCarouselNext = workCarousel?.querySelector("[data-work-carousel-next]");

if (workCarousel && workCarouselTrack && workCarouselItems.length > 0) {
    let currentIndex = 0;

    const updateCarousel = () => {
        const firstItem = workCarouselItems[0];

        const visibleItems = window.matchMedia("(max-width: 640px)").matches ? 1 : 3;
        const maxIndex = Math.max(0, workCarouselItems.length - visibleItems);

        currentIndex = Math.min(currentIndex, maxIndex);

        const trackStyles = getComputedStyle(workCarouselTrack);
        const gap = parseFloat(trackStyles.columnGap) || 0;
        const step = firstItem.getBoundingClientRect().width + gap;

        workCarouselTrack.style.transform = `translateX(${-currentIndex * step}px)`;

        if (workCarouselControls) {
            workCarouselControls.hidden = maxIndex === 0;
        }

        if (workCarouselPrev) {
            workCarouselPrev.disabled = currentIndex === 0;
        }

        if (workCarouselNext) {
            workCarouselNext.disabled = currentIndex === maxIndex;
        }
    };

    if (workCarouselPrev && workCarouselNext) {
        workCarouselPrev.addEventListener("click", () => {
            currentIndex -= 1;
            updateCarousel();
        });

        workCarouselNext.addEventListener("click", () => {
            currentIndex += 1;
            updateCarousel();
        });
    }

    updateCarousel();

    window.addEventListener("resize", updateCarousel);
}