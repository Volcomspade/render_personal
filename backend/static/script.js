document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("theme-toggle");
  toggle.onclick = () => {
    document.body.classList.toggle("dark");
    localStorage.theme = document.body.classList.contains("dark") ? "dark" : "light";
  };
  if (localStorage.theme === "dark") document.body.classList.add("dark");
});
