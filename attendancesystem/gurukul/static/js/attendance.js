// Attendance JS

function setStatus(studentId, status) {
    const select = document.getElementById('student_' + studentId);
    if (select) {
        select.value = status;
        highlight(select);
    }
}

function markAllPresent() {
    document.querySelectorAll('.attendance-select').forEach(s => {
        s.value = 'present';
        highlight(s);
    });
}

function markAllAbsent() {
    document.querySelectorAll('.attendance-select').forEach(s => {
        s.value = 'absent';
        highlight(s);
    });
}

function highlight(el) {
    const tr = el.closest('tr');
    tr.classList.remove('table-success', 'table-danger', 'table-warning');
    if (el.value === 'present') tr.classList.add('table-success');
    if (el.value === 'absent') tr.classList.add('table-danger');
    if (el.value === 'late') tr.classList.add('table-warning');
}

// Attach submit handler safely
var attendanceForm = document.getElementById('attendanceForm');
if (attendanceForm) {
    attendanceForm.addEventListener('submit', function(e) {
        e.preventDefault();
        var data = {};
        document.querySelectorAll('.attendance-select').forEach(function(s) {
            data[s.getAttribute('data-student-id')] = s.value;
        });
        document.getElementById('attendanceData').value = JSON.stringify(data);
        attendanceForm.submit();
    });
}

// Initialize highlighting on load
document.querySelectorAll('.attendance-select').forEach(function(s) {
    highlight(s);
    s.addEventListener('change', function() {
        highlight(s);
    });
});