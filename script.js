// API endpoints
const API_URL = ''; // Use relative paths for API calls
const ENDPOINTS = {
    PROCESS_REQUIREMENT: `${API_URL}/api/process-requirement`,
    GENERATE_CODE: `${API_URL}/api/generate-code`,
    PUSH_GITHUB: `${API_URL}/api/push-to-github`,
    UPDATE_GITHUB_TOKEN: `${API_URL}/api/update-github-token`
};

// DOM Elements
const initialLoading = document.querySelector('.initial-loading');
const warpStars = document.getElementById('warpStars');
const requirementInput = document.querySelector('.requirement-input');
const submitBtn = document.querySelector('.submit-btn');
const outputSection = document.querySelector('.output-section');
const developmentGoals = document.querySelector('.development-goals');
const loadingIndicator = document.getElementById('loadingIndicator');
const downloadMdBtn = document.querySelector('.download-md');
const generateCodeBtn = document.querySelector('.generate-code');
const pushGithubBtn = document.querySelector('.push-github');
const historyList = document.querySelector('.history-list');
const sidebarToggle = document.getElementById('sidebarToggle');
const sidebar = document.querySelector('.sidebar');
const clearHistory = document.getElementById('clearHistory');
const settingsBtn = document.querySelector('.settings-btn');
const aboutBtn = document.querySelector('.about-btn');
const settingsModal = document.getElementById('settingsModal');
const aboutModal = document.getElementById('aboutModal');
const closeModalBtns = document.querySelectorAll('.close-modal');
const githubBtn = document.querySelector('.github-btn');
const saveSettingsBtn = document.getElementById('saveSettings');
const githubTokenInput = document.getElementById('githubTokenInput');

// State management
let currentTasks = [];
let currentLanguage = 'generic'; // Add variable to store detected language
let sidebarCollapsed = false;
let githubToken = localStorage.getItem('githubToken') || '';

// Initialize GitHub token from storage
if (githubToken) {
    githubTokenInput.value = githubToken;
}

// Initial loading animation
function createWarpStars() {
    for (let i = 0; i < 100; i++) {
        const star = document.createElement('div');
        star.classList.add('warp-star');
        star.style.left = `${Math.random() * 100}%`;
        star.style.top = `${Math.random() * 100}%`;
        star.style.animationDuration = `${1 + Math.random() * 2}s`;
        star.style.animationDelay = `${Math.random() * 2}s`;
        warpStars.appendChild(star);
    }
}

function hideInitialLoading() {
    initialLoading.style.opacity = '0';
    setTimeout(() => {
        initialLoading.style.display = 'none';
    }, 500);
}

// Initialize loading animation
createWarpStars();
setTimeout(hideInitialLoading, 3000);

// Sidebar toggle
sidebarToggle.addEventListener('click', () => {
    sidebarCollapsed = !sidebarCollapsed;
    sidebar.classList.toggle('collapsed', sidebarCollapsed);
    sidebarToggle.innerHTML = sidebarCollapsed ? 
        '<i class="fas fa-chevron-right"></i>' : 
        '<i class="fas fa-chevron-left"></i>';
});

// Modal functionality
function openModal(modal) {
    modal.style.display = 'flex';
}

function closeModal(modal) {
    modal.style.display = 'none';
}

settingsBtn.addEventListener('click', () => openModal(settingsModal));
aboutBtn.addEventListener('click', () => openModal(aboutModal));

closeModalBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const modal = btn.closest('.modal');
        closeModal(modal);
    });
});

window.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        closeModal(e.target);
    }
});

// Settings handling
saveSettingsBtn.addEventListener('click', async () => {
    const newToken = githubTokenInput.value.trim();
    
    try {
        const response = await fetch(ENDPOINTS.UPDATE_GITHUB_TOKEN, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ token: newToken })
        });

        const data = await response.json();
        if (data.success) {
            localStorage.setItem('githubToken', newToken);
            alert('Settings saved successfully!');
            closeModal(settingsModal);
        } else {
            throw new Error(data.error || 'Failed to save settings');
        }
    } catch (error) {
        alert('Error saving settings: ' + error.message);
    }
});

