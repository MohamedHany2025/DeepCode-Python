// ==================== LANGUAGE SWITCHING ====================
const currentLang = localStorage.getItem('language') || 'ar';
document.documentElement.lang = currentLang;
document.documentElement.dir = currentLang === 'ar' ? 'rtl' : 'ltr';

// Set active language button
document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.classList.remove('active');
    if (btn.getAttribute('data-lang') === currentLang) {
        btn.classList.add('active');
    }
});

// Language switching functionality
document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const lang = this.getAttribute('data-lang');
        switchLanguage(lang);
    });
});

function switchLanguage(lang) {
    localStorage.setItem('language', lang);
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
    
    // Update active button
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-lang') === lang) {
            btn.classList.add('active');
        }
    });

    // Update all text elements with data-en and data-ar attributes
    document.querySelectorAll('[data-en][data-ar]').forEach(element => {
        if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
            const placeholderAttr = lang === 'ar' ? 'data-ar-placeholder' : 'data-en-placeholder';
            if (element.hasAttribute(placeholderAttr)) {
                element.placeholder = element.getAttribute(placeholderAttr);
            }
        } else {
            element.textContent = lang === 'ar' ? element.getAttribute('data-ar') : element.getAttribute('data-en');
        }
    });
}

// Initialize language on page load
window.addEventListener('DOMContentLoaded', function() {
    switchLanguage(currentLang);
});

// ==================== NAVIGATION MENU TOGGLE ==================== 
document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.getElementById('menuToggle');
    const navLinks = document.getElementById('navLinks');

    menuToggle.addEventListener('click', function() {
        menuToggle.classList.toggle('active');
        navLinks.classList.toggle('active');
    });

    // Close menu when a link is clicked
    const navLink = document.querySelectorAll('.nav-link');
    navLink.forEach(link => {
        link.addEventListener('click', function() {
            menuToggle.classList.remove('active');
            navLinks.classList.remove('active');
        });
    });
});

// ==================== SMOOTH SCROLLING FOR NAV LINKS ====================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ==================== PROJECT FILTERING ====================
document.addEventListener('DOMContentLoaded', function() {
    const filterBtns = document.querySelectorAll('.filter-btn');
    const projectCards = document.querySelectorAll('.project-card');

    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove active class from all buttons
            filterBtns.forEach(b => b.classList.remove('active'));
            // Add active class to clicked button
            this.classList.add('active');

            const filterValue = this.getAttribute('data-filter');

            projectCards.forEach(card => {
                const category = card.getAttribute('data-category');
                
                if (filterValue === 'all' || category === filterValue) {
                    card.style.display = 'block';
                    setTimeout(() => {
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, 0);
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });
});

// ==================== CONTACT FORM HANDLING ====================
document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contactForm');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();

            // Get form values
            const name = this.querySelector('input[placeholder="Your Name"]').value;
            const email = this.querySelector('input[placeholder="Your Email"]').value;
            const subject = this.querySelector('input[placeholder="Subject"]').value;
            const message = this.querySelector('textarea[placeholder="Your Message"]').value;

            // Simple validation
            if (name && email && subject && message) {
                // Show success message
                showNotification('Message sent successfully! We\'ll get back to you soon.', 'success');
                
                // Reset form
                this.reset();

                // In a real application, you would send this data to a backend
                console.log({
                    name: name,
                    email: email,
                    subject: subject,
                    message: message
                });
            } else {
                showNotification('Please fill in all fields.', 'error');
            }
        });
    }
});

// ==================== NOTIFICATION FUNCTION ====================
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        padding: 1rem 2rem;
        background: ${type === 'success' ? '#27ae60' : '#e74c3c'};
        color: white;
        border-radius: 5px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        z-index: 2000;
        animation: slideInRight 0.3s ease-out;
        font-weight: bold;
    `;

    document.body.appendChild(notification);

    // Remove notification after 4 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 4000);
}

// ==================== ADD ANIMATIONS ON SCROLL ====================
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe all elements with animation classes
document.querySelectorAll('.project-card, .tutorial-card, .stat-box, .about-text').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'all 0.6s ease-out';
    observer.observe(el);
});

// ==================== NAVBAR SCROLL EFFECT ====================
let lastScrollTop = 0;
const navbar = document.querySelector('.navbar');

window.addEventListener('scroll', function() {
    let scrollTop = window.pageYOffset || document.documentElement.scrollTop;

    // Add shadow effect on scroll
    if (scrollTop > 50) {
        navbar.style.boxShadow = '0 4px 30px rgba(231, 76, 60, 0.3)';
    } else {
        navbar.style.boxShadow = '0 4px 30px rgba(231, 76, 60, 0.2)';
    }

    lastScrollTop = scrollTop;
});

// ==================== PARALLAX EFFECT ====================
window.addEventListener('scroll', function() {
    const scrolled = window.pageYOffset;
    const hero = document.querySelector('.hero');
    
    if (hero) {
        hero.style.backgroundPosition = '0px ' + scrolled * 0.5 + 'px';
    }
});

// ==================== RIPPLE EFFECT ON BUTTONS ====================
document.querySelectorAll('.btn, .filter-btn').forEach(button => {
    button.addEventListener('click', function(e) {
        const ripple = document.createElement('span');
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;

        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.5);
            left: ${x}px;
            top: ${y}px;
            pointer-events: none;
            animation: ripple 0.6s ease-out;
        `;

        this.style.position = 'relative';
        this.style.overflow = 'hidden';
        this.appendChild(ripple);

        setTimeout(() => ripple.remove(), 600);
    });
});

