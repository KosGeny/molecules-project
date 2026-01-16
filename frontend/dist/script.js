const API_BASE_URL = 'http://localhost:8000/api/v1';

let currentPage = 1;
const pageSize = 2;
let molecules = [];
let searchResults = [];
let currentSearchQuery = '';
let currentSearchLimit = 2;

const homeSection = document.getElementById('home-section');
const searchSection = document.getElementById('search-section');
const uploadSection = document.getElementById('upload-section');
const moleculesList = document.getElementById('molecules-list');
const formMessage = document.getElementById('form-message');
const paginationControls = document.getElementById('pagination-controls');
const searchPaginationControls = document.getElementById('search-pagination-controls');
const totalCount = document.getElementById('total-count');
const searchTotalCount = document.getElementById('search-total-count');
const uploadResult = document.getElementById('upload-result');

let editModal = null;

function showSection(section) {
    homeSection.style.display = section === 'home' ? 'block' : 'none';
    searchSection.style.display = section === 'search' ? 'block' : 'none';
    
    // Update active nav buttons
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    if (event && event.target) {
        event.target.classList.add('active');
    } else {
        document.querySelector('.nav-link[href="#"]').classList.add('active');
    }
    
    // Load data if switching to sections
    if (section === 'home') {
        loadMolecules(currentPage);
    } else if (section === 'search') {
        if (currentSearchQuery) {
            loadSearchResults(currentSearchQuery, currentSearchLimit, 1);
        }
    }
}

// API Functions
async function apiCall(url, options = {}) {
    const response = await fetch(API_BASE_URL + url, {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
        ...options
    });
    
    if (!response.ok) {
        let error;
        try {
            error = await response.json();
        } catch (jsonError) {
            const errorText = await response.text();
            error = { detail: errorText };
        }
        
        console.error('API error details:', error);
        throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
    }
    
    return response.json();
}

// Molecule API functions
async function getMolecules(skip = 0, limit = 10) {
    return await apiCall(`/molecules?skip=${skip}&limit=${limit}`);
}

async function createMolecule(moleculeData) {
    return await apiCall('/molecules', {
        method: 'POST',
        body: JSON.stringify(moleculeData)
    });
}

async function updateMolecule(id, moleculeData) {
    return await apiCall(`/molecules/${id}`, {
        method: 'PUT',
        body: JSON.stringify(moleculeData)
    });
}

async function deleteMolecule(id) {
    return await apiCall(`/molecules/${id}`, {
        method: 'DELETE'
    });
}

async function searchMolecules(query, limit = 2, offset = 0) {
    return await apiCall('/molecules/search', {
        method: 'POST',
        body: JSON.stringify({ 
            query: query,
            limit: limit,
            offset: offset
        })
    });
}

async function uploadMolecules(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(API_BASE_URL + '/molecules/upload', {
        method: 'POST',
        body: formData
    });
    
    if (!response.ok) {
        let error;
        try {
            error = await response.json();
        } catch (jsonError) {
            const errorText = await response.text();
            error = { detail: errorText };
        }
        
        console.error('API error details:', error);
        throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
    }
    
    return response.json();
}

// Display functions
function showMessage(message, type = 'success') {
    formMessage.textContent = message;
    formMessage.className = `alert alert-${type === 'error' ? 'danger' : 'success'} d-block`;
    
    setTimeout(() => {
        formMessage.classList.add('d-none');
    }, 5000);
}

function displayMolecules(moleculesData, total, currentPage, pageSize) {
    moleculesList.innerHTML = '';
    
    if (moleculesData.length === 0) {
        moleculesList.innerHTML = '<div class="col-12"><p class="text-center">No molecules found</p></div>';
        return;
    }
    
    moleculesData.forEach(molecule => {
        const col = document.createElement('div');
        col.className = 'col-md-6 col-lg-4 mb-3';
        col.innerHTML = `
            <div class="card h-100 molecule-card">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h5 class="card-title molecule-name">${molecule.name || 'Unnamed Molecule'}</h5>
                        <div class="btn-group">
                            <button class="btn btn-outline-primary btn-sm edit-btn" onclick="openEditModal(${molecule.id}, '${molecule.name || ''}', '${molecule.smiles}')">
                                <i class="fas fa-edit"></i> Edit
                            </button>
                            <button class="btn btn-outline-danger btn-sm delete-btn" onclick="deleteMoleculeHandler(${molecule.id})">
                                <i class="fas fa-trash"></i> Delete
                            </button>
                        </div>
                    </div>
                    <div class="molecule-details">
                        <strong>SMILES:</strong> ${molecule.smiles}
                    </div>
                </div>
            </div>
        `;
        moleculesList.appendChild(col);
    });
}

