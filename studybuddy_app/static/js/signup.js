document.getElementById('signupForm').addEventListener('submit', function(e) {
    const form = this;
    const username = document.getElementById('username');
    const email = document.getElementById('email');
    const password1 = document.getElementById('password1');
    const password2 = document.getElementById('password2');

    let isValid = true;
    console.log("📤 Form submitted");

    // Reset styles
    document.querySelectorAll('.form-control').forEach(input => input.classList.remove('is-invalid'));
    document.querySelectorAll('.invalid-feedback').forEach(f => f.style.display = 'none');

    // Username
    if (!username.value.trim() || username.value.length < 3) {
        showFieldError(username, 'Username must be at least 3 characters long');
        isValid = false;
    }

    // Email
    const emailRegex = /^s\d{7}@bi\.no$/;
    if (!email.value.trim() || !emailRegex.test(email.value)) {
        showFieldError(email, 'Only valid BI emails allowed (e.g., s1234567@bi.no)');
        isValid = false;
    }

    // Password
    if (!password1.value || password1.value.length < 8) {
        showFieldError(password1, 'Password must be at least 8 characters long');
        isValid = false;
    }

    // Confirm Password
    if (!password2.value || password1.value !== password2.value) {
        showFieldError(password2, 'Passwords do not match');
        isValid = false;
    }

    console.log("✅ Validation result:", isValid);

    // 🛑 Prevent submission if invalid
    if (!isValid) {
        e.preventDefault();
        console.log("❌ Prevented form submission due to invalid input");
    }
});
