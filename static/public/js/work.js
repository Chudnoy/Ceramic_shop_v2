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
const workCarouselPrev = workCarousel?.querySelector("[data-work-carousel-prev]");
const workCarouselNext = workCarousel?.querySelector("[data-work-carousel-next]");

if (
    workCarousel &&
    workCarouselTrack &&
    workCarouselItems &&
    workCarouselPrev &&
    workCarouselNext
) {
    let currentIndex = 0;

    const updateCarousel = () => {
        const visibleItems = window.matchMedia("(max-width: 640px)").matches ? 1 : 3;
        const maxIndex = workCarouselItems.length - visibleItems;
        
        if (currentIndex > maxIndex) {
            currentIndex = maxIndex
        }
        const step = workCarouselItems[1].offsetLeft - workCarouselItems[0].offsetLeft;

        workCarouselTrack.style.transform = `translateX(${-currentIndex * step}px)`;

        workCarouselPrev.disabled = currentIndex === 0;
        workCarouselNext.disabled = currentIndex === maxIndex;
    };

    workCarouselPrev.addEventListener("click", () => {
        currentIndex -= 1;
        updateCarousel();
    });

    workCarouselNext.addEventListener("click", () => {
        currentIndex += 1;
        updateCarousel();
    });

    updateCarousel();

    window.addEventListener('resize', updateCarousel)
}