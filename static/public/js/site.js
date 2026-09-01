const navigation = document.querySelector("[data-nav]");
const toggle = navigation?.querySelector(".home-header__toggle");

if (navigation && toggle) {
    toggle.addEventListener("click", () => {
        const isOpen = navigation.classList.toggle("is-open");

        toggle.setAttribute(
            "aria-expanded",
            String(isOpen)
        );
    });

    navigation
        .querySelectorAll(".home-header__nav a")
        .forEach((link) => {
            link.addEventListener('click', () => {
                navigation.classList.remove("is-open");

                toggle.setAttribute(
                    "aria-expanded",
                    "false",
                );
            });
        });
};