// Clear history
clearHistory.addEventListener('click', () => {
    historyList.innerHTML = '';
});
// Removed redundant submitBtn listener that called Gemini directly from frontend.
// The listener below correctly calls the backend API.

// GitHub button handling
githubBtn.addEventListener('click', async () => {
    const githubToken = localStorage.getItem('githubToken');
    if (!githubToken) {
        alert('Please set your GitHub Access Token in Settings first');
        openModal(settingsModal);
        return;
    }

    try {
        // Verify token is still valid
        const response = await fetch(ENDPOINTS.UPDATE_GITHUB_TOKEN, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ token: githubToken })
        });

        const data = await response.json();
        if (data.success) {
            // Token is valid, redirect to GitHub repositories
            window.open('https://github.com?tab=repositories', '_blank');
        } else {
            // Token is invalid
            alert('Your GitHub token appears to be invalid. Please update it in Settings.');
            openModal(settingsModal);
        }
    } catch (error) {
        alert('Error connecting to GitHub. Please check your token in Settings.');
        openModal(settingsModal);
    }
});

// Event Listeners
submitBtn.addEventListener('click', async () => {
    const requirement = requirementInput.value.trim();
    if (!requirement) return;

    try {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Processing...';
        
        // Show output section with loading indicator
        outputSection.classList.remove('hidden');
        loadingIndicator.style.display = 'flex';
        developmentGoals.innerHTML = '';
        
        const response = await fetch(ENDPOINTS.PROCESS_REQUIREMENT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ requirement })
        });

        const data = await response.json();
        if (!data.success) throw new Error(data.error || 'Failed to process requirement');

        if (!data.tasks || !Array.isArray(data.tasks)) {
            throw new Error('Invalid response format: tasks array is missing');
        }

        currentTasks = data.tasks;
        currentLanguage = data.techStack?.language || 'generic'; // Store the language

        // Hide loading indicator and display analysis
        loadingIndicator.style.display = 'none';
        displayAnalysis(data);
        saveToHistory(requirement, currentTasks);
    } catch (error) {
        console.error('Error processing requirement:', error);
        alert('Error processing requirement: ' + error.message);
        loadingIndicator.style.display = 'none';
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Generate Plan';
    }
});

downloadMdBtn.addEventListener('click', () => {
    const content = currentTasks.join('\n');
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'development-goals.md';
    a.click();
    URL.revokeObjectURL(url);
});

generateCodeBtn.addEventListener('click', async () => {
    if (!currentTasks.length) return;

    try {
        generateCodeBtn.disabled = true;
        generateCodeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...'; // Use innerHTML for icon

        const response = await fetch(ENDPOINTS.GENERATE_CODE, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            // Send tasks and the stored language as project_type
            body: JSON.stringify({ tasks: currentTasks, project_type: currentLanguage })
        });

        if (response.ok && response.headers.get('Content-Type')?.includes('application/zip')) {
            // Success: Handle the ZIP file download
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'generated_project.zip'; // Fixed filename
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
            pushGithubBtn.classList.remove('hidden'); // Show GitHub button on success
        } else {
            // Error: Try to parse JSON error message from backend
            let errorMsg = 'Failed to generate project files. Unknown error.';
            try {
                const errorData = await response.json();
                if (errorData && errorData.error) {
                    errorMsg = errorData.error;
                } else {
                     errorMsg = `Server responded with status ${response.status}: ${response.statusText}`;
                }
            } catch (jsonError) {
                 errorMsg = `Server responded with status ${response.status}. Failed to parse error message.`;
                 console.error("Failed to parse error JSON:", jsonError);
                 console.error("Response status:", response.status);
                 console.error("Response status text:", response.statusText);
            }
            throw new Error(errorMsg); // Throw the extracted or generated error message
        }

    } catch (error) {
        // Use the specific alert message format
        alert('Error generating code: ' + error.message);
        console.error('Error in generateCodeBtn:', error);
    } finally {
        generateCodeBtn.disabled = false;
        generateCodeBtn.innerHTML = '<i class="fas fa-code"></i> Generate Codebase'; // Restore button
    }
});

