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

function getCookie(name) {
  const cookieValue = document.cookie
    .split('; ')
    .find(function (row) {
      return row.startsWith(name + '=');
    });
  return cookieValue ? decodeURIComponent(cookieValue.split('=')[1]) : '';
}

async function submitStudentAssignment(button) {
  const card = button.closest('.event-card');
  const statusEl = document.getElementById('student-assignment-message');
  const submitUrl = statusEl ? statusEl.getAttribute('data-submit-url') : '';
  const assignmentId = button.getAttribute('data-assignment-id');
  const textArea = card ? card.querySelector('[data-assignment-field="submission_text"]') : null;

  if (!statusEl || !submitUrl || !assignmentId || !textArea) {
    return;
  }

  const submissionText = (textArea.value || '').trim();
  if (!submissionText) {
    statusEl.textContent = 'Please write submission text before submit.';
    statusEl.style.color = '#dc2626';
    return;
  }

  const payload = new URLSearchParams();
  payload.append('assignment_id', assignmentId);
  payload.append('submission_text', submissionText);

  const originalLabel = button.textContent;
  button.disabled = true;
  button.textContent = 'Submitting...';

  try {
    const response = await fetch(submitUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-CSRFToken': getCookie('csrftoken'),
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: payload.toString(),
    });

    const data = await response.json();
    if (response.ok && data.success) {
      statusEl.textContent = data.message + ' (' + data.submission.submitted_at + ')';
      statusEl.style.color = '#16a34a';
      button.textContent = 'Resubmit';

      const statusLine = Array.from(card.querySelectorAll('p')).find(function (node) {
        return node.textContent.trim().startsWith('Status:');
      });
      if (statusLine) {
        statusLine.innerHTML = 'Status: <strong>Submitted</strong>';
      }
    } else {
      statusEl.textContent = data.message || 'Unable to submit assignment.';
      statusEl.style.color = '#dc2626';
      button.textContent = originalLabel;
    }
  } catch (_error) {
    statusEl.textContent = 'Unable to submit assignment right now. Please try again.';
    statusEl.style.color = '#dc2626';
    button.textContent = originalLabel;
  } finally {
    button.disabled = false;
  }
}
