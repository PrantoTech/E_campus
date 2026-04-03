function showPage(pageId, button) {
  const pages = document.querySelectorAll('.page');
  const navLinks = document.querySelectorAll('.nav-link');

  pages.forEach((page) => {
    page.classList.remove('active');
  });

  navLinks.forEach((link) => {
    link.classList.remove('active');
  });

  document.getElementById(pageId).classList.add('active');
  button.classList.add('active');
}

function getCookie(name) {
  const cookieValue = document.cookie
    .split('; ')
    .find((row) => row.startsWith(`${name}=`));
  return cookieValue ? decodeURIComponent(cookieValue.split('=')[1]) : '';
}

let activeStudentRow = null;

function openStudentEditModal(button) {
  const row = button.closest('tr');
  const modal = document.getElementById('student-edit-modal');
  const saveBtn = document.getElementById('student-modal-save-btn');
  if (!row || !modal || !saveBtn) {
    return;
  }

  activeStudentRow = row;
  saveBtn.setAttribute('data-update-url', button.getAttribute('data-update-url') || '');

  document.getElementById('student-modal-student-id').value = row.dataset.studentId || '';
  document.getElementById('student-modal-roll-no').value = row.dataset.rollNo || '';
  document.getElementById('student-modal-full-name').value = row.dataset.fullName || '';
  document.getElementById('student-modal-email').value = row.dataset.email || '';
  document.getElementById('student-modal-course').value = row.dataset.course || '';
  document.getElementById('student-modal-gender').value = row.dataset.gender || '';
  document.getElementById('student-modal-semester').value = row.dataset.semester || '';
  document.getElementById('student-modal-date-of-birth').value = row.dataset.dateOfBirth || '';
  document.getElementById('student-modal-mobile').value = row.dataset.mobile || '';
  document.getElementById('student-modal-overall-gpa').value = row.dataset.overallGpa || '';
  document.getElementById('student-modal-advisor-faculty-id').value = row.dataset.advisorFacultyId || '';
  document.getElementById('student-modal-guardian-name').value = row.dataset.guardianName || '';
  document.getElementById('student-modal-guardian-contact').value = row.dataset.guardianContact || '';
  document.getElementById('student-modal-address').value = row.dataset.address || '';

  modal.classList.add('open');
  modal.setAttribute('aria-hidden', 'false');
}

function closeStudentEditModal() {
  const modal = document.getElementById('student-edit-modal');
  if (!modal) {
    return;
  }

  modal.classList.remove('open');
  modal.setAttribute('aria-hidden', 'true');
  activeStudentRow = null;
}