function displaySearchResults(response, currentPage, pageSize) {
    const searchResultsDiv = document.getElementById('search-results');
    searchResultsDiv.innerHTML = '';
    
    if (response.items.length === 0) {
        searchResultsDiv.innerHTML = '<p class="text-center">No search results found</p>';
        return;
    }
    
    const resultsRow = document.createElement('div');
    resultsRow.className = 'row';
    
    response.items.forEach(molecule => {
        const col = document.createElement('div');
        col.className = 'col-md-6 col-lg-4 mb-3';
        col.innerHTML = `
            <div class="card h-100 molecule-card">
                <div class="card-body">
                    <h5 class="card-title molecule-name">${molecule.name || 'Unnamed Molecule'}</h5>
                    <div class="molecule-details">
                        <strong>SMILES:</strong> ${molecule.smiles}
                    </div>
                </div>
            </div>
        `;
        resultsRow.appendChild(col);
    });
    
    searchResultsDiv.appendChild(resultsRow);
}

function updatePagination(total, currentPage, pageSize, containerId, onPageChange) {
    const totalPages = Math.ceil(total / pageSize);
    const container = document.getElementById(containerId);
    
    if (totalPages <= 1) {
        container.innerHTML = '';
        return;
    }
    
    const startIndex = Math.max(1, currentPage - 2);
    const endIndex = Math.min(totalPages, currentPage + 2);
    
    let paginationHTML = `
        <nav aria-label="Page navigation">
            <ul class="pagination pagination-container">
    `;
    
    // Previous button
    if (currentPage > 1) {
        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="${onPageChange}(${currentPage - 1}); return false;">Previous</a>
            </li>
        `;
    } else {
        paginationHTML += `<li class="page-item disabled"><span class="page-link">Previous</span></li>`;
    }
    
    // First page
    if (startIndex > 1) {
        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="${onPageChange}(1); return false;">1</a>
            </li>
            ${startIndex > 2 ? '<li class="page-item disabled"><span class="page-link">...</span></li>' : ''}
        `;
    }
    
    // Page numbers
    for (let i = startIndex; i <= endIndex; i++) {
        paginationHTML += `
            <li class="page-item ${i === currentPage ? 'active' : ''}">
                <a class="page-link" href="#" onclick="${onPageChange}(${i}); return false;">${i}</a>
            </li>
        `;
    }
    
    // Last page
    if (endIndex < totalPages) {
        paginationHTML += `
            ${endIndex < totalPages - 1 ? '<li class="page-item disabled"><span class="page-link">...</span></li>' : ''}
            <li class="page-item">
                <a class="page-link" href="#" onclick="${onPageChange}(${totalPages}); return false;">${totalPages}</a>
            </li>
        `;
    }
    
    // Next button
    if (currentPage < totalPages) {
        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="${onPageChange}(${currentPage + 1}); return false;">Next</a>
            </li>
        `;
    } else {
        paginationHTML += `<li class="page-item disabled"><span class="page-link">Next</span></li>`;
    }
    
    paginationHTML += '</ul></nav>';
    container.innerHTML = paginationHTML;
}

function openEditModal(id, name, smiles) {
    document.getElementById('edit-id').value = id;
    document.getElementById('edit-name').value = name || '';
    document.getElementById('edit-smiles').value = smiles;
    
    if (!editModal) {
        editModal = new bootstrap.Modal(document.getElementById('editModal'));
    }
    editModal.show();
}

// Event handlers
async function handleMoleculeSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const moleculeData = {
        name: formData.get('name').trim() || undefined,
        smiles: formData.get('smiles').trim()
    };
    
    try {
        await createMolecule(moleculeData);
        showMessage('Molecule added successfully!');
        event.target.reset();
        loadMolecules(1);
    } catch (error) {
        showMessage(error.message, 'error');
    }
}

async function handleEditSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const id = parseInt(formData.get('id'));
    const moleculeData = {
        name: formData.get('name').trim() || undefined,
        smiles: formData.get('smiles').trim()
    };
    
    try {
        await updateMolecule(id, moleculeData);
        showMessage('Molecule updated successfully!');
        editModal.hide();
        loadMolecules(currentPage);
    } catch (error) {
        showMessage(error.message, 'error');
    }
}

async function deleteMoleculeHandler(id) {
    if (confirm('Are you sure you want to delete this molecule?')) {
        try {
            await deleteMolecule(id);
            showMessage('Molecule deleted successfully!');
            loadMolecules(currentPage);
        } catch (error) {
            showMessage(error.message, 'error');
        }
    }
}

async function handleSearchSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const query = formData.get('query').trim();
    const limit = parseInt(formData.get('limit')) || 25;
    
    if (!query) {
        showMessage('Please enter a search query', 'error');
        return;
    }
    
    currentSearchQuery = query;
    currentSearchLimit = limit;
    
    try {
        await loadSearchResults(query, limit, 1);
    } catch (error) {
        showMessage(error.message, 'error');
    }
}

async function handleUploadSubmit(event) {
    event.preventDefault();
    
    const fileInput = document.getElementById('upload-file');
    const file = fileInput.files[0];
    
    if (!file) {
        showMessage('Please select a file', 'error');
        return;
    }
    
    if (!file.name.toLowerCase().endsWith('.csv')) {
        showMessage('Only CSV files are allowed', 'error');
        return;
    }
    
    try {
        const result = await uploadMolecules(file);
        uploadResult.innerHTML = `<div class="alert alert-success">${result.message}</div>`;
        uploadResult.style.display = 'block';
        
        setTimeout(() => {
            uploadResult.style.display = 'none';
            fileInput.value = '';
        }, 5000);
        
        loadMolecules(1);
    } catch (error) {
        uploadResult.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
        uploadResult.style.display = 'block';
    }
}

async function loadMolecules(page = 1) {
    currentPage = page;
    const skip = (page - 1) * pageSize;
    
    try {
        const response = await getMolecules(skip, pageSize);
        displayMolecules(response.items, response.total, page, pageSize);
        updatePagination(response.total, page, pageSize, 'pagination-controls', 'loadMolecules');
        
        totalCount.textContent = `${response.total} total`;
        
        searchTotalCount.textContent = '0 found';
    } catch (error) {
        showMessage(error.message, 'error');
    }
}

async function loadSearchResults(query, limit, page = 1) {
    const offset = (page - 1) * limit;
    
    try {
        const response = await searchMolecules(query, limit, offset);
        displaySearchResults(response, page, limit);
        updatePagination(response.total, page, limit, 'search-pagination-controls', 'loadSearchResultsFromButton');
        
        searchTotalCount.textContent = `${response.total} found`;
        
        totalCount.textContent = '0 total';
        
        currentSearchQuery = query;
        currentSearchLimit = limit;
    } catch (error) {
        showMessage(error.message, 'error');
    }
}

// Function called from pagination links for search
function loadSearchResultsFromButton(page) {
    if (currentSearchQuery) {
        loadSearchResults(currentSearchQuery, currentSearchLimit, page);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('.nav-link[href="#"]').classList.add('active');
    
    document.getElementById('molecule-form').addEventListener('submit', handleMoleculeSubmit);
    document.getElementById('edit-form').addEventListener('submit', handleEditSubmit);
    document.getElementById('search-form').addEventListener('submit', handleSearchSubmit);
    
    loadMolecules(1);
});

window.showSection = showSection;
window.openEditModal = openEditModal;
window.deleteMoleculeHandler = deleteMoleculeHandler;
window.loadMolecules = loadMolecules;
window.loadSearchResultsFromButton = loadSearchResultsFromButton;