function payFees() {
  alert("Redirecting to payment gateway...");
}

function addTask() {
  let task = prompt("Enter new task:");
  if (task) {
    let li = document.createElement("li");
    li.textContent = task;
    document.getElementById("taskList").appendChild(li);
  }
}

function calculateAttendance() {
  let attended = parseInt(document.querySelector("#attendance p:nth-child(2)").textContent.replace(/\D/g, ""));
  let total = parseInt(document.querySelector("#attendance p:nth-child(3)").textContent.replace(/\D/g, ""));
  let percent = ((attended / total) * 100).toFixed(2);
  document.getElementById("attendancePercent").textContent = percent;
}

document.addEventListener("DOMContentLoaded", calculateAttendance);