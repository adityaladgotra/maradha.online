/**
 * Maradha Institute - Admin Dashboard JavaScript
 * Version: 1.0
 */

document.addEventListener('DOMContentLoaded', function() {
    // Handle sidebar navigation
    const sidebarLinks = document.querySelectorAll('#admin-sidebar a');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    // Function to show a specific tab
    function showTab(tabId) {
        // Hide all tabs
        tabPanes.forEach(pane => {
            pane.classList.remove('show', 'active');
        });
        
        // Remove active class from all sidebar links
        sidebarLinks.forEach(link => {
            link.classList.remove('active');
        });
        
        // Show the selected tab
        const selectedTab = document.getElementById(tabId);
        if (selectedTab) {
            selectedTab.classList.add('show', 'active');
            
            // Make the corresponding sidebar link active
            const correspondingLink = document.querySelector(`#admin-sidebar a[data-target="${tabId}"]`);
            if (correspondingLink) {
                correspondingLink.classList.add('active');
            }
        }
    }
    
    // Add click event listeners to sidebar links
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (this.getAttribute('href') === '#') {
                e.preventDefault();
                const tabId = this.getAttribute('data-target');
                showTab(tabId);
                
                // Update URL with a hash for better navigation
                history.pushState(null, null, `#${tabId}`);
            }
        });
    });
    
    // Also handle the "Add Course" button in the courses tab
    const addCourseBtn = document.getElementById('add-course-btn');
    if (addCourseBtn) {
        addCourseBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const tabId = this.getAttribute('data-target');
            showTab(tabId);
        });
    }
    
    // Check if there's a hash in the URL on page load
    if (window.location.hash) {
        const tabId = window.location.hash.substring(1); // Remove the # symbol
        showTab(tabId);
    }
    
    // Filter enrollments by course
    const courseFilter = document.getElementById('courseFilter');
    if (courseFilter) {
        courseFilter.addEventListener('change', function() {
            const courseId = this.value;
            filterEnrollmentsByCourse(courseId);
        });
    }
    
    // Function to filter enrollments by course
    function filterEnrollmentsByCourse(courseId) {
        const enrollmentRows = document.querySelectorAll('#enrollmentsTable tbody tr');
        
        if (courseId === '0') {
            // Show all enrollments
            enrollmentRows.forEach(row => {
                row.style.display = '';
            });
        } else {
            // Show only enrollments for the selected course
            enrollmentRows.forEach(row => {
                const rowCourseId = row.getAttribute('data-course-id');
                if (rowCourseId === courseId) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        }
        
        // Check if there are no visible rows
        let visibleRows = 0;
        enrollmentRows.forEach(row => {
            if (row.style.display !== 'none') {
                visibleRows++;
            }
        });
        
        // If no visible rows, show empty state message
        const tableBody = document.querySelector('#enrollmentsTable tbody');
        const existingEmptyMessage = document.querySelector('#enrollmentsTable .empty-filtered-message');
        
        if (visibleRows === 0 && !existingEmptyMessage) {
            const emptyRow = document.createElement('tr');
            emptyRow.className = 'empty-filtered-message';
            emptyRow.innerHTML = `
                <td colspan="6" class="text-center py-4">
                    <div class="empty-state">
                        <i class="fas fa-filter empty-icon mb-3"></i>
                        <h5>No enrollments found</h5>
                        <p class="text-muted">There are no student enrollments for the selected course.</p>
                    </div>
                </td>
            `;
            tableBody.appendChild(emptyRow);
        } else if (visibleRows > 0 && existingEmptyMessage) {
            existingEmptyMessage.remove();
        }
    }
    
    // Search functionality for enrollments
    const enrollmentSearch = document.getElementById('enrollmentSearch');
    if (enrollmentSearch) {
        enrollmentSearch.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            searchEnrollments(searchTerm);
        });
    }
    
    // Function to search enrollments
    function searchEnrollments(searchTerm) {
        const enrollmentRows = document.querySelectorAll('#enrollmentsTable tbody tr:not(.empty-filtered-message)');
        
        enrollmentRows.forEach(row => {
            const rowText = row.textContent.toLowerCase();
            const isVisible = row.style.display !== 'none'; // Check if it's already hidden by the course filter
            
            if (isVisible) {
                if (searchTerm === '' || rowText.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            }
        });
        
        // Check if there are no visible rows
        let visibleRows = 0;
        enrollmentRows.forEach(row => {
            if (row.style.display !== 'none') {
                visibleRows++;
            }
        });
        
        // If no visible rows, show empty state message
        const tableBody = document.querySelector('#enrollmentsTable tbody');
        const existingEmptyMessage = document.querySelector('#enrollmentsTable .empty-search-message');
        
        if (visibleRows === 0 && !existingEmptyMessage) {
            const emptyRow = document.createElement('tr');
            emptyRow.className = 'empty-search-message';
            emptyRow.innerHTML = `
                <td colspan="6" class="text-center py-4">
                    <div class="empty-state">
                        <i class="fas fa-search empty-icon mb-3"></i>
                        <h5>No results found</h5>
                        <p class="text-muted">No students match your search criteria.</p>
                    </div>
                </td>
            `;
            tableBody.appendChild(emptyRow);
        } else if (visibleRows > 0 && existingEmptyMessage) {
            existingEmptyMessage.remove();
        }
    }
    
    // Dynamic date validation for course start/end dates
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    
    if (startDateInput && endDateInput) {
        startDateInput.addEventListener('change', function() {
            // Set the min attribute of end date to be at least the start date
            endDateInput.min = this.value;
            
            // If end date is before start date, reset it
            if (endDateInput.value && endDateInput.value < this.value) {
                endDateInput.value = this.value;
            }
        });
        
        // Set initial min value for end date
        if (startDateInput.value) {
            endDateInput.min = startDateInput.value;
        }
    }
    
    // Dynamic price calculation and validation
    const regularPriceInput = document.getElementById('price');
    const offerPriceInput = document.getElementById('offer_price');
    
    if (regularPriceInput && offerPriceInput) {
        // Ensure offer price doesn't exceed regular price
        offerPriceInput.addEventListener('input', function() {
            const regularPrice = parseFloat(regularPriceInput.value) || 0;
            const offerPrice = parseFloat(this.value) || 0;
            
            if (offerPrice > regularPrice) {
                this.setCustomValidity('Offer price cannot be higher than regular price');
            } else {
                this.setCustomValidity('');
            }
            
            // Calculate and display discount percentage if both prices are valid
            if (regularPrice > 0 && offerPrice > 0 && offerPrice <= regularPrice) {
                const discountPercentage = ((regularPrice - offerPrice) / regularPrice * 100).toFixed(0);
                
                // Update discount display if it exists
                const discountDisplay = document.getElementById('discount-display');
                if (discountDisplay) {
                    discountDisplay.textContent = `${discountPercentage}% OFF`;
                }
            }
        });
        
        regularPriceInput.addEventListener('input', function() {
            // Trigger the offer price validation when regular price changes
            if (offerPriceInput.value) {
                const event = new Event('input');
                offerPriceInput.dispatchEvent(event);
            }
        });
    }
    
    // Display form validation errors
    const formInputs = document.querySelectorAll('form input, form textarea, form select');
    formInputs.forEach(input => {
        input.addEventListener('input', function() {
            // Clear validation message when user types
            this.classList.remove('is-invalid');
            
            // For custom validation messages
            this.setCustomValidity('');
        });
    });
    
    // View enrollment details
    const viewEnrollmentButtons = document.querySelectorAll('.view-enrollment');
    viewEnrollmentButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Modal will be handled by Bootstrap, no additional JS needed for basic functionality
        });
    });
    
    // View course enrollments (filter)
    const viewEnrollmentsButtons = document.querySelectorAll('.view-enrollments');
    viewEnrollmentsButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get the course ID
            const courseId = this.getAttribute('data-course-id');
            
            // Navigate to enrollments tab
            showTab('enrollments-tab');
            
            // Set the course filter dropdown
            if (courseFilter) {
                courseFilter.value = courseId;
                
                // Trigger the change event to apply the filter
                const event = new Event('change');
                courseFilter.dispatchEvent(event);
            }
        });
    });
    
    // Benefits input helper: convert comma-separated to line breaks
    const benefitsInput = document.getElementById('benefits');
    if (benefitsInput) {
        benefitsInput.addEventListener('blur', function() {
            // If user entered comma-separated list, convert to line breaks
            if (this.value.includes(',') && !this.value.includes('\n')) {
                this.value = this.value.split(',').map(item => item.trim()).join('\n');
            }
        });
    }
    
    // Confirm before deleting a course
    const deleteForms = document.querySelectorAll('form[action*="delete_course"]');
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Modal is already handling confirmation, this is just a fallback
            if (!confirm('Are you sure you want to delete this course? This will also delete all enrollments for this course.')) {
                e.preventDefault();
            }
        });
    });
    
    // Initialize any Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});
