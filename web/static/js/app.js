/**
 * Cosmos Generator Web Interface
 * Main JavaScript file
 */

// Add custom date filter for templates
document.addEventListener('alpine:init', () => {
    Alpine.magic('now', () => {
        return (format) => {
            const date = new Date();
            
            if (format === 'Y') {
                return date.getFullYear();
            } else if (format === 'm') {
                return String(date.getMonth() + 1).padStart(2, '0');
            } else if (format === 'd') {
                return String(date.getDate()).padStart(2, '0');
            } else if (format === 'H') {
                return String(date.getHours()).padStart(2, '0');
            } else if (format === 'i') {
                return String(date.getMinutes()).padStart(2, '0');
            } else if (format === 's') {
                return String(date.getSeconds()).padStart(2, '0');
            } else if (format === 'full') {
                return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}:${String(date.getSeconds()).padStart(2, '0')}`;
            }
            
            return date.toString();
        };
    });
});

// Add sci-fi UI effects
document.addEventListener('DOMContentLoaded', () => {
    // Add glow effect to buttons on hover
    const buttons = document.querySelectorAll('.sci-fi-button');
    buttons.forEach(button => {
        button.addEventListener('mouseover', () => {
            button.style.boxShadow = '0 0 15px rgba(0, 212, 255, 0.5)';
        });
        
        button.addEventListener('mouseout', () => {
            button.style.boxShadow = '';
        });
    });
    
    // Add subtle animation to panels
    const panels = document.querySelectorAll('.sci-fi-panel');
    panels.forEach(panel => {
        panel.addEventListener('mouseover', () => {
            panel.style.boxShadow = '0 0 20px rgba(0, 212, 255, 0.3)';
            panel.style.borderColor = 'rgba(0, 212, 255, 0.5)';
        });
        
        panel.addEventListener('mouseout', () => {
            panel.style.boxShadow = '0 0 10px rgba(0, 212, 255, 0.2)';
            panel.style.borderColor = 'rgba(0, 212, 255, 0.3)';
        });
    });
});
