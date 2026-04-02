document.addEventListener("DOMContentLoaded", function () {
  const navbar = document.querySelector(".navbar");
  const toggleButton = document.querySelector(".menu-toggle");
  const navLinks = document.querySelectorAll(".nav-links a");
  const sections = document.querySelectorAll(".page-section");

  // Show only the requested section and sync the active nav link.
  const showSection = function (sectionId) {
    const targetId = sectionId && document.getElementById(sectionId) ? sectionId : "overview";

    sections.forEach(function (section) {
      section.classList.toggle("active", section.id === targetId);
    });

    navLinks.forEach(function (link) {
      const isActive = link.getAttribute("href") === "#" + targetId;
      link.classList.toggle("active", isActive);
    });
  };

  if (navbar && toggleButton) {
    // Controls mobile menu expansion state.
    const setExpanded = function (isExpanded) {
      navbar.classList.toggle("nav-open", isExpanded);
      toggleButton.setAttribute("aria-expanded", String(isExpanded));
    };

    toggleButton.addEventListener("click", function () {
      setExpanded(!navbar.classList.contains("nav-open"));
    });

    navLinks.forEach(function (link) {
      link.addEventListener("click", function (event) {
        event.preventDefault();
        const sectionId = link.getAttribute("href").replace("#", "");
        showSection(sectionId);
        setExpanded(false);
        // Keep URL hash in sync without forcing a full page jump.
        if (window.location.hash !== link.getAttribute("href")) {
          window.history.replaceState(null, "", link.getAttribute("href"));
        }
      });
    });

    // Initial state supports direct hash links and defaults to overview.
    const initialSection = window.location.hash.replace("#", "") || "overview";
    showSection(initialSection);

    window.addEventListener("hashchange", function () {
      showSection(window.location.hash.replace("#", ""));
    });
  }
});

function showMessage(pageName) {
  alert("You are now on the " + pageName + " page.");
}
