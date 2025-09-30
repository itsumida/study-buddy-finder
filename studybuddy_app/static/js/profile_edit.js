$(document).ready(function() {
    // Initialize Select2 for courses
    $('.select2, #id_courses').select2({
        placeholder: "Select your courses",
        width: '100%',
        allowClear: true,
        tags: false
    });

    // Add form-control class to all form fields
    $('.edit-card input, .edit-card textarea, .edit-card select').addClass('form-control');
    
    // Remove form-control from Select2 elements to avoid conflicts
    $('.select2-hidden-accessible').removeClass('form-control');

    // Form validation and interaction
    $('.form-control').on('focus', function() {
        $(this).closest('.form-group').addClass('focused');
    });

    $('.form-control').on('blur', function() {
        $(this).closest('.form-group').removeClass('focused');
    });

    // Auto-resize textareas
    $('textarea').on('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    // Smooth scroll to first error if any
    if ($('.alert-error').length > 0) {
        $('html, body').animate({
            scrollTop: $('.alert-error').first().offset().top - 100
        }, 500);
    }
});