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