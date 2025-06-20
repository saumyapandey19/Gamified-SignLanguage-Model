// DOM Elements
const profileToggle = document.getElementById('profileToggle');
const profileDropdown = document.getElementById('profileDropdown');
const mobileMenuToggle = document.getElementById('mobileMenuToggle');
const mobileMenu = document.getElementById('mobileMenu');
const tabButtons = document.querySelectorAll('.tab-btn');
const navLinks = document.querySelectorAll('.main-nav a, .mobile-menu a');
const categorySections = document.querySelectorAll('.category-section');
const statusParagraph = document.getElementById("status"); // ⬅️ Element to show status feedback

// Function to switch active category
const switchCategory = (category) => {
    tabButtons.forEach(btn => btn.classList.remove('active'));
    navLinks.forEach(link => link.parentElement.classList.remove('active'));
    categorySections.forEach(section => section.classList.remove('active'));

    const targetTab = document.querySelector(`.tab-btn[data-category="${category}"]`);
    if (targetTab) targetTab.classList.add('active');

    const targetNavLinks = document.querySelectorAll(`.main-nav a[href="#${category}"], .mobile-menu a[href="#${category}"]`);
    targetNavLinks.forEach(link => link.parentElement.classList.add('active'));

    const targetSection = document.getElementById(`${category}Section`);
    if (targetSection) {
        targetSection.classList.add('active');
        targetSection.style.opacity = '0';
        setTimeout(() => {
            targetSection.style.opacity = '1';
        }, 100);
    }
};

// Function to start the model using fetch
const startModel = (mode) => {
    fetch(`http://127.0.0.1:5000/start-${mode}`, {
        method: 'POST',
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.text();
    })
    .then(message => {
        if (statusParagraph) statusParagraph.innerText = "✅ " + message;
    })
    .catch(error => {
        console.error("Error:", error);
        if (statusParagraph) statusParagraph.innerText = "❌ Failed to start: " + error.message;
    });
};

// Navigation event listeners
navLinks.forEach(link => {
    const category = link.textContent.toLowerCase();
    link.setAttribute('href', `#${category}`);
    
    link.addEventListener('click', (e) => {
        e.preventDefault();
        switchCategory(category);
        mobileMenu.classList.remove('active');
    });
});

// Tab buttons event listeners
tabButtons.forEach(button => {
    button.addEventListener('click', () => {
        const category = button.getAttribute('data-category');
        switchCategory(category);
    });
});

// Profile dropdown toggle
profileToggle?.addEventListener('click', () => {
    profileDropdown?.classList.toggle('active');
    mobileMenu?.classList.remove('active');
});

// Close profile dropdown when clicking outside
document.addEventListener('click', (e) => {
    if (!profileToggle?.contains(e.target) && !profileDropdown?.contains(e.target)) {
        profileDropdown?.classList.remove('active');
    }
});

// Mobile menu toggle
mobileMenuToggle?.addEventListener('click', () => {
    mobileMenu?.classList.toggle('active');
    profileDropdown?.classList.remove('active');
});

// Sample user data
const userData = {
    name: 'John Doe',
    email: 'john.doe@example.com',
    progress: {
        alphabets: 60,
        numbers: 45,
        phrases: 30
    }
};

// Update user information
const updateUserInfo = () => {
    const userName = document.getElementById('userName');
    const profileName = document.querySelector('.profile-name');
    const profileEmail = document.querySelector('.profile-email');
    
    if (userName) userName.textContent = userData.name;
    if (profileName) profileName.textContent = userData.name;
    if (profileEmail) profileEmail.textContent = userData.email;
};

// Initialize the dashboard
const initDashboard = () => {
    updateUserInfo();
    const hash = window.location.hash.slice(1);
    const initialCategory = hash || 'learn';
    switchCategory(initialCategory);
};

// Listen for hash changes
window.addEventListener('hashchange', () => {
    const category = window.location.hash.slice(1);
    if (category) {
        switchCategory(category);
    }
});

// Handle responsive navigation
const handleResponsiveNav = () => {
    if (window.innerWidth >= 768) {
        mobileMenu.classList.remove('active');
    }
};

document.addEventListener('DOMContentLoaded', initDashboard);
window.addEventListener('resize', handleResponsiveNav);