async function saveStudentDetailsFromModal() {
  const saveBtn = document.getElementById('student-modal-save-btn');
  const statusEl = document.getElementById('student-update-message');
  const updateUrl = saveBtn ? saveBtn.getAttribute('data-update-url') : '';

  if (!activeStudentRow || !saveBtn || !statusEl || !updateUrl) {
    return;
  }

  const payload = new URLSearchParams();
  payload.append('student_id', (document.getElementById('student-modal-student-id').value || '').trim());
  payload.append('roll_no', (document.getElementById('student-modal-roll-no').value || '').trim());
  payload.append('full_name', (document.getElementById('student-modal-full-name').value || '').trim());
  payload.append('email', (document.getElementById('student-modal-email').value || '').trim());
  payload.append('course', (document.getElementById('student-modal-course').value || '').trim());
  payload.append('gender', (document.getElementById('student-modal-gender').value || '').trim());
  payload.append('semester', (document.getElementById('student-modal-semester').value || '').trim());
  payload.append('date_of_birth', (document.getElementById('student-modal-date-of-birth').value || '').trim());
  payload.append('mobile', (document.getElementById('student-modal-mobile').value || '').trim());
  payload.append('overall_gpa', (document.getElementById('student-modal-overall-gpa').value || '').trim());
  payload.append('advisor_faculty_id', (document.getElementById('student-modal-advisor-faculty-id').value || '').trim());
  payload.append('guardian_name', (document.getElementById('student-modal-guardian-name').value || '').trim());
  payload.append('guardian_contact', (document.getElementById('student-modal-guardian-contact').value || '').trim());
  payload.append('address', (document.getElementById('student-modal-address').value || '').trim());

  const originalLabel = saveBtn.textContent;
  saveBtn.disabled = true;
  saveBtn.textContent = 'Updating...';

  try {
    const response = await fetch(updateUrl, {
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
      const courseSelect = document.getElementById('student-modal-course');
      const courseLabel = courseSelect.options[courseSelect.selectedIndex]?.textContent || courseSelect.value;
      const advisorSelect = document.getElementById('student-modal-advisor-faculty-id');
      const advisorLabel = advisorSelect.value
        ? (advisorSelect.options[advisorSelect.selectedIndex]?.textContent || advisorSelect.value)
        : '-';

      activeStudentRow.dataset.studentId = document.getElementById('student-modal-student-id').value.trim();
      activeStudentRow.dataset.rollNo = document.getElementById('student-modal-roll-no').value.trim();
      activeStudentRow.dataset.fullName = document.getElementById('student-modal-full-name').value.trim();
      activeStudentRow.dataset.email = document.getElementById('student-modal-email').value.trim();
      activeStudentRow.dataset.course = document.getElementById('student-modal-course').value.trim();
      activeStudentRow.dataset.gender = document.getElementById('student-modal-gender').value.trim();
      activeStudentRow.dataset.semester = document.getElementById('student-modal-semester').value.trim();
      activeStudentRow.dataset.dateOfBirth = document.getElementById('student-modal-date-of-birth').value.trim();
      activeStudentRow.dataset.mobile = document.getElementById('student-modal-mobile').value.trim();
      activeStudentRow.dataset.overallGpa = document.getElementById('student-modal-overall-gpa').value.trim();
      activeStudentRow.dataset.advisorFacultyId = advisorSelect.value.trim();
      activeStudentRow.dataset.advisorName = advisorLabel === '-' ? '' : advisorLabel;
      activeStudentRow.dataset.guardianName = document.getElementById('student-modal-guardian-name').value.trim();
      activeStudentRow.dataset.guardianContact = document.getElementById('student-modal-guardian-contact').value.trim();
      activeStudentRow.dataset.address = document.getElementById('student-modal-address').value.trim();

      activeStudentRow.cells[0].textContent = activeStudentRow.dataset.rollNo || '-';
      activeStudentRow.cells[2].textContent = activeStudentRow.dataset.fullName || '-';
      activeStudentRow.cells[3].textContent = courseLabel || '-';
      activeStudentRow.cells[4].textContent = activeStudentRow.dataset.semester || '-';
      activeStudentRow.cells[5].textContent = activeStudentRow.dataset.mobile || '-';
      activeStudentRow.cells[6].textContent = activeStudentRow.dataset.overallGpa || '-';
      activeStudentRow.cells[7].textContent = advisorLabel;

      statusEl.textContent = data.message || 'Student details updated successfully.';
      statusEl.style.color = '#16a34a';
      closeStudentEditModal();
    } else {
      statusEl.textContent = data.message || 'Unable to update student details.';
      statusEl.style.color = '#dc2626';
    }
  } catch (_error) {
    statusEl.textContent = 'Unable to update student right now. Please try again.';
    statusEl.style.color = '#dc2626';
  } finally {
    saveBtn.disabled = false;
    saveBtn.textContent = originalLabel;
  }
}

async function saveStudentDetails(button) {
  const row = button.closest('tr');
  const updateUrl = button.getAttribute('data-update-url');
  const statusEl = document.getElementById('student-update-message');

  if (!row || !updateUrl) {
    return;
  }

  const payload = new URLSearchParams();
  row.querySelectorAll('[data-field]').forEach((element) => {
    payload.append(element.getAttribute('data-field'), element.value.trim());
  });

  const originalLabel = button.textContent;
  button.disabled = true;
  button.textContent = 'Saving...';

  try {
    const response = await fetch(updateUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-CSRFToken': getCookie('csrftoken'),
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: payload.toString(),
    });

    const data = await response.json();
    statusEl.textContent = data.message || 'Request completed.';
    statusEl.style.color = response.ok && data.success ? '#16a34a' : '#dc2626';
  } catch (_error) {
    statusEl.textContent = 'Unable to update student right now. Please try again.';
    statusEl.style.color = '#dc2626';
  } finally {
    button.disabled = false;
    button.textContent = originalLabel;
  }
}

