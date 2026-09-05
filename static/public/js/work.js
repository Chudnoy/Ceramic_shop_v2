const story = document.querySelector(".work-story");
const storyContent = document.querySelector("[data-story-content]");
const storyDescription = document.querySelector("[data-story-description]");
const storyToggle = document.querySelector("[data-story-toggle]");
const storyToggleLabel = document.querySelector("[data-story-toggle-label]");

if (story && storyContent && storyDescription && storyToggle && storyToggleLabel) {
    storyContent.classList.add("is-collapsible");

    const isOverflowing = storyDescription.scrollHeight > storyDescription.clientHeight;

    if (isOverflowing) {
        storyToggle.hidden = false;

        storyToggle.addEventListener("click", () => {
            const isExpanded = storyContent.classList.toggle("is-expanded");

            story.classList.toggle("is-expanded", isExpanded);
            storyToggle.setAttribute("aria-expanded", String(isExpanded));
            storyToggleLabel.textContent = isExpanded ? "Свернуть" : "Читать далее";
        });
    } else {
        storyContent.classList.remove("is-collapsible");
    }
}