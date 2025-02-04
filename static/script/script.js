const mobileMenuButton = document.getElementById('mobile-menu-button');
const mobileMenu = document.getElementById('mobile-menu');
const header = document.getElementById('header');
const svgPath = mobileMenuButton.querySelector('svg path');

// Mobile menu toggle with animation
mobileMenuButton.addEventListener('click', () => {
    mobileMenu.classList.toggle('hidden');
    mobileMenu.classList.toggle('show');

    // Toggle between hamburger and close icon for SVG
    if (mobileMenu.classList.contains('show')) {
        svgPath.setAttribute('d', 'M6 18L18 6M6 6l12 12'); // Close Icon
        header.classList.add('header-shadow');  // Add shadow when opened
    } else {
        svgPath.setAttribute('d', 'M4 6h16M4 12h16M4 18h16'); // Hamburger Icon
        if (window.scrollY === 0) header.classList.remove('header-shadow');
    }
});


// Mobile dropdowns toggle
const setupMobileDropdown = (buttonId, dropdownId) => {
    const button = document.getElementById(buttonId);
    const dropdown = document.getElementById(dropdownId);
    
    button.addEventListener('click', () => {
        dropdown.classList.toggle('hidden');
    });
};

setupMobileDropdown('mobile-whoweare-button', 'mobile-whoweare-dropdown');
setupMobileDropdown('mobile-training-button', 'mobile-training-dropdown');
setupMobileDropdown('mobile-news-button', 'mobile-news-dropdown');