document.documentElement.classList.add("js");
const navigation = document.querySelector("[data-nav]");
const toggle = navigation?.querySelector(".home-nav__toggle");
if (navigation && toggle) {
  toggle.addEventListener("click", () => { const open = navigation.classList.toggle("is-open"); toggle.setAttribute("aria-expanded", String(open)); });
  navigation.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => { navigation.classList.remove("is-open"); toggle.setAttribute("aria-expanded", "false"); }));
}
