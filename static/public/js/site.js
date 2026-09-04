const header = document.querySelector("[data-nav]");
const toggle = header?.querySelector(".site-header__toggle");
const navigation = header?.querySelector(".site-header__nav");

if (header && toggle && navigation) {
    toggle.addEventListener("click", () => {
        const isOpen = header.classList.toggle("is-open");

        toggle.setAttribute(
            "aria-expanded",
            String(isOpen)
        );
    });

    navigation
        .querySelectorAll("a")
        .forEach((link) => {
            link.addEventListener("click", () => {
                header.classList.remove("is-open");

                toggle.setAttribute(
                    "aria-expanded",
                    "false"
                );
            });
        });

    header.classList.add("is-enhanced");
}