pushGithubBtn.addEventListener('click', async () => {
    const repoName = prompt('Enter repository name:');
    if (!repoName) return;

    try {
        pushGithubBtn.disabled = true;
        pushGithubBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Pushing...';

        const response = await fetch(ENDPOINTS.PUSH_GITHUB, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                repoName,
                tasks: currentTasks
            })
        });

        const data = await response.json();
        if (!data.success) throw new Error(data.error);

        // Create a custom success modal instead of alert
        const successModal = document.createElement('div');
        successModal.className = 'modal';
        successModal.style.display = 'flex';
        successModal.innerHTML = `
            <div class="modal-content">
                <button class="close-modal">&times;</button>
                <h2><i class="fas fa-check-circle" style="color: #4CAF50;"></i> Success!</h2>
                <p>Your code has been successfully pushed to GitHub!</p>
                <p>Repository URL: <a href="${data.repoUrl}" target="_blank" style="color: #4facfe;">${data.repoUrl}</a></p>
            </div>
        `;
        document.body.appendChild(successModal);
        
        // Add event listeners to close the modal
        const closeBtn = successModal.querySelector('.close-modal');
        closeBtn.addEventListener('click', () => {
            document.body.removeChild(successModal);
        });
        
        successModal.addEventListener('click', (e) => {
            if (e.target === successModal) {
                document.body.removeChild(successModal);
            }
        });
    } catch (error) {
        alert('Error pushing to GitHub: ' + error.message);
    } finally {
        pushGithubBtn.disabled = false;
        pushGithubBtn.innerHTML = '<i class="fab fa-github"></i> Push to GitHub';
    }
});

// Helper Functions
function displayTasks(tasks) {
    developmentGoals.innerHTML = '';
    
    // Add tasks with staggered animation
    tasks.forEach((task, index) => {
        const taskElement = document.createElement('div');
        taskElement.className = 'task';
        taskElement.textContent = `${index + 1}. ${task}`;
        taskElement.style.animationDelay = `${0.1 * index}s`;
        developmentGoals.appendChild(taskElement);
    });
    
    outputSection.classList.remove('hidden');
}

function saveToHistory(requirement, tasks) {
    const historyItem = document.createElement('div');
    historyItem.className = 'history-item';
    historyItem.textContent = requirement.substring(0, 50) + '...';
    historyItem.addEventListener('click', () => {
        requirementInput.value = requirement;
        currentTasks = tasks;
        displayTasks(tasks);
    });
    historyList.insertBefore(historyItem, historyList.firstChild);
}

// Removed downloadFiles function as it's handled directly in the event listener now.

function displayAnalysis(data) {
    developmentGoals.innerHTML = '';
    
    // Display tech stack
    if (data.techStack) {
        const techStackSection = document.createElement('div');
        techStackSection.className = 'analysis-section';
        techStackSection.innerHTML = `
            <h3>Tech Stack</h3>
            <div class="tech-info">
                <p><strong>Language:</strong> ${data.techStack.language}</p>
                <p><strong>Frameworks:</strong> ${data.techStack.frameworks.join(', ') || 'None'}</p>
            </div>
        `;
        developmentGoals.appendChild(techStackSection);
    }
    
    // Display project structure
    if (data.projectStructure) {
        const structureSection = document.createElement('div');
        structureSection.className = 'analysis-section';
        structureSection.innerHTML = `
            <h3>Project Structure</h3>
            <pre class="project-tree">${data.projectStructure}</pre>
        `;
        developmentGoals.appendChild(structureSection);
    }
    
    // Display tasks with staggered animation
    const tasksSection = document.createElement('div');
    tasksSection.className = 'analysis-section';
    tasksSection.innerHTML = '<h3>Development Tasks</h3>';
    
    data.tasks.forEach((task, index) => {
        const taskElement = document.createElement('div');
        taskElement.className = 'task';
        taskElement.textContent = task;
        taskElement.style.animationDelay = `${0.1 * index}s`;
        tasksSection.appendChild(taskElement);
    });
    
    developmentGoals.appendChild(tasksSection);
    outputSection.classList.remove('hidden');
}
