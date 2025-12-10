// app.js - JavaScript para cargar y mostrar datos de trámites

let allTramites = [];
let currentTramites = [];

// Cargar datos al iniciar la página
document.addEventListener('DOMContentLoaded', async () => {
    try {
        await loadTramites();
        initializeFilters();
        displayTramites(allTramites);
        updateStats();
        setupEventListeners();
    } catch (error) {
        console.error('Error al inicializar la aplicación:', error);
        showError('Error al cargar los datos. Por favor, recarga la página.');
    }
});

// Cargar datos desde el archivo JSON
async function loadTramites() {
    try {
        const response = await fetch('tramites.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        allTramites = data.tramites || [];
        currentTramites = [...allTramites];
        console.log(`Cargados ${allTramites.length} trámites`);
    } catch (error) {
        console.error('Error al cargar trámites:', error);
        throw error;
    }
}

// Inicializar los filtros
function initializeFilters() {
    const categoryFilter = document.getElementById('categoryFilter');
    const categories = [...new Set(allTramites.map(t => t.categoria))];
    
    categories.forEach(category => {
        const option = document.createElement('option');
        option.value = category;
        option.textContent = category;
        categoryFilter.appendChild(option);
    });
}

// Mostrar trámites en la página
function displayTramites(tramites) {
    const container = document.getElementById('tramitesList');
    
    if (tramites.length === 0) {
        container.innerHTML = '<p class="no-results">No se encontraron trámites.</p>';
        return;
    }
    
    container.innerHTML = tramites.map(tramite => `
        <div class="tramite-card" data-id="${tramite.id}">
            <h3>${tramite.nombre}</h3>
            <span class="categoria-badge">${tramite.categoria}</span>
            <p class="descripcion">${tramite.descripcion}</p>
            <div class="tramite-details">
                <p><strong>Requisitos:</strong></p>
                <ul>
                    ${tramite.requisitos.map(req => `<li>${req}</li>`).join('')}
                </ul>
                <p><strong>Costo:</strong> ${tramite.costo}</p>
                <p><strong>Duración:</strong> ${tramite.duracion}</p>
                <p><strong>Lugar:</strong> ${tramite.lugar}</p>
            </div>
        </div>
    `).join('');
}

// Actualizar estadísticas
function updateStats() {
    const totalTramites = document.getElementById('totalTramites');
    const totalCategorias = document.getElementById('totalCategorias');
    
    totalTramites.textContent = currentTramites.length;
    const categories = new Set(currentTramites.map(t => t.categoria));
    totalCategorias.textContent = categories.size;
}

// Configurar eventos
function setupEventListeners() {
    const searchInput = document.getElementById('searchInput');
    const searchButton = document.getElementById('searchButton');
    const categoryFilter = document.getElementById('categoryFilter');
    
    // Búsqueda por texto
    searchButton.addEventListener('click', performSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
    
    // Filtro por categoría
    categoryFilter.addEventListener('change', applyFilters);
}

// Realizar búsqueda
function performSearch() {
    applyFilters();
}

// Aplicar filtros
function applyFilters() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const selectedCategory = document.getElementById('categoryFilter').value;
    
    currentTramites = allTramites.filter(tramite => {
        const matchesSearch = searchTerm === '' || 
            tramite.nombre.toLowerCase().includes(searchTerm) ||
            tramite.descripcion.toLowerCase().includes(searchTerm) ||
            tramite.requisitos.some(req => req.toLowerCase().includes(searchTerm));
        
        const matchesCategory = selectedCategory === '' || tramite.categoria === selectedCategory;
        
        return matchesSearch && matchesCategory;
    });
    
    displayTramites(currentTramites);
    updateStats();
}

// Mostrar error
function showError(message) {
    const container = document.getElementById('tramitesList');
    container.innerHTML = `<p class="error">${message}</p>`;
}
