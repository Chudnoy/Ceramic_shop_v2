const navigation = document.querySelector(".site-nav");
const toggle = document.querySelector(".site-nav__toggle");

if (navigation && toggle) {
    toggle.addEventListener("click", () => {
        const isOpen = navigation.classList.toggle("is-open");

        toggle.setAttribute("aria-expanded", String("is-open"));
    });
}