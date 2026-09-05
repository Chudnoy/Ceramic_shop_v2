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