async function saveFacultyDetails(button) {
  const row = button.closest('tr');
  const updateUrl = button.getAttribute('data-update-url');
  const statusEl = document.getElementById('faculty-update-message');

  if (!row || !updateUrl) {
    return;
  }

  const payload = new URLSearchParams();
  row.querySelectorAll('[data-faculty-field]').forEach((element) => {
    payload.append(element.getAttribute('data-faculty-field'), element.value.trim());
  });

  const originalLabel = button.textContent;
  button.disabled = true;
  button.textContent = 'Saving...';

  try {
    const response = await fetch(updateUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-CSRFToken': getCookie('csrftoken'),
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: payload.toString(),
    });

    const data = await response.json();
    statusEl.textContent = data.message || 'Request completed.';
    statusEl.style.color = response.ok && data.success ? '#16a34a' : '#dc2626';
  } catch (_error) {
    statusEl.textContent = 'Unable to update faculty right now. Please try again.';
    statusEl.style.color = '#dc2626';
  } finally {
    button.disabled = false;
    button.textContent = originalLabel;
  }
}

async function saveAttendance(button) {
  const row = button.closest('tr');
  const updateUrl = button.getAttribute('data-update-url');
  const statusEl = document.getElementById('attendance-update-message');
  const attendanceDateEl = document.getElementById('attendance-date');

  if (!row || !updateUrl || !attendanceDateEl) {
    return;
  }

  const attendanceDate = attendanceDateEl.value;
  if (!attendanceDate) {
    statusEl.textContent = 'Please select an attendance date.';
    statusEl.style.color = '#dc2626';
    return;
  }

  const payload = new URLSearchParams();
  row.querySelectorAll('[data-attendance-field]').forEach((element) => {
    payload.append(element.getAttribute('data-attendance-field'), element.value.trim());
  });
  payload.append('attendance_date', attendanceDate);

  const originalLabel = button.textContent;
  button.disabled = true;
  button.textContent = 'Saving...';

  try {
    const response = await fetch(updateUrl, {
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
      statusEl.textContent = `${data.student_id} marked ${data.status}. Average Attendance: ${data.average_attendance}%`;
      statusEl.style.color = '#16a34a';
    } else {
      statusEl.textContent = data.message || 'Unable to save attendance.';
      statusEl.style.color = '#dc2626';
    }
  } catch (_error) {
    statusEl.textContent = 'Unable to save attendance right now. Please try again.';
    statusEl.style.color = '#dc2626';
  } finally {
    button.disabled = false;
    button.textContent = originalLabel;
  }
}

async function submitAssignmentForm() {
  const statusEl = document.getElementById('assignment-update-message');
  const listBody = document.getElementById('assignment-list-body');
  if (!statusEl || !listBody) {
    return;
  }

  const createUrl = listBody.getAttribute('data-create-url');
  const title = (document.getElementById('assignment-title')?.value || '').trim();
  const course = (document.getElementById('assignment-course')?.value || '').trim();
  const semester = (document.getElementById('assignment-semester')?.value || '').trim();
  const dueDate = (document.getElementById('assignment-due-date')?.value || '').trim();
  const description = (document.getElementById('assignment-description')?.value || '').trim();

  if (!title || !course || !semester || !dueDate) {
    statusEl.textContent = 'Please fill title, course, semester and due date.';
    statusEl.style.color = '#dc2626';
    return;
  }

  const payload = new URLSearchParams();
  payload.append('title', title);
  payload.append('course', course);
  payload.append('semester', semester);
  payload.append('due_date', dueDate);
  payload.append('description', description);

  try {
    const response = await fetch(createUrl, {
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
      const assignment = data.assignment;
      const formattedDate = assignment.due_date;
      const emptyRow = listBody.querySelector('td[colspan="6"], td[colspan="5"]')?.closest('tr');
      if (emptyRow) {
        emptyRow.remove();
      }

      const newRow = document.createElement('tr');
      newRow.setAttribute('data-assignment-id', assignment.id || '');
      newRow.setAttribute('data-delete-url', listBody.getAttribute('data-delete-url') || '');
      newRow.innerHTML = `
        <td>${assignment.title}</td>
        <td>${assignment.course}</td>
        <td>${assignment.semester}</td>
        <td>${formattedDate}</td>
        <td>${assignment.description || '-'}</td>
        <td><button class="dark-btn" type="button" onclick="deleteAssignment(this)">Delete</button></td>
      `;
      listBody.prepend(newRow);

      document.getElementById('assignment-title').value = '';
      document.getElementById('assignment-course').value = '';
      document.getElementById('assignment-semester').value = '';
      document.getElementById('assignment-due-date').value = '';
      document.getElementById('assignment-description').value = '';

      statusEl.textContent = data.message || 'Assignment posted successfully.';
      statusEl.style.color = '#16a34a';
    } else {
      statusEl.textContent = data.message || 'Unable to post assignment.';
      statusEl.style.color = '#dc2626';
    }
  } catch (_error) {
    statusEl.textContent = 'Unable to post assignment right now. Please try again.';
    statusEl.style.color = '#dc2626';
  }
}

async function submitAnnouncementForm() {
  const statusEl = document.getElementById('announcement-update-message');
  const submitBtn = document.getElementById('announcement-submit-btn');
  if (!statusEl || !submitBtn) {
    return;
  }

  const createUrl = submitBtn.getAttribute('data-create-url');
  const title = (document.getElementById('announcement-title')?.value || '').trim();
  const eventType = (document.getElementById('announcement-type')?.value || '').trim();
  const eventDate = (document.getElementById('announcement-date')?.value || '').trim();
  const venue = (document.getElementById('announcement-venue')?.value || '').trim();
  const description = (document.getElementById('announcement-description')?.value || '').trim();

  if (!title || !eventType || !eventDate) {
    statusEl.textContent = 'Please fill title, category and date.';
    statusEl.style.color = '#dc2626';
    return;
  }

  const payload = new URLSearchParams();
  payload.append('title', title);
  payload.append('event_type', eventType);
  payload.append('event_date', eventDate);
  payload.append('venue', venue);
  payload.append('description', description);

  const originalLabel = submitBtn.textContent;
  submitBtn.disabled = true;
  submitBtn.textContent = 'Posting...';

  try {
    const response = await fetch(createUrl, {
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
      statusEl.textContent = data.message || 'Announcement posted successfully.';
      statusEl.style.color = '#16a34a';
      document.getElementById('announcement-title').value = '';
      document.getElementById('announcement-date').value = '';
      document.getElementById('announcement-venue').value = '';
      document.getElementById('announcement-description').value = '';
    } else {
      statusEl.textContent = data.message || 'Unable to post announcement.';
      statusEl.style.color = '#dc2626';
    }
  } catch (_error) {
    statusEl.textContent = 'Unable to post announcement right now. Please try again.';
    statusEl.style.color = '#dc2626';
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = originalLabel;
  }
}

async function reviewAssignmentSubmission(button) {
  const row = button.closest('tr');
  const statusEl = document.getElementById('assignment-review-message');
  const reviewUrl = button.getAttribute('data-review-url');
  const submissionId = button.getAttribute('data-submission-id');

  if (!row || !statusEl || !reviewUrl || !submissionId) {
    return;
  }

  const marksInput = row.querySelector('[data-review-field="marks"]');
  const feedbackInput = row.querySelector('[data-review-field="feedback"]');

  const payload = new URLSearchParams();
  payload.append('submission_id', submissionId);
  payload.append('marks', (marksInput?.value || '').trim());
  payload.append('feedback', (feedbackInput?.value || '').trim());

  const originalLabel = button.textContent;
  button.disabled = true;
  button.textContent = 'Saving...';

  try {
    const response = await fetch(reviewUrl, {
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
      row.cells[7].textContent = data.review.status;
      statusEl.textContent = data.message || 'Review saved.';
      statusEl.style.color = '#16a34a';
    } else {
      statusEl.textContent = data.message || 'Unable to save review.';
      statusEl.style.color = '#dc2626';
    }
  } catch (_error) {
    statusEl.textContent = 'Unable to save review right now. Please try again.';
    statusEl.style.color = '#dc2626';
  } finally {
    button.disabled = false;
    button.textContent = originalLabel;
  }
}

async function deleteAssignment(button) {
  const row = button.closest('tr');
  const listBody = document.getElementById('assignment-list-body');
  const statusEl = document.getElementById('assignment-update-message');
  if (!row || !listBody || !statusEl) {
    return;
  }

  const deleteUrl = row.getAttribute('data-delete-url') || listBody.getAttribute('data-delete-url') || '';
  const assignmentId = row.getAttribute('data-assignment-id') || '';
  if (!deleteUrl || !assignmentId) {
    return;
  }

  const payload = new URLSearchParams();
  payload.append('assignment_id', assignmentId);

  const originalLabel = button.textContent;
  button.disabled = true;
  button.textContent = 'Deleting...';

  try {
    const response = await fetch(deleteUrl, {
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
      row.remove();
      if (!listBody.querySelector('tr')) {
        const emptyRow = document.createElement('tr');
        emptyRow.innerHTML = '<td colspan="6">No assignments posted yet.</td>';
        listBody.appendChild(emptyRow);
      }
      statusEl.textContent = data.message || 'Assignment deleted successfully.';
      statusEl.style.color = '#16a34a';
    } else {
      statusEl.textContent = data.message || 'Unable to delete assignment.';
      statusEl.style.color = '#dc2626';
    }
  } catch (_error) {
    statusEl.textContent = 'Unable to delete assignment right now. Please try again.';
    statusEl.style.color = '#dc2626';
  } finally {
    button.disabled = false;
    button.textContent = originalLabel;
  }
}

async function deleteAnnouncement(button) {
  const card = button.closest('[data-announcement-id]');
  const statusEl = document.getElementById('announcement-update-message');
  if (!card || !statusEl) {
    return;
  }

  const deleteUrl = card.getAttribute('data-delete-url') || '';
  const announcementId = card.getAttribute('data-announcement-id') || '';
  if (!deleteUrl || !announcementId) {
    return;
  }

  const payload = new URLSearchParams();
  payload.append('announcement_id', announcementId);

  const originalLabel = button.textContent;
  button.disabled = true;
  button.textContent = 'Deleting...';

  try {
    const response = await fetch(deleteUrl, {
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
      card.remove();
      statusEl.textContent = data.message || 'Announcement deleted successfully.';
      statusEl.style.color = '#16a34a';
    } else {
      statusEl.textContent = data.message || 'Unable to delete announcement.';
      statusEl.style.color = '#dc2626';
    }
  } catch (_error) {
    statusEl.textContent = 'Unable to delete announcement right now. Please try again.';
    statusEl.style.color = '#dc2626';
  } finally {
    button.disabled = false;
    button.textContent = originalLabel;
  }
}