// ==================== ADD RIPPLE ANIMATION ====================
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }

    @keyframes slideInRight {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// ==================== ACTIVE NAVIGATION LINK ====================
window.addEventListener('scroll', function() {
    const sections = document.querySelectorAll('section');
    const navLinks = document.querySelectorAll('.nav-link');

    let current = '';
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        if (pageYOffset >= sectionTop - 200) {
            current = section.getAttribute('id');
        }
    });

    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href').slice(1) === current) {
            link.style.color = '#ff4757';
        } else {
            link.style.color = '';
        }
    });
});

// ==================== SMOOTH PAGE LOAD ====================
window.addEventListener('load', function() {
    document.body.style.opacity = '1';
    document.body.style.transition = 'opacity 0.5s ease-in';
});

// ==================== VIDEO PLACEHOLDER CLICK ====================
const videoPlaceholder = document.querySelector('.video-placeholder');
if (videoPlaceholder) {
    videoPlaceholder.addEventListener('click', function() {
        // You can embed an actual YouTube video here
        window.open('https://www.youtube.com/@DeepCode-Python/videos', '_blank');
    });

    videoPlaceholder.style.cursor = 'pointer';
}

// ==================== KEYBOARD SHORTCUTS ====================
document.addEventListener('keydown', function(e) {
    // Press 'h' to go to home
    if (e.key === 'h' || e.key === 'H') {
        const homeSection = document.getElementById('home');
        if (homeSection) {
            homeSection.scrollIntoView({ behavior: 'smooth' });
        }
    }

    // Press 'c' to go to contact
    if (e.key === 'c' || e.key === 'C') {
        const contactSection = document.getElementById('contact');
        if (contactSection) {
            contactSection.scrollIntoView({ behavior: 'smooth' });
        }
    }

    // Press 'p' to go to projects
    if (e.key === 'p' || e.key === 'P') {
        const projectsSection = document.getElementById('projects');
        if (projectsSection) {
            projectsSection.scrollIntoView({ behavior: 'smooth' });
        }
    }
});

// ==================== TERMINAL-STYLE TEXT EFFECT ====================
const glitchElements = document.querySelectorAll('.glitch');
glitchElements.forEach(element => {
    const text = element.textContent;
    element.setAttribute('data-text', text);
});

// ==================== SCROLL TO TOP BUTTON ====================
const scrollTopBtn = document.createElement('button');
scrollTopBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
scrollTopBtn.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 45px;
    height: 45px;
    border-radius: 50%;
    background: #e74c3c;
    color: white;
    border: none;
    cursor: pointer;
    display: none;
    z-index: 999;
    font-size: 1.2rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
`;

document.body.appendChild(scrollTopBtn);

window.addEventListener('scroll', function() {
    if (window.pageYOffset > 300) {
        scrollTopBtn.style.display = 'flex';
        scrollTopBtn.style.alignItems = 'center';
        scrollTopBtn.style.justifyContent = 'center';
    } else {
        scrollTopBtn.style.display = 'none';
    }
});

scrollTopBtn.addEventListener('click', function() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
});

scrollTopBtn.addEventListener('mouseenter', function() {
    this.style.transform = 'scale(1.1)';
    this.style.boxShadow = '0 4px 25px rgba(231, 76, 60, 0.6)';
});

scrollTopBtn.addEventListener('mouseleave', function() {
    this.style.transform = 'scale(1)';
    this.style.boxShadow = '0 4px 15px rgba(231, 76, 60, 0.3)';
});

// ==================== DARK MODE TOGGLE (OPTIONAL) ====================
const darkModeToggle = () => {
    // Can be added if you want light/dark theme switching
    console.log('Dark mode is the default theme for DeepCode Python');
};

// ==================== CONSOLE EASTER EGG ====================
console.log(`
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║          Welcome to DeepCode Python Website!             ║
║                                                           ║
║     Master Python. Build Extraordinary Things.           ║
║                                                           ║
║          Check out our projects and tutorials            ║
║          Subscribe on YouTube for more content!          ║
║                                                           ║
║                 Happy Coding! 🚀                          ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
`);

console.log('%cDeepCode Python', 'color: #e74c3c; font-size: 20px; font-weight: bold;');
console.log('%cAdvanced Python Programming Tutorials & Projects', 'color: #ff4757; font-size: 14px;');
console.log('%cYouTube: https://www.youtube.com/@DeepCode-Python', 'color: #3498db; font-size: 14px